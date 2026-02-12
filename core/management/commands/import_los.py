# path to this file: "dml-marketing-middleware/core/management/commands/import_los.py"

import csv
from django.core.management.base import BaseCommand
from core.models import LoanOfficer


class Command(BaseCommand):
    help = 'Import loan officers from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file with LO data')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write(f'Importing loan officers from: {csv_file}')
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        slug = row['slug'].strip().lower()
                        
                        if not slug:
                            self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipping empty slug'))
                            error_count += 1
                            continue
                        
                        lo, created = LoanOfficer.objects.update_or_create(
                            slug=slug,
                            defaults={
                                'first_name': row.get('first_name', '').strip(),
                                'last_name': row.get('last_name', '').strip(),
                                'email': row.get('email', '').strip(),
                                'phone': row.get('phone', '').strip(),
                                'te_owner_id': row.get('te_owner_id', '').strip(),
                                'is_active': row.get('is_active', 'true').lower() in ('true', '1', 'yes'),
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f'✓ Created: {lo.slug}'))
                        else:
                            updated_count += 1
                            self.stdout.write(f'✓ Updated: {lo.slug}')
                    
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f'Row {row_num}: Missing required field: {e}'))
                        error_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Row {row_num}: Error: {e}'))
                        error_count += 1
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('IMPORT COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Created: {created_count}')
        self.stdout.write(f'Updated: {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'Errors: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count + updated_count}'))
