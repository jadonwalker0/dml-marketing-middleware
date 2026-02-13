"""
Management command to import loan officers from a CSV file.

Usage:
    python manage.py import_loan_officers loan_officers.csv

CSV Format:
    slug,first_name,last_name,email,phone,te_owner_id,is_active
    john-smith,John,Smith,john.smith@example.com,555-1234,TE_USER_123,1
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from core.models import LoanOfficer


class Command(BaseCommand):
    help = 'Import loan officers from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing loan officers if slug matches'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options['update']

        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                
                created_count = 0
                updated_count = 0
                skipped_count = 0
                
                for row in reader:
                    slug = row.get('slug', '').strip().lower()
                    
                    if not slug:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping row with empty slug: {row}')
                        )
                        skipped_count += 1
                        continue
                    
                    # Check if loan officer exists
                    existing = LoanOfficer.objects.filter(slug=slug).first()
                    
                    if existing and not update_existing:
                        self.stdout.write(
                            self.style.WARNING(f'Loan officer {slug} already exists (use --update to modify)')
                        )
                        skipped_count += 1
                        continue
                    
                    # Prepare data
                    data = {
                        'slug': slug,
                        'first_name': row.get('first_name', '').strip(),
                        'last_name': row.get('last_name', '').strip(),
                        'email': row.get('email', '').strip(),
                        'phone': row.get('phone', '').strip(),
                        'te_owner_id': row.get('te_owner_id', '').strip(),
                        'is_active': row.get('is_active', '1').strip() in ('1', 'true', 'True', 'yes', 'Yes'),
                    }
                    
                    if existing and update_existing:
                        # Update existing
                        for key, value in data.items():
                            setattr(existing, key, value)
                        existing.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Updated loan officer: {slug}')
                        )
                        updated_count += 1
                    else:
                        # Create new
                        LoanOfficer.objects.create(**data)
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Created loan officer: {slug}')
                        )
                        created_count += 1
                
                # Summary
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('='* 50))
                self.stdout.write(self.style.SUCCESS('Import Summary:'))
                self.stdout.write(self.style.SUCCESS(f'  Created: {created_count}'))
                self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count}'))
                self.stdout.write(self.style.WARNING(f'  Skipped: {skipped_count}'))
                self.stdout.write(self.style.SUCCESS('='* 50))
                
        except FileNotFoundError:
            raise CommandError(f'File not found: {csv_file}')
        except KeyError as e:
            raise CommandError(f'Missing required column in CSV: {e}')
        except Exception as e:
            raise CommandError(f'Error importing loan officers: {e}')
