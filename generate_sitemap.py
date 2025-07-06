import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination

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
        
        # Add all destinations
        count = 0
        for destination in Destination.objects.all():
            # Check all languages with modular_guides or article_content_multilang
            lang_set = set()
            if destination.modular_guides:
                lang_set.update(destination.modular_guides.keys())
            if destination.article_content_multilang:
                lang_set.update(destination.article_content_multilang.keys())
            if not lang_set:
                lang_set = {'en'} if destination.article_content else set()

            for lang in lang_set:
                slug = destination.generate_slug(language=lang)
                if lang == 'en':
                    url = f'https://tcgplex.com/golf-courses/{slug}/'
                else:
                    url = f'https://tcgplex.com/{lang}/golf-courses/{slug}/'
                f.write('    <url>\n')
                f.write(f'        <loc>{url}</loc>\n')
                f.write('        <changefreq>weekly</changefreq>\n')
                f.write('        <priority>0.8</priority>\n')
                f.write('    </url>\n')
                count += 1
            
        # Close the XML file
        f.write('</urlset>')
    
    print(f"Generated sitemap.xml with {count} destination-language entries")

if __name__ == "__main__":
    generate_sitemap()
