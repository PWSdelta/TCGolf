import os
import django
import sys
from urllib.parse import quote_plus

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide

def write_sitemap(filename, urls):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in urls:
            f.write('    <url>\n')
            f.write(f'        <loc>{url}</loc>\n')
            f.write('        <changefreq>weekly</changefreq>\n')
            f.write('        <priority>0.8</priority>\n')
            f.write('    </url>\n')
        f.write('</urlset>\n')
    print(f"Wrote {len(urls)} URLs to {filename}")

def get_english_slug_and_content(dest):
    # Try DestinationGuide first
    guide = DestinationGuide.objects.filter(destination=dest, language_code='en').first()
    if guide and guide.slug and guide.content:
        return guide.slug, guide.content
    # Fallback: article_content_multilang
    if hasattr(dest, 'article_content_multilang') and dest.article_content_multilang:
        content = dest.article_content_multilang.get('en')
        if content:
            slug = dest.generate_slug(language='en') if hasattr(dest, 'generate_slug') else ''
            return slug, content
    # Fallback: article_content
    if hasattr(dest, 'article_content') and dest.article_content:
        slug = dest.generate_slug(language='en') if hasattr(dest, 'generate_slug') else ''
        return slug, dest.article_content
    # No content
    slug = dest.generate_slug(language='en') if hasattr(dest, 'generate_slug') else ''
    return slug, ''

def generate_sitemaps():
    # English Destinations: always output one per Destination, with backward compatibility
    en_urls = []
    for dest in Destination.objects.all():
        slug, content = get_english_slug_and_content(dest)
        if content:
            url = f'https://tcgplex.com/golf-courses/{slug}/'
            en_urls.append(url)
    write_sitemap('sitemap_en.xml', en_urls)

    # Non-English Guides: output all non-English DestinationGuides
    non_en_urls = []
    for guide in DestinationGuide.objects.select_related('destination').exclude(language_code='en'):
        lang = guide.language_code
        slug = guide.slug
        if guide.content:
            url = f'https://tcgplex.com/{lang}/golf-courses/{slug}/'
            non_en_urls.append(url)
    write_sitemap('sitemap_non_en.xml', non_en_urls)

    # Search URLs
    base_url = 'https://tcgplex.com/?q='
    cities = set(Destination.objects.values_list('city', flat=True))
    regions = set(Destination.objects.values_list('region_or_state', flat=True))
    countries = set(Destination.objects.values_list('country', flat=True))
    city_region = set()
    city_country = set()
    for dest in Destination.objects.all():
        if dest.city and dest.region_or_state:
            city_region.add(f"{dest.city} {dest.region_or_state}")
        if dest.city and dest.country:
            city_country.add(f"{dest.city} {dest.country}")
    search_terms = set()
    search_terms.update(cities)
    search_terms.update(regions)
    search_terms.update(countries)
    search_terms.update(city_region)
    search_terms.update(city_country)
    # Remove empty/None
    search_terms = {s.strip() for s in search_terms if s and s.strip()}
    search_urls = [base_url + quote_plus(term) for term in sorted(search_terms, key=lambda x: x.lower())]
    write_sitemap('sitemap_search.xml', search_urls)

    # Sitemap index
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for fname in ['sitemap_en.xml', 'sitemap_non_en.xml', 'sitemap_search.xml']:
            f.write('    <sitemap>\n')
            f.write(f'        <loc>https://tcgplex.com/{fname}</loc>\n')
            f.write('    </sitemap>\n')
        f.write('</sitemapindex>\n')
    print("Wrote sitemap.xml index")

def debug_guide_counts():
    total_dest = Destination.objects.count()
    en_guides = DestinationGuide.objects.filter(language_code='en').count()
    non_en_guides = DestinationGuide.objects.exclude(language_code='en').count()
    print(f"Destinations: {total_dest}")
    print(f"English guides in DestinationGuide: {en_guides}")
    print(f"Non-English guides in DestinationGuide: {non_en_guides}")
    print("\n=== Destination Table Sample ===")
    for dest in Destination.objects.all()[:10]:
        for field in dest._meta.fields:
            print(f"{field.name}: {getattr(dest, field.name)}", end=' | ')
        print()
    print("\n=== DestinationGuide Table Sample ===")
    for guide in DestinationGuide.objects.all()[:10]:
        for field in guide._meta.fields:
            print(f"{field.name}: {getattr(guide, field.name)}", end=' | ')
        print()

if __name__ == "__main__":
    debug_guide_counts()
    generate_sitemaps()
