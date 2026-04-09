import csv
import uuid
from django.core.management.base import BaseCommand, CommandError
from students.models import Student


class Command(BaseCommand):
    help = 'Import students from a CSV exported from Google Sheets'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        created = 0
        skipped = 0

        try:
            with open(csv_path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                students_to_create = []

                for row in reader:
                    usn = row['USN'].strip().upper()
                    if Student.objects.filter(usn=usn).exists():
                        self.stdout.write(f"  Skipping duplicate USN: {usn}")
                        skipped += 1
                        continue

                    food = row['Food'].strip()
                    if food not in ['Veg', 'Non-Veg']:
                        self.stdout.write(self.style.WARNING(
                            f"  Unknown food type '{food}' for {usn} — defaulting to Veg"
                        ))
                        food = 'Veg'

                    students_to_create.append(Student(
                        name=row['Name'].strip(),
                        usn=usn,
                        section=row['Section'].strip(),
                        food_type=food,
                        email=row['Email'].strip().lower(),
                        qr_id=uuid.uuid4(),
                        is_used=False,
                        email_sent=False,
                    ))

                Student.objects.bulk_create(students_to_create)
                created = len(students_to_create)

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {created}, Skipped (duplicates): {skipped}"
        ))