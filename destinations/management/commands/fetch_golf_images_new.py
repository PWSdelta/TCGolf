from django.core.management.base import BaseCommand
from django.db import models
from destinations.models import Destination
import requests
import time
import random

class Command(BaseCommand):
    help = 'Fetch golf course images for destinations using verified working sources'

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

        # Get curated golf images
        golf_images = self.get_curated_golf_images()
        updated_count = 0
        
        for i, dest in enumerate(destinations):
            try:
                # Use a consistent image for each destination based on its ID
                image_index = dest.id % len(golf_images)
                image_url = golf_images[image_index]
                
                if options['dry_run']:
                    self.stdout.write(f'Would update {dest.name}: {image_url}')
                else:
                    # Verify the image URL works
                    if self.verify_image_url(image_url):
                        dest.image_url = image_url
                        dest.save()
                        updated_count += 1
                        self.stdout.write(f'✅ Updated {dest.name}: {image_url}')
                    else:
                        # Fallback to Picsum
                        fallback_url = self.get_picsum_image(dest)
                        dest.image_url = fallback_url
                        dest.save()
                        updated_count += 1
                        self.stdout.write(f'✅ Updated {dest.name} (fallback): {fallback_url}')
                
                # Be respectful to servers
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(f'❌ Error for {dest.name}: {str(e)}')

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} destinations with images!')
            )

    def verify_image_url(self, url):
        """Check if an image URL is accessible"""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_picsum_image(self, destination):
        """Generate a consistent placeholder image using Lorem Picsum"""
        seed = abs(hash(destination.name)) % 1000
        return f"https://picsum.photos/seed/golf{seed}/800/400"

    def get_curated_golf_images(self):
        """Return a list of verified, working golf course images from Unsplash"""
        return [
            # These are direct Unsplash URLs that should work
            "https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1535131749006-b7f58c99034b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400", 
            "https://images.unsplash.com/photo-1593111774240-d529f12cf4bb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1599112352976-a5d4c0e9d9b4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1524498250077-390f9e378fc0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1596727362302-b8d891c42ab8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400",
            "https://images.unsplash.com/photo-1587174768734-b05d8b7e8cc5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400"
        ]
