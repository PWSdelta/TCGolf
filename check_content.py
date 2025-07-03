#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination
import json

# Check a few destinations
destinations = Destination.objects.all()[:10]

print("Content Analysis:")
print("=" * 50)

main_content_count = 0
multilang_content_count = 0

for dest in destinations:
    main_len = len(dest.article_content or "")
    multilang_data = dest.article_content_multilang if dest.article_content_multilang else {}
    multilang_en_len = len(multilang_data.get('en', ''))
    
    if main_len > 0:
        main_content_count += 1
    if multilang_en_len > 0:
        multilang_content_count += 1
    
    print(f"{dest.city:15} | Main: {main_len:5d} | EN: {multilang_en_len:5d} | Total langs: {len(multilang_data)}")

print("=" * 50)
print(f"Total destinations: {destinations.count()}")
print(f"With main content: {main_content_count}")
print(f"With multilang EN: {multilang_content_count}")

# Check if any have multiple languages
multilang_dest = Destination.objects.exclude(article_content_multilang='{}').exclude(article_content_multilang='').first()
if multilang_dest:
    data = multilang_dest.article_content_multilang
    print(f"Sample destination ({multilang_dest.city}) has languages: {list(data.keys())}")
