from django.core.management.base import BaseCommand
from django.conf import settings
import os
from destinations.models import Destination

class Command(BaseCommand):
    help = 'Generates a comprehensive sitemap.xml file'

    def handle(self, *args, **options):
        sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
        
        self.stdout.write(f"Creating sitemap at {sitemap_path}")
        
        with open(sitemap_path, 'w') as f:
            # Start the XML file
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            
            # Add the homepage
            f.write('    <!-- Homepage -->\n')
            f.write('    <url>\n')
            f.write('        <loc>https://tcgplex.com/</loc>\n')
            f.write('        <changefreq>daily</changefreq>\n')
            f.write('        <priority>1.0</priority>\n')
            f.write('    </url>\n\n')
            
            # Get all destinations
            destinations = Destination.objects.all()
            total = destinations.count()
            self.stdout.write(f"Processing {total} destinations")
            
            # Add all destinations
            count = 0
            for destination in destinations:
                slug = destination.generate_slug()
                f.write('    <url>\n')
                f.write(f'        <loc>https://tcgplex.com/golf-courses/{slug}/</loc>\n')
                f.write('        <changefreq>weekly</changefreq>\n')
                f.write('        <priority>0.8</priority>\n')
                f.write('    </url>\n')
                count += 1
                
                if count % 100 == 0:
                    self.stdout.write(f"  Processed {count}/{total} destinations")
                
            # Close the XML file
            f.write('</urlset>')
        
        self.stdout.write(self.style.SUCCESS(f"Generated sitemap.xml with {count} destinations"))
