import csv
from django.core.management.base import BaseCommand
from core.models import LoanOfficer

# Management command to import Loan Officers from a CSV file
class Command(BaseCommand):
    help = "Import Loan Officers from a CSV"

    # collect command line arguments
    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    # process the CSV and import Loan Officers
    def handle(self, *args, **options):
        path = options["csv_path"]
        created, updated = 0, 0
        # open and read the CSV file
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # iterate through each row and create/update LoanOfficer records
            for row in reader:
                slug = (row.get("slug") or "").strip().strip("/").lower()
                if not slug:
                    continue
                
                # create or update the LoanOfficer record
                _, is_created = LoanOfficer.objects.update_or_create(
                    slug=slug,
                    # set the other fields from the CSV row
                    defaults={
                        "first_name": (row.get("first_name") or "").strip(),
                        "last_name": (row.get("last_name") or "").strip(),
                        "email": (row.get("email") or "").strip(),
                        "phone": (row.get("phone") or "").strip(),
                        "te_owner_id": (row.get("te_owner_id") or "").strip(),
                        "is_active": (row.get("is_active") or "true").strip().lower() in ("true","1","yes","y"),
                    },
                )
                # track created vs updated counts
                created += 1 if is_created else 0
                updated += 0 if is_created else 1

        # output the results to the console
        self.stdout.write(self.style.SUCCESS(f"Import complete. Created={created} Updated={updated}"))
