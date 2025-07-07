import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide

def generate_sitemap():
    sitemap_path = 'sitemap.xml'
    with open(sitemap_path, 'w', encoding='utf-8') as f:
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

        count = 0
        # Pass 1: English for all Destinations
        for dest in Destination.objects.all():
            try:
                # Try to get English content from DestinationGuide only
                guide = DestinationGuide.objects.filter(destination=dest, language_code='en').first()
                if guide:
                    slug = guide.slug
                else:
                    # Fallback: generate slug from destination
                    slug = dest.generate_slug(language='en') if hasattr(dest, 'generate_slug') else ''
                url = f'https://tcgplex.com/golf-courses/{slug}/'
                f.write('    <url>\n')
                f.write(f'        <loc>{url}</loc>\n')
                f.write('        <changefreq>weekly</changefreq>\n')
                f.write('        <priority>0.8</priority>\n')
                f.write('    </url>\n')
                count += 1
            except Exception as e:
                print(f"[SKIP] Error with destination id={dest.id}: {e}")
                continue

        # Pass 2: All non-English DestinationGuides
        for guide in DestinationGuide.objects.select_related('destination').exclude(language_code='en'):
            try:
                lang = guide.language_code
                slug = guide.slug
                url = f'https://tcgplex.com/{lang}/golf-courses/{slug}/'
                f.write('    <url>\n')
                f.write(f'        <loc>{url}</loc>\n')
                f.write('        <changefreq>weekly</changefreq>\n')
                f.write('        <priority>0.8</priority>\n')
                f.write('    </url>\n')
                count += 1
            except Exception as e:
                print(f"[SKIP] Error with guide id={guide.id}: {e}")
                continue

        # Close the XML file
        f.write('</urlset>')
    print(f"Generated sitemap.xml with {count} destination-language entries")

if __name__ == "__main__":
    generate_sitemap()
