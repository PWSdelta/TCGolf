#!/usr/bin/env python3
"""
Import international golf destination reviews from ollama_reviews.db to Django database
Excludes Tokyo since it's already been updated with a preferred version
"""

import os
import sys
import sqlite3
import django
from pathlib import Path

# Add Django project to Python path and setup
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

def get_coordinates(city, region, country):
    """Get coordinates for a location using geocoding"""
    geolocator = Nominatim(user_agent="golfplex-importer")
    location_string = f"{city.strip()}, {region.strip()}, {country.strip()}"
    print(f"🌍 Geocoding: {location_string}")
    try:
        time.sleep(1)  # Respect Nominatim rate limit
        location = geolocator.geocode(location_string)
        if location:
            return location.latitude, location.longitude
        # Fallback: try without region
        time.sleep(1)
        fallback_string = f"{city.strip()}, {country.strip()}"
        print(f"🌍 Geocoding fallback: {fallback_string}")
        location = geolocator.geocode(fallback_string)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"⚠️  Geocoding error for {location_string}: {str(e)}")
    return 0.0, 0.0

def import_ollama_reviews():
    """Import reviews from ollama_reviews.db to Django database"""
    
    try:
        # Connect to source database
        conn = sqlite3.connect('ollama_reviews.db')
        cursor = conn.cursor()
        
        # Get all reviews
        cursor.execute("SELECT city, region_or_state, country, article_content FROM reviews")
        reviews = cursor.fetchall()
        
        print(f"📊 Found {len(reviews)} reviews in ollama_reviews.db")
        print("🚀 Starting import process...")
        print("=" * 60)
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        
        for i, (city, region_or_state, country, article_content) in enumerate(reviews, 1):
            city = city.strip()
            region_or_state = region_or_state.strip()
            country = country.strip()
            
            print(f"\n📍 [{i}/{len(reviews)}] Processing: {city}, {region_or_state}, {country}")
            
            try:
                # Check if destination already exists
                existing = Destination.objects.filter(
                    city__iexact=city,
                    region_or_state__iexact=region_or_state,
                    country__iexact=country
                ).first()
                
                if existing:
                    # Update existing destination with English content
                    print(f"📝 Updating existing destination")
                    existing.set_article_content(article_content, 'en')
                    existing.save()
                    updated_count += 1
                    print(f"✅ Updated: {existing.name}")
                else:
                    # Create new destination
                    print(f"🆕 Creating new destination")
                    
                    # Get coordinates
                    lat, lng = get_coordinates(city, region_or_state, country)
                    
                    destination = Destination.objects.create(
                        name=f"{city}, {region_or_state}",
                        city=city,
                        region_or_state=region_or_state,
                        country=country,
                        description=f"Golf destination guide for {city}, {region_or_state}",
                        latitude=lat,
                        longitude=lng
                    )
                    
                    # Set the article content for English
                    destination.set_article_content(article_content, 'en')
                    destination.save()
                    
                    imported_count += 1
                    print(f"✅ Created: {destination.name}")
                
            except Exception as e:
                print(f"❌ Error processing {city}, {country}: {e}")
                error_count += 1
                continue
        
        conn.close()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 IMPORT SUMMARY")
        print("=" * 60)
        print(f"📝 Total reviews processed: {len(reviews)}")
        print(f"🆕 New destinations created: {imported_count}")
        print(f"📝 Existing destinations updated: {updated_count}")
        print(f"❌ Errors: {error_count}")
        print(f"✅ Success rate: {((imported_count + updated_count) / len(reviews) * 100):.1f}%")
        print(f"\n🎉 Import complete! Added {imported_count + updated_count} golf destinations.")
        
    except FileNotFoundError:
        print("❌ ollama_reviews.db not found in current directory")
    except Exception as e:
        print(f"❌ Import error: {e}")

if __name__ == "__main__":
    import_ollama_reviews()
