from django.core.management.base import BaseCommand
from django.db import models
from destinations.models import Destination
import requests
import time
import random

class Command(BaseCommand):
    help = 'Fetch destination city images (skylines, landmarks, landscapes) for golf destinations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of destinations to update (default: 20)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update destinations that already have images',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        # Get destinations without images (or all if --force)
        if options['force']:
            destinations = Destination.objects.all()[:options['limit']]
        else:
            destinations = Destination.objects.filter(
                models.Q(image_url='') | models.Q(image_url__isnull=True)
            )[:options['limit']]

        if not destinations.exists():
            self.stdout.write(self.style.SUCCESS('All destinations already have images!'))
            return

        updated_count = 0
        
        for i, dest in enumerate(destinations):
            try:
                # Try Pexels API first for city images, then fallback to curated images
                image_url = self.get_pexels_city_image(dest) or self.get_curated_city_image(dest)
                
                if options['dry_run']:
                    self.stdout.write(f'Would update {dest.name}: {image_url}')
                else:
                    dest.image_url = image_url
                    dest.save()
                    updated_count += 1
                    self.stdout.write(f'✅ Updated {dest.name}: {image_url}')
                
                # Be respectful to APIs
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(f'❌ Error for {dest.name}: {str(e)}')

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} destinations with images!')
            )

    def get_pexels_city_image(self, destination):
        """
        Get city/destination image from Pexels API
        Sign up for free at: https://www.pexels.com/api/
        """
        # You can get a free API key instantly from Pexels
        PEXELS_API_KEY = "YOUR_PEXELS_API_KEY_HERE"
        
        if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
            return None  # Fall back to curated images
        
        try:
            # Create search terms for the destination city
            search_terms = [
                f"{destination.city} skyline",
                f"{destination.city} downtown", 
                f"{destination.city} cityscape",
                f"{destination.city} landmark",
                f"{destination.city} {destination.region_or_state}",
                f"{destination.region_or_state} landscape",
                f"{destination.city} architecture"
            ]
            
            for term in search_terms:
                url = "https://api.pexels.com/v1/search"
                headers = {"Authorization": PEXELS_API_KEY}
                params = {
                    "query": term,
                    "per_page": 1,
                    "orientation": "landscape"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data['photos']:
                        return data['photos'][0]['src']['large']
                        
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            self.stdout.write(f'Pexels API error: {e}')
        
        return None

    def get_curated_city_image(self, destination):
        """Return a beautiful destination image using Lorem Picsum with city-based seeds"""
        
        # Create a consistent seed based on the city name
        city_seed = abs(hash(destination.city)) % 1000
        
        # Use different categories for variety
        categories = [
            "architecture",
            "city", 
            "urban",
            "building",
            "landscape",
            "nature",
            "travel",
            "scenic"
        ]
        
        # Select category based on destination ID for consistency
        category_index = destination.id % len(categories)
        category = categories[category_index]
        
        # Return a consistent image URL for this destination
        return f"https://picsum.photos/seed/{category}{city_seed}/800/400"
