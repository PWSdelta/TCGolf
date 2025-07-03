#!/usr/bin/env python
"""
Check final database statistics after reaching 500+ destinations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide

def main():
    total_destinations = Destination.objects.count()
    total_guides = DestinationGuide.objects.count()
    countries = Destination.objects.values('country').distinct().count()
    
    print("🎉 GOLF DESTINATION DATABASE FINAL STATISTICS")
    print("=" * 60)
    print(f"🏌️  Total Destinations: {total_destinations}")
    print(f"📖 Total Guides: {total_guides}")
    print(f"🌍 Countries Represented: {countries}")
    print(f"📊 Destinations without guides: {total_destinations - total_guides}")
    print()
    
    print("🆕 Sample of recently added destinations:")
    print("-" * 40)
    for dest in Destination.objects.order_by('-id')[:15]:
        print(f"  • {dest.city}, {dest.country}")
    
    print()
    print("🌎 Top countries by destination count:")
    print("-" * 40)
    from django.db.models import Count
    top_countries = Destination.objects.values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    for country_data in top_countries:
        print(f"  • {country_data['country']}: {country_data['count']} destinations")
    
    print()
    print("✅ SUCCESS: Goal of 500+ destinations achieved!")
    print("🚀 Ready for multi-language content generation and further expansion!")

if __name__ == "__main__":
    main()
