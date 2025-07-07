import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide
from django.utils.text import slugify
from django.db import transaction

created = 0
skipped = 0
updated = 0

def migrate():
    global created, skipped, updated
    for dest in Destination.objects.all():
        # Migrate English
        en_content = None
        if dest.article_content_multilang and isinstance(dest.article_content_multilang, dict):
            en_content = dest.article_content_multilang.get('en')
        if not en_content and dest.article_content:
            en_content = dest.article_content
        if en_content and en_content.strip():
            guide, was_created = DestinationGuide.objects.get_or_create(
                destination=dest,
                language_code='en',
                defaults={
                    'content': en_content,
                    'title': dest.name,
                    'slug': '',  # Will be auto-generated
                }
            )
            if was_created:
                created += 1
                print(f"[CREATE] English guide for destination id={dest.id} ({dest.name})")
            else:
                # Optionally update content if different
                if guide.content != en_content:
                    guide.content = en_content
                    guide.save()
                    updated += 1
                    print(f"[UPDATE] English guide for destination id={dest.id} ({dest.name})")
                else:
                    skipped += 1
        # Optionally: migrate other languages from article_content_multilang
        if dest.article_content_multilang and isinstance(dest.article_content_multilang, dict):
            for lang, content in dest.article_content_multilang.items():
                if lang == 'en':
                    continue
                if not content or not content.strip():
                    continue
                guide, was_created = DestinationGuide.objects.get_or_create(
                    destination=dest,
                    language_code=lang,
                    defaults={
                        'content': content,
                        'title': dest.name,
                        'slug': '',
                    }
                )
                if was_created:
                    created += 1
                    print(f"[CREATE] {lang} guide for destination id={dest.id} ({dest.name})")
                else:
                    if guide.content != content:
                        guide.content = content
                        guide.save()
                        updated += 1
                        print(f"[UPDATE] {lang} guide for destination id={dest.id} ({dest.name})")
                    else:
                        skipped += 1

if __name__ == "__main__":
    with transaction.atomic():
        migrate()
    print(f"\nDone. Created: {created}, Updated: {updated}, Skipped: {skipped}")
