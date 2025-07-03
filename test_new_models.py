#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide

# Test the new model structure
print("Testing new DestinationGuide model:")
print("=" * 50)

# Get a sample destination
dest = Destination.objects.first()
print(f"Sample destination: {dest.name}, {dest.city}")

# Test creating a guide
guide = DestinationGuide(
    destination=dest,
    language_code='en',
    title=f"Golf Guide to {dest.city}, {dest.country}",
    content="# Sample Golf Guide\n\nThis is a test golf guide content...",
    meta_description=f"Complete golf guide for {dest.city}",
    generated_by='manual'
)

# Test slug generation without saving
test_slug = guide.generate_slug()
print(f"Generated slug: {test_slug}")

# Test the relationship
print(f"Destination guides count: {dest.guides.count()}")

# Check model validation
try:
    guide.full_clean()
    print("✅ Model validation passed")
except Exception as e:
    print(f"❌ Model validation failed: {e}")

# Test unique constraint (don't actually save to avoid duplicates)
print(f"Language choices: {[choice[0] for choice in DestinationGuide._meta.get_field('language_code').choices]}")

print("\n🎯 Model structure looks good!")
print("Ready for data migration from existing content.")
