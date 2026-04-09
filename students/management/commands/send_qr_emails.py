import io
import qrcode
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
                img = qr.make_image(fill_color="black", back_color="white")

                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)

                # Build email
                subject = f"[Fest Lunch] Your food coupon — {student.name}"
                body = (
                    f"Hi {student.name},\n\n"
                    f"Your food coupon for the college fest lunch is attached below.\n\n"
                    f"Details:\n"
                    f"  Name    : {student.name}\n"
                    f"  USN     : {student.usn}\n"
                    f"  Section : {student.section}\n"
                    f"  Food    : {student.food_type}\n"
                    f"  Timing  : 12:00 PM to 1:00 PM\n\n"
                    f"Show this QR code to the volunteer at the food counter.\n"
                    f"Each QR can only be used ONCE.\n\n"
                    f"See you at the fest!\n"
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