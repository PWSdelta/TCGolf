from django.core.management.base import BaseCommand
from django.db import models
from destinations.models import Destination

class Command(BaseCommand):
    help = 'Update all US destinations to have "USA" as country'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        # Find destinations that are likely US destinations
        # (those with US state names in region_or_state field and no country set or empty country)
        us_states = [
            # State codes
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC',
            # Full state names
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
            'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
            'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
            'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
            'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
            'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
            'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
            'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
            'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
            'West Virginia', 'Wisconsin', 'Wyoming', 'District of Columbia'
        ]

        # Query for destinations that need updating
        us_destinations = Destination.objects.filter(
            region_or_state__in=us_states
        ).filter(
            models.Q(country='') | 
            models.Q(country__isnull=True) | 
            models.Q(country='United States') |
            models.Q(country='US') |
            models.Q(country='U.S.') |
            models.Q(country='United States of America')
        )

        count = us_destinations.count()
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would update {count} destinations to have country="USA"')
            )
            for dest in us_destinations:
                self.stdout.write(f'  - {dest.name} ({dest.city}, {dest.region_or_state}) - Current country: "{dest.country}"')
        else:
            updated = us_destinations.update(country='USA')
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated} destinations to have country="USA"')
            )
            
        # Also update any destinations that might be missing country but are clearly US
        missing_country = Destination.objects.filter(
            models.Q(country='') | models.Q(country__isnull=True)
        ).exclude(id__in=us_destinations.values_list('id', flat=True))
        
        if missing_country.exists():
            self.stdout.write(
                self.style.WARNING(f'Found {missing_country.count()} destinations with missing country that are not US states:')
            )
            for dest in missing_country[:10]:  # Show first 10
                self.stdout.write(f'  - {dest.name} ({dest.city}, {dest.region_or_state})')
