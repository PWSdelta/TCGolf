import csv
import os
import sqlite3
from django.core.management.base import BaseCommand
from destinations.models import Destination
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

class Command(BaseCommand):
    help = 'Import destinations from ollama_reviews.db SQLite database and geocode lat/long'

    def add_arguments(self, parser):
        parser.add_argument('--sqlite', type=str, default='ollama_reviews.db', help='Path to the SQLite database file')
        parser.add_argument('--retry-failed', action='store_true', help='Retry geocoding for failed destinations (lat/lon = 0.0)')
        parser.add_argument('--clear', action='store_true', help='Delete all destinations before import')

    def get_coordinates(self, city, region, country):
        geolocator = Nominatim(user_agent="golfplex-import")
        location_string = f"{city.strip()}, {region.strip()}, {country.strip()}"
        self.stdout.write(self.style.SUCCESS(f'Geocoding: {location_string}'))
        try:
            time.sleep(1)  # Respect Nominatim rate limit
            location = geolocator.geocode(location_string)
            if location:
                return location.latitude, location.longitude
            # Fallback: try without region
            time.sleep(1)
            fallback_string = f"{city.strip()}, {country.strip()}"
            self.stdout.write(self.style.SUCCESS(f'Geocoding fallback: {fallback_string}'))
            location = geolocator.geocode(fallback_string)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            self.stdout.write(self.style.WARNING(f'Geocoding error for {location_string}: {str(e)}'))
        return 0.0, 0.0

    def handle(self, *args, **options):
        if options.get('clear'):
            count, _ = Destination.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} destinations from the database.'))
            return
        if options.get('retry_failed'):
            self.retry_failed_geocodes()
            return
        db_path = options['sqlite']
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'SQLite DB {db_path} does not exist'))
            return

        # Inspect schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.stdout.write(self.style.NOTICE(f'Found tables: {tables}'))
        # Try to find a table with 'review' or 'destination' in the name
        table_name = None
        for t in tables:
            if 'review' in t.lower() or 'destination' in t.lower():
                table_name = t
                break
        if not table_name:
            table_name = tables[0]  # fallback to first table
        self.stdout.write(self.style.NOTICE(f'Using table: {table_name}'))
        # Get columns
        cursor.execute(f'PRAGMA table_info({table_name});')
        columns = [row[1] for row in cursor.fetchall()]
        self.stdout.write(self.style.NOTICE(f'Columns: {columns}'))
        # Try to map columns
        col_map = {c.lower(): c for c in columns}
        city_col = col_map.get('city')
        region_col = col_map.get('region_or_state') or col_map.get('state')
        country_col = col_map.get('country')
        article_col = col_map.get('article_content') or col_map.get('content')
        # Query all rows
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        destinations_created = 0
        for row in rows:
            row_dict = dict(zip(columns, row))
            city = row_dict.get(city_col, '').strip()
            region = row_dict.get(region_col, '').strip()
            country = row_dict.get(country_col, '').strip()
            article = row_dict.get(article_col, '')
            lat, lon = self.get_coordinates(city, region, country)
            # Use upsert (update or create) to avoid duplicates
            try:
                obj, created = Destination.objects.update_or_create(
                    name=f"{city}, {region}",
                    city=city,
                    region_or_state=region,
                    country=country,
                    defaults={
                        'article_content': article,
                        'latitude': lat,
                        'longitude': lon,
                        'image_url': row_dict.get('image_url', ''),
                        'created_at': row_dict.get('created_at') if 'created_at' in row_dict else None,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Created {city}, {region} ({lat}, {lon})'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'Updated {city}, {region} ({lat}, {lon})'
                    ))
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Failed to import destination {city}: {str(e)}'
                    )
                )
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {destinations_created} destinations')
        )
        conn.close()

    def retry_failed_geocodes(self):
        failed = Destination.objects.filter(latitude=0.0, longitude=0.0)
        retried = 0
        for dest in failed:
            lat, lon = self.get_coordinates(dest.city, dest.region_or_state, dest.country)
            if lat != 0.0 or lon != 0.0:
                dest.latitude = lat
                dest.longitude = lon
                dest.save()
                retried += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Updated {dest.name} to ({lat}, {lon})'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Could not geocode {dest.name} again.'
                ))
        self.stdout.write(self.style.SUCCESS(f'Retried geocoding for {retried} destinations'))
