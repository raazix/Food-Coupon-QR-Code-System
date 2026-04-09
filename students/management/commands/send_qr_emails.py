import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from students.models import Student


class Command(BaseCommand):
    help = 'Generate QR codes and send to all students who have not received email yet'

    def handle(self, *args, **options):
        pending = Student.objects.filter(email_sent=False)
        total = pending.count()
        self.stdout.write(f"Sending to {total} students...")

        success = 0
        failed = 0

        for student in pending:
            try:
                # Generate QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(str(student.qr_id))
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                
                width, height = img.size
                extra_height = 100
                new_img = Image.new('RGB', (width, height + extra_height), color='white')
                new_img.paste(img, (0, 0))
                
                draw = ImageDraw.Draw(new_img)
                try:
                    # Times New Roman (Small)
                    font_title = ImageFont.truetype("times.ttf", 18)
                    font_sub = ImageFont.truetype("times.ttf", 14)
                except IOError:
                    font_title = ImageFont.load_default(size=18)
                    font_sub = ImageFont.load_default(size=14)
                    
                text_name = f"{student.name}"
                text_usn = f"{student.usn}"
                
                bbox_name = draw.textbbox((0, 0), text_name, font=font_title)
                w_name = bbox_name[2] - bbox_name[0]
                draw.text(((width - w_name) // 2, height + 25), text_name, fill="#111111", font=font_title)
                
                bbox_usn = draw.textbbox((0, 0), text_usn, font=font_sub)
                w_usn = bbox_usn[2] - bbox_usn[0]
                # Use a slightly softer gray for the USN to establish depth and professionalism
                draw.text(((width - w_usn) // 2, height + 50), text_usn, fill="#555555", font=font_sub)

                buf = io.BytesIO()
                new_img.save(buf, format='PNG')
                buf.seek(0)

                # Build email
                subject = f"VIGAM’26 – Your food pass"
                body = (
                    f"Hi {student.name},\n\n"
                    f"Your food pass for Vigam'26 is attached below.\n\n"
                    f"Details:\n"
                    f"  Name    : {student.name}\n"
                    f"  USN     : {student.usn}\n"
                    f"  Section : {student.section}\n"
                    f"  Food    : {student.food_type}\n"
                    f"  Timing  : 12:00 PM to 1:00 PM\n\n"
                    f"Show this QR code to the volunteer at the food counter.\n"
                    f"Each QR can only be used ONCE.\n\n"
                    f"See you at Vigam'26!\n"
                )

                mail = EmailMessage(subject=subject, body=body, to=[student.email])
                mail.attach(
                    filename=f"coupon_{student.usn}.png",
                    content=buf.read(),
                    mimetype='image/png'
                )
                mail.send()

                student.email_sent = True
                student.save(update_fields=['email_sent'])
                success += 1
                self.stdout.write(f"  Sent to {student.email}")

            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f"  Failed for {student.usn}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Success: {success}, Failed: {failed}"
        ))
        if failed:
            self.stdout.write("Re-run this command to retry failed ones.")