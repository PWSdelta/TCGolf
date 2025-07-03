#!/usr/bin/env python3
"""
Golf Destination Guide Generator
Streamlined version using Ollama local models to generate golf destination guides
and save directly to Django database.
"""

import os
import sys
import json
import time
import requests
import argparse
from pathlib import Path
from datetime import datetime
import django
import pytz
from urllib.parse import quote

# Add Django project to Python path and setup
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class LanguageDetector:
    """Detects primary language(s) for countries to enable auto-language generation"""
    
    def __init__(self):
        # Comprehensive country to language mapping
        self.country_languages = {
            # Major Golf Destinations
            'Japan': ['ja', 'en'],
            'South Korea': ['ko', 'en'], 
            'Germany': ['de', 'en'],
            'Spain': ['es', 'en'],
            'France': ['fr', 'en'],
            'Italy': ['it', 'en'],
            'United Kingdom': ['en'],
            'Ireland': ['en'],
            'Scotland': ['en'],
            'Wales': ['en'],
            'England': ['en'],
            'Australia': ['en'],
            'New Zealand': ['en'],
            'Canada': ['en', 'fr'],
            'United States': ['en'],
            'USA': ['en'],
            
            # Asia-Pacific
            'Thailand': ['th', 'en'],
            'Singapore': ['en', 'zh', 'ms', 'ta'],
            'Malaysia': ['ms', 'en', 'zh'],
            'Indonesia': ['id', 'en'],
            'Philippines': ['tl', 'en'],
            'China': ['zh', 'en'],
            'Taiwan': ['zh', 'en'],
            'Hong Kong': ['zh', 'en'],
            'Macau': ['zh', 'en'],
            'India': ['hi', 'en'],
            'Vietnam': ['vi', 'en'],
            'Cambodia': ['km', 'en'],
            'Laos': ['lo', 'en'],
            'Myanmar': ['my', 'en'],
            'Sri Lanka': ['si', 'en'],
            'Nepal': ['ne', 'en'],
            'Bhutan': ['dz', 'en'],
            'Bangladesh': ['bn', 'en'],
            'Pakistan': ['ur', 'en'],
            
            # Middle East & Africa
            'UAE': ['ar', 'en'],
            'Qatar': ['ar', 'en'],
            'Kuwait': ['ar', 'en'],
            'Bahrain': ['ar', 'en'],
            'Saudi Arabia': ['ar', 'en'],
            'Jordan': ['ar', 'en'],
            'Lebanon': ['ar', 'en'],
            'Israel': ['he', 'en'],
            'Turkey': ['tr', 'en'],
            'Egypt': ['ar', 'en'],
            'Morocco': ['ar', 'fr', 'en'],
            'Tunisia': ['ar', 'fr', 'en'],
            'South Africa': ['af', 'en', 'zu'],
            'Kenya': ['sw', 'en'],
            'Tanzania': ['sw', 'en'],
            'Uganda': ['en'],
            'Rwanda': ['rw', 'en', 'fr'],
            'Ethiopia': ['am', 'en'],
            'Ghana': ['en'],
            'Nigeria': ['en'],
            'Senegal': ['fr', 'en'],
            'Ivory Coast': ['fr', 'en'],
            'Mauritius': ['en', 'fr'],
            'Seychelles': ['en', 'fr'],
            
            # Europe
            'Netherlands': ['nl', 'en'],
            'Belgium': ['nl', 'fr', 'en'],
            'Switzerland': ['de', 'fr', 'it', 'en'],
            'Austria': ['de', 'en'],
            'Portugal': ['pt', 'en'],
            'Norway': ['no', 'en'],
            'Sweden': ['sv', 'en'],
            'Denmark': ['da', 'en'],
            'Finland': ['fi', 'en'],
            'Iceland': ['is', 'en'],
            'Poland': ['pl', 'en'],
            'Czech Republic': ['cs', 'en'],
            'Slovakia': ['sk', 'en'],
            'Hungary': ['hu', 'en'],
            'Slovenia': ['sl', 'en'],
            'Croatia': ['hr', 'en'],
            'Serbia': ['sr', 'en'],
            'Montenegro': ['sr', 'en'],
            'Bosnia and Herzegovina': ['bs', 'en'],
            'North Macedonia': ['mk', 'en'],
            'Albania': ['sq', 'en'],
            'Bulgaria': ['bg', 'en'],
            'Romania': ['ro', 'en'],
            'Greece': ['el', 'en'],
            'Cyprus': ['el', 'tr', 'en'],
            'Malta': ['mt', 'en'],
            'Luxembourg': ['lb', 'fr', 'de', 'en'],
            'Monaco': ['fr', 'en'],
            'Andorra': ['ca', 'es', 'fr', 'en'],
            'San Marino': ['it', 'en'],
            'Vatican City': ['it', 'la', 'en'],
            'Liechtenstein': ['de', 'en'],
            'Estonia': ['et', 'en'],
            'Latvia': ['lv', 'en'],
            'Lithuania': ['lt', 'en'],
            'Belarus': ['be', 'ru', 'en'],
            'Ukraine': ['uk', 'en'],
            'Moldova': ['ro', 'en'],
            'Russia': ['ru', 'en'],
            
            # Latin America
            'Mexico': ['es', 'en'],
            'Guatemala': ['es', 'en'],
            'Belize': ['en', 'es'],
            'Honduras': ['es', 'en'],
            'El Salvador': ['es', 'en'],
            'Nicaragua': ['es', 'en'],
            'Costa Rica': ['es', 'en'],
            'Panama': ['es', 'en'],
            'Colombia': ['es', 'en'],
            'Venezuela': ['es', 'en'],
            'Guyana': ['en'],
            'Suriname': ['nl', 'en'],
            'French Guiana': ['fr', 'en'],
            'Brazil': ['pt', 'en'],
            'Ecuador': ['es', 'en'],
            'Peru': ['es', 'en'],
            'Bolivia': ['es', 'en'],
            'Paraguay': ['es', 'en'],
            'Uruguay': ['es', 'en'],
            'Argentina': ['es', 'en'],
            'Chile': ['es', 'en'],
            
            # Caribbean
            'Cuba': ['es', 'en'],
            'Jamaica': ['en'],
            'Haiti': ['ht', 'fr', 'en'],
            'Dominican Republic': ['es', 'en'],
            'Puerto Rico': ['es', 'en'],
            'Barbados': ['en'],
            'Trinidad and Tobago': ['en'],
            'Bahamas': ['en'],
            'Bermuda': ['en'],
            'Cayman Islands': ['en'],
            'Turks and Caicos': ['en'],
            'British Virgin Islands': ['en'],
            'US Virgin Islands': ['en'],
            'Anguilla': ['en'],
            'Antigua and Barbuda': ['en'],
            'Saint Kitts and Nevis': ['en'],
            'Dominica': ['en'],
            'Saint Lucia': ['en'],
            'Saint Vincent and the Grenadines': ['en'],
            'Grenada': ['en'],
            'Aruba': ['nl', 'en'],
            'Curacao': ['nl', 'en'],
            'Bonaire': ['nl', 'en'],
            'Martinique': ['fr', 'en'],
            'Guadeloupe': ['fr', 'en'],
            'Saint Martin': ['fr', 'en'],
            'Saint Barthelemy': ['fr', 'en'],
            
            # Pacific Islands
            'Fiji': ['fj', 'en'],
            'Tonga': ['to', 'en'],
            'Samoa': ['sm', 'en'],
            'Vanuatu': ['bi', 'en', 'fr'],
            'Solomon Islands': ['en'],
            'Papua New Guinea': ['en'],
            'New Caledonia': ['fr', 'en'],
            'French Polynesia': ['fr', 'en'],
            'Cook Islands': ['en'],
            'Niue': ['en'],
            'Palau': ['en'],
            'Marshall Islands': ['en'],
            'Micronesia': ['en'],
            'Kiribati': ['en'],
            'Tuvalu': ['en'],
            'Nauru': ['en'],
        }
    
    def get_languages_for_country(self, country):
        """Get list of languages for a country, with English as fallback"""
        country_clean = country.strip()
        
        # Direct lookup
        if country_clean in self.country_languages:
            return self.country_languages[country_clean]
        
        # Try case-insensitive lookup
        for key, languages in self.country_languages.items():
            if key.lower() == country_clean.lower():
                return languages
        
        # Try partial matching for common variations
        country_lower = country_clean.lower()
        for key, languages in self.country_languages.items():
            key_lower = key.lower()
            if (country_lower in key_lower or key_lower in country_lower):
                return languages
        
        # Default to English if no match found
        return ['en']
    
    def get_auto_languages(self, country, max_languages=2):
        """Get auto-detected languages for a country, limited by max_languages"""
        languages = self.get_languages_for_country(country)
        
        # Always include English, then add local language(s)
        if 'en' not in languages:
            languages = ['en'] + languages
        
        # Limit to max_languages
        return languages[:max_languages]
    
    def detect_languages_for_country(self, country):
        """Alias for get_languages_for_country for compatibility"""
        return self.get_languages_for_country(country)
    
    def get_language_name(self, lang_code):
        """Get human-readable language name from code"""
        language_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'it': 'Italian',
            'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese',
            'ar': 'Arabic', 'hi': 'Hindi', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian',
            'ms': 'Malay', 'tl': 'Filipino', 'he': 'Hebrew', 'tr': 'Turkish', 'nl': 'Dutch',
            'sv': 'Swedish', 'no': 'Norwegian', 'da': 'Danish', 'fi': 'Finnish', 'pl': 'Polish',
            'cs': 'Czech', 'sk': 'Slovak', 'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian',
            'hr': 'Croatian', 'sr': 'Serbian', 'sl': 'Slovenian', 'el': 'Greek', 'uk': 'Ukrainian',
            'be': 'Belarusian', 'lt': 'Lithuanian', 'lv': 'Latvian', 'et': 'Estonian', 'mt': 'Maltese',
            'ga': 'Irish', 'cy': 'Welsh', 'is': 'Icelandic', 'fo': 'Faroese', 'sq': 'Albanian',
            'mk': 'Macedonian', 'bs': 'Bosnian', 'me': 'Montenegrin', 'af': 'Afrikaans', 'zu': 'Zulu',
            'sw': 'Swahili', 'am': 'Amharic', 'rw': 'Kinyarwanda', 'ur': 'Urdu', 'bn': 'Bengali',
            'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam', 'kn': 'Kannada', 'gu': 'Gujarati',
            'pa': 'Punjabi', 'mr': 'Marathi', 'or': 'Odia', 'as': 'Assamese', 'ne': 'Nepali',
            'si': 'Sinhala', 'my': 'Burmese', 'km': 'Khmer', 'lo': 'Lao', 'dz': 'Dzongkha',
            'mn': 'Mongolian', 'kk': 'Kazakh', 'ky': 'Kyrgyz', 'uz': 'Uzbek', 'tg': 'Tajik',
            'tk': 'Turkmen', 'az': 'Azerbaijani', 'ka': 'Georgian', 'hy': 'Armenian', 'fa': 'Persian',
            'ps': 'Pashto', 'sd': 'Sindhi', 'ks': 'Kashmiri', 'ku': 'Kurdish', 'yi': 'Yiddish',
            'la': 'Latin', 'eu': 'Basque', 'ca': 'Catalan', 'gl': 'Galician', 'lb': 'Luxembourgish',
            'rm': 'Romansh', 'sc': 'Sardinian', 'co': 'Corsican', 'br': 'Breton', 'gd': 'Scottish Gaelic',
            'mi': 'Maori', 'haw': 'Hawaiian', 'sm': 'Samoan', 'to': 'Tongan', 'fj': 'Fijian',
            'bi': 'Bislama', 'ho': 'Hiri Motu', 'ht': 'Haitian Creole', 'pap': 'Papiamento'
        }
        return language_names.get(lang_code, lang_code.upper())

class RealTimeDataAPI:
    """Fetches real-time data for destinations including weather, time, exchange rates"""
    
    def __init__(self):
        # Free API services (no keys required for basic usage)
        self.weather_api = "http://wttr.in"
        self.timezone_api = "http://worldtimeapi.org/api"
        self.exchange_api = "https://api.exchangerate-api.com/v4/latest"
        self.country_api = "https://restcountries.com/v3.1"
    
    def get_weather_info(self, city, country):
        """Get current weather and forecast for destination"""
        try:
            location = f"{city},{country}"
            response = requests.get(
                f"{self.weather_api}/{quote(location)}?format=j1",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_condition', [{}])[0]
                return {
                    'temperature_c': current.get('temp_C', 'N/A'),
                    'temperature_f': current.get('temp_F', 'N/A'),
                    'condition': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    'humidity': current.get('humidity', 'N/A'),
                    'wind_speed': current.get('windspeedKmph', 'N/A'),
                    'visibility': current.get('visibility', 'N/A'),
                    'uv_index': current.get('uvIndex', 'N/A'),
                    'feels_like_c': current.get('FeelsLikeC', 'N/A'),
                    'feels_like_f': current.get('FeelsLikeF', 'N/A')
                }
        except Exception as e:
            print(f"⚠️  Weather API error: {e}")
        return None
    
    def get_timezone_info(self, country):
        """Get current local time and timezone for destination"""
        try:
            # Get timezone by country
            response = requests.get(
                f"{self.timezone_api}/timezone/Europe/London",  # Default fallback
                timeout=10
            )
            
            # Try to get country-specific timezone
            country_zones = {
                'Japan': 'Asia/Tokyo',
                'South Korea': 'Asia/Seoul',
                'Germany': 'Europe/Berlin',
                'Spain': 'Europe/Madrid',
                'France': 'Europe/Paris',
                'Italy': 'Europe/Rome',
                'United Kingdom': 'Europe/London',
                'Australia': 'Australia/Sydney',
                'New Zealand': 'Pacific/Auckland',
                'Thailand': 'Asia/Bangkok',
                'Singapore': 'Asia/Singapore',
                'Malaysia': 'Asia/Kuala_Lumpur',
                'Indonesia': 'Asia/Jakarta',
                'Philippines': 'Asia/Manila',
                'China': 'Asia/Shanghai',
                'India': 'Asia/Kolkata',
                'UAE': 'Asia/Dubai',
                'South Africa': 'Africa/Johannesburg'
            }
            
            timezone = country_zones.get(country, 'UTC')
            response = requests.get(
                f"{self.timezone_api}/timezone/{timezone}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'timezone': data.get('timezone', timezone),
                    'local_time': data.get('datetime', '').split('T')[1][:8] if 'datetime' in data else 'N/A',
                    'local_date': data.get('datetime', '').split('T')[0] if 'datetime' in data else 'N/A',
                    'utc_offset': data.get('utc_offset', 'N/A'),
                    'day_of_week': data.get('day_of_week', 'N/A')
                }
        except Exception as e:
            print(f"⚠️  Timezone API error: {e}")
        return None
    
    def get_exchange_rates(self, country):
        """Get current exchange rates for destination currency"""
        try:
            # Currency mapping for countries
            currency_map = {
                'Japan': 'JPY',
                'South Korea': 'KRW',
                'Germany': 'EUR',
                'Spain': 'EUR',
                'France': 'EUR',
                'Italy': 'EUR',
                'United Kingdom': 'GBP',
                'Australia': 'AUD',
                'New Zealand': 'NZD',
                'Thailand': 'THB',
                'Singapore': 'SGD',
                'Malaysia': 'MYR',
                'Indonesia': 'IDR',
                'Philippines': 'PHP',
                'China': 'CNY',
                'India': 'INR',
                'UAE': 'AED',
                'South Africa': 'ZAR'
            }
            
            currency = currency_map.get(country, 'USD')
            
            # Get rates from USD base
            response = requests.get(f"{self.exchange_api}/USD", timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                return {
                    'currency': currency,
                    'usd_to_local': rates.get(currency, 1),
                    'eur_to_local': rates.get(currency, 1) / rates.get('EUR', 1) if rates.get('EUR') else None,
                    'gbp_to_local': rates.get(currency, 1) / rates.get('GBP', 1) if rates.get('GBP') else None,
                    'last_updated': data.get('date', 'N/A')
                }
        except Exception as e:
            print(f"⚠️  Exchange rate API error: {e}")
        return None
    
    def get_country_info(self, country):
        """Get basic country information"""
        try:
            response = requests.get(
                f"{self.country_api}/name/{quote(country)}?fullText=true",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    country_data = data[0]
                    return {
                        'capital': country_data.get('capital', ['N/A'])[0] if country_data.get('capital') else 'N/A',
                        'population': country_data.get('population', 'N/A'),
                        'languages': list(country_data.get('languages', {}).values()) if country_data.get('languages') else ['N/A'],
                        'currency_name': list(country_data.get('currencies', {}).values())[0].get('name', 'N/A') if country_data.get('currencies') else 'N/A',
                        'currency_symbol': list(country_data.get('currencies', {}).values())[0].get('symbol', 'N/A') if country_data.get('currencies') else 'N/A',
                        'calling_code': country_data.get('idd', {}).get('root', '') + (country_data.get('idd', {}).get('suffixes', [''])[0] if country_data.get('idd', {}).get('suffixes') else ''),
                        'driving_side': country_data.get('car', {}).get('side', 'N/A')
                    }
        except Exception as e:
            print(f"⚠️  Country info API error: {e}")
        return None
    
    def get_all_destination_data(self, city, country):
        """Get all real-time data for a destination"""
        print(f"🌐 Fetching real-time data for {city}, {country}...")
        
        data = {
            'weather': self.get_weather_info(city, country),
            'timezone': self.get_timezone_info(country),
            'exchange': self.get_exchange_rates(country),
            'country': self.get_country_info(country),
            'generated_at': datetime.now().isoformat()
        }
        
        return data
    
    def format_data_for_prompt(self, data):
        """Format the real-time data for inclusion in LLM prompts"""
        if not data:
            return ""
        
        formatted = "\n\n### CURRENT REAL-TIME DATA ###\n"
        
        # Weather information
        if data.get('weather'):
            w = data['weather']
            formatted += f"**Current Weather:**\n"
            formatted += f"- Temperature: {w.get('temperature_c', 'N/A')}°C ({w.get('temperature_f', 'N/A')}°F)\n"
            formatted += f"- Feels like: {w.get('feels_like_c', 'N/A')}°C ({w.get('feels_like_f', 'N/A')}°F)\n"
            formatted += f"- Conditions: {w.get('condition', 'N/A')}\n"
            formatted += f"- Humidity: {w.get('humidity', 'N/A')}%\n"
            formatted += f"- Wind Speed: {w.get('wind_speed', 'N/A')} km/h\n"
            formatted += f"- UV Index: {w.get('uv_index', 'N/A')}\n"
            formatted += f"- Visibility: {w.get('visibility', 'N/A')} km\n\n"
        
        # Time and timezone
        if data.get('timezone'):
            t = data['timezone']
            formatted += f"**Local Time & Date:**\n"
            formatted += f"- Current local time: {t.get('local_time', 'N/A')}\n"
            formatted += f"- Local date: {t.get('local_date', 'N/A')}\n"
            formatted += f"- Timezone: {t.get('timezone', 'N/A')}\n"
            formatted += f"- UTC offset: {t.get('utc_offset', 'N/A')}\n\n"
        
        # Exchange rates
        if data.get('exchange'):
            e = data['exchange']
            formatted += f"**Currency & Exchange Rates:**\n"
            formatted += f"- Local currency: {e.get('currency', 'N/A')}\n"
            formatted += f"- 1 USD = {e.get('usd_to_local', 'N/A')} {e.get('currency', '')}\n"
            if e.get('eur_to_local'):
                formatted += f"- 1 EUR = {e.get('eur_to_local', 'N/A'):.2f} {e.get('currency', '')}\n"
            if e.get('gbp_to_local'):
                formatted += f"- 1 GBP = {e.get('gbp_to_local', 'N/A'):.2f} {e.get('currency', '')}\n"
            formatted += f"- Rates updated: {e.get('last_updated', 'N/A')}\n\n"
        
        # Country information
        if data.get('country'):
            c = data['country']
            formatted += f"**Country Information:**\n"
            formatted += f"- Capital: {c.get('capital', 'N/A')}\n"
            formatted += f"- Population: {c.get('population', 'N/A'):,}\n" if isinstance(c.get('population'), int) else f"- Population: {c.get('population', 'N/A')}\n"
            formatted += f"- Languages: {', '.join(c.get('languages', ['N/A']))}\n"
            formatted += f"- Currency: {c.get('currency_name', 'N/A')} ({c.get('currency_symbol', 'N/A')})\n"
            formatted += f"- International calling code: {c.get('calling_code', 'N/A')}\n"
            formatted += f"- Driving side: {c.get('driving_side', 'N/A')}\n\n"
        
        formatted += "### END REAL-TIME DATA ###\n\n"
        formatted += "Please incorporate this current, real-time information naturally into your golf destination guide.\n\n"
        
        return formatted

def get_coordinates(city, region, country):
    """Get coordinates for a location using geocoding"""
    geolocator = Nominatim(user_agent="golfplex-generator")
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

class OllamaGenerator:
    """Handles Ollama API calls for local LLM generation"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def list_models(self):
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            else:
                print(f"❌ Error listing models: {response.status_code}")
                return []
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama. Make sure it's running on localhost:11434")
            return []
    
    def generate_guide(self, model, city, region, country, temperature=0.7, prompt_file="prompt-worldwide.txt", language="en", include_realtime_data=True):
        """Generate a golf destination guide using Ollama with streaming output and real-time data"""
        
        # Fetch real-time data if requested
        real_time_data_text = ""
        if include_realtime_data:
            try:
                api = RealTimeDataAPI()
                real_time_data = api.get_all_destination_data(city, country)
                real_time_data_text = api.format_data_for_prompt(real_time_data)
            except Exception as e:
                print(f"⚠️  Could not fetch real-time data: {e}")
                real_time_data_text = ""
        
        # Determine the appropriate prompt file based on language
        if language != "en" and prompt_file == "prompt-worldwide.txt":
            # Check for language-specific prompt files
            lang_prompt_map = {
                'de': 'prompt-german.txt',
                'es': 'prompt-spanish.txt',
                'ja': 'prompt-japanese.txt',
                'ko': 'prompt-korean.txt',
                'fr': 'prompt-french.txt',
                'it': 'prompt-italian.txt',
            }
            if language in lang_prompt_map:
                lang_prompt_file = lang_prompt_map[language]
                if os.path.exists(lang_prompt_file):
                    prompt_file = lang_prompt_file
                    print(f"🌍 Using {language} prompt file: {prompt_file}")
        
        # Load prompt template from file
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            print(f"⚠️  Prompt file '{prompt_file}' not found, using default prompt")
            # Fallback to simple prompt if file not found
            if language == 'de':
                prompt_template = """Schreibe einen umfassenden Golf-Reiseführer für {city}, {region}, {country} auf Deutsch.
                
Erstelle einen detaillierten Führer mit Platzbewertungen, Reisetipps, lokaler Kultur und praktischen Informationen für deutsche Golfer. 2500-3000 Wörter."""
            elif language == 'es':
                prompt_template = """Escribe una guía completa de destino de golf para {city}, {region}, {country} en español.
                
Crea una guía detallada que cubra reseñas de campos, consejos de viaje, cultura local e información práctica para golfistas españoles y latinoamericanos. 2500-3000 palabras."""
            else:
                prompt_template = """Write a comprehensive golf destination guide for {city}, {region}, {country}.
                
Create a detailed guide covering course reviews, travel tips, local culture, and practical information for international golfers. Make it 2500-3000 words."""
        
        # Format the prompt with the destination details
        location = f"{city}, {region}, {country}"
        prompt = prompt_template.format(city=city, region=region, country=country, location=location)
        
        # Add real-time data to the prompt
        if real_time_data_text:
            prompt = real_time_data_text + prompt

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,  # Enable streaming
            "options": {
                "temperature": temperature,
                "num_predict": 16000,  # Significantly increased for 2500-3000 word articles
                # Increase context window for international destinations
                "num_ctx": 8192 if hasattr(self, 'low_resource') and self.low_resource else 16384,
                "num_thread": 4 if hasattr(self, 'low_resource') and self.low_resource else None,
                # Additional parameters to ensure complete generation
                "repeat_penalty": 1.05,  # Slightly reduced to allow more natural repetition
                "top_k": 50,  # Increased for more variety
                "top_p": 0.95,  # Increased for more creative content
                "stop": [],  # Don't stop on any particular tokens
                # Additional parameters for longer generation
                "num_keep": 4,
                "typical_p": 1.0,
                "min_p": 0.05
            }
        }
        
        try:
            print(f"🤖 Generating guide for {city}, {region}, {country}...")
            print("💭 Content generation in progress...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                stream=True,  # Enable streaming
                timeout=600  # Increased to 10 minutes
            )
            
            if response.status_code != 200:
                return None, f"❌ Error: {response.status_code} - {response.text}"
            
            # Process streaming response
            content = ""
            word_count = 0
            last_progress_time = time.time()
            
            print("📝 Starting generation...", end="", flush=True)  # Immediate feedback
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            new_text = chunk['response']
                            content += new_text
                            
                            # Update progress every second for more responsive feedback
                            current_time = time.time()
                            if current_time - last_progress_time > 1:  # Update every 1 second
                                word_count = len(content.split())
                                elapsed = current_time - start_time
                                print(f"\r📝 {word_count} words generated ({elapsed:.1f}s)...", end="", flush=True)
                                last_progress_time = current_time
                            
                        if chunk.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        # Show we're still alive even if JSON parsing fails
                        current_time = time.time()
                        if current_time - last_progress_time > 5:
                            elapsed = current_time - start_time
                            print(f"\r📝 Processing... ({elapsed:.1f}s)", end="", flush=True)
                            last_progress_time = current_time
                        continue
            
            end_time = time.time()
            generation_time = end_time - start_time
            final_word_count = len(content.split())
            
            print(f"\r✅ Generated {final_word_count} words in {generation_time:.2f} seconds")
            print(f"📊 Content: {len(content)} characters")
            
            return content.strip(), None
            
        except requests.exceptions.ConnectionError:
            return None, "❌ Cannot connect to Ollama. Make sure it's running."
        except requests.exceptions.Timeout:
            return None, "❌ Request timed out (10 minutes). Try a smaller model or reduce content length."
        except Exception as e:
            return None, f"❌ Error: {str(e)}"

class DatabaseManager:
    """Handles Django database operations for golf destinations"""
    
    def save_destination(self, city, region, country, article_content, language="en"):
        """Save or update destination in Django database with multi-language support"""
        try:
            # Check if destination already exists
            existing = Destination.objects.filter(
                city__iexact=city,
                region_or_state__iexact=region,
                country__iexact=country
            ).first()
            
            if existing:
                print(f"📝 Updating existing destination: {city}, {country} ({language})")
                # Set content for the specific language
                existing.set_article_content(article_content, language)
                existing.save()
                return existing, "updated"
            
            # Create new destination
            print(f"🆕 Creating new destination: {city}, {country} ({language})")
            
            # Get coordinates
            coords = get_coordinates(city, region, country)
            lat, lng = coords if coords else (0.0, 0.0)
            
            if not coords:
                print(f"⚠️  Could not get coordinates for {city}, {country}")
            
            destination = Destination.objects.create(
                name=f"{city}, {region}",
                city=city,
                region_or_state=region,
                country=country,
                description=f"Golf destination guide for {city}, {region}",
                latitude=lat,
                longitude=lng
            )
            
            # Set the article content for the specific language
            destination.set_article_content(article_content, language)
            destination.save()
            
            return destination, "created"
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None, str(e)

def load_destinations_file(file_path):
    """Load destinations from a text file"""
    destinations = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == 3:
                        destinations.append(tuple(parts))
                    else:
                        print(f"⚠️  Skipping invalid line {line_num}: {line}")
        return destinations
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Generate golf destination guides with Ollama")
    parser.add_argument("--model", "-m", default="gemma3n:e4b", help="Ollama model name")
    parser.add_argument("--destination", "-d", help="Single destination: 'City, Region, Country'")
    parser.add_argument("--file", "-f", help="File with destinations (one per line)")
    parser.add_argument("--prompt", "-p", default="prompt-worldwide.txt", help="Prompt template file")
    parser.add_argument("--language", "-lang", default="en", help="Language code (en, de, es, fr, it)")
    parser.add_argument("--multi-language", "-ml", action="store_true", help="Generate content in major languages (en, es, de, ja, ko)")
    parser.add_argument("--languages", nargs="+", help="Specific languages to generate (e.g., --languages en es de)")
    parser.add_argument("--auto-language", "-al", action="store_true", help="Automatically detect country language + English")
    parser.add_argument("--auto-language-max", type=int, default=2, help="Maximum languages for auto-detection (default: 2)")
    parser.add_argument("--test-languages", action="store_true", help="Test language detection for destinations without generating content")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available models")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Generation temperature")
    parser.add_argument("--delay", type=int, default=2, help="Delay between generations (seconds)")
    parser.add_argument("--start-from", type=int, default=0, help="Start from destination number (0-based)")
    parser.add_argument("--low-resource", action="store_true", help="Use lower resource settings for concurrent processing")
    parser.add_argument("--no-realtime", action="store_true", help="Skip real-time data fetching (faster generation)")
    parser.add_argument("--realtime-only", action="store_true", help="Only fetch and display real-time data without generation")
    
    args = parser.parse_args()
    
    # Initialize language detector
    lang_detector = LanguageDetector()
    
    # Test language detection mode
    if args.test_languages:
        print("🧪 LANGUAGE DETECTION TEST")
        print("=" * 40)
        
        if args.destination:
            parts = [p.strip() for p in args.destination.split(',')]
            if len(parts) == 3:
                city, region, country = parts
                auto_langs = lang_detector.get_auto_languages(country, args.auto_language_max)
                all_langs = lang_detector.detect_languages_for_country(country)
                
                print(f"📍 Destination: {city}, {region}, {country}")
                print(f"🗣️  All languages detected: {', '.join([lang_detector.get_language_name(lang) for lang in all_langs])}")
                print(f"🎯 Auto-selected (max {args.auto_language_max}): {', '.join([lang_detector.get_language_name(lang) for lang in auto_langs])}")
                print(f"📝 Language codes: {', '.join(auto_langs)}")
        elif args.file:
            destinations = load_destinations_file(args.file)
            for city, region, country in destinations:
                auto_langs = lang_detector.get_auto_languages(country, args.auto_language_max)
                all_langs = lang_detector.detect_languages_for_country(country)
                
                print(f"\n📍 {city}, {country}")
                print(f"   🗣️  All: {', '.join([lang_detector.get_language_name(lang) for lang in all_langs])}")
                print(f"   🎯 Auto: {', '.join([lang_detector.get_language_name(lang) for lang in auto_langs])}")
        else:
            # Test some sample countries
            test_countries = ['Japan', 'Germany', 'Spain', 'France', 'South Korea', 'Thailand', 'Mexico', 'Brazil']
            for country in test_countries:
                auto_langs = lang_detector.get_auto_languages(country, args.auto_language_max)
                all_langs = lang_detector.detect_languages_for_country(country)
                
                print(f"\n🌍 {country}")
                print(f"   🗣️  All: {', '.join([lang_detector.get_language_name(lang) for lang in all_langs])}")
                print(f"   🎯 Auto: {', '.join([lang_detector.get_language_name(lang) for lang in auto_langs])}")
        
        return
    
    # Determine which languages to generate
    if args.multi_language:
        target_languages = ['en', 'es', 'de', 'ja', 'ko']  # Major international markets
        print("🌍 Multi-language mode: Generating content in English, Spanish, German, Japanese, and Korean")
    elif args.auto_language:
        # Auto-detect will be done per destination since it depends on country
        target_languages = None  # Will be set per destination
        print(f"🤖 Auto-language mode: Detecting country languages + English (max {args.auto_language_max})")
    elif args.languages:
        target_languages = args.languages
        lang_names = [lang_detector.get_language_name(lang) for lang in target_languages]
        print(f"🌍 Custom languages: {', '.join(lang_names)}")
    else:
        target_languages = [args.language]
    
    # Initialize components
    ollama = OllamaGenerator()
    db = DatabaseManager()
    
    # List models
    if args.list_models:
        models = ollama.list_models()
        if models:
            print("📋 Available Ollama models:")
            for model in models:
                print(f"   • {model}")
        else:
            print("❌ No models found or Ollama not running")
        return
    
    # Check if model exists
    available_models = ollama.list_models()
    if not available_models:
        print("❌ No Ollama models available")
        return
    
    if args.model not in available_models:
        print(f"❌ Model '{args.model}' not found")
        print(f"Available models: {', '.join(available_models)}")
        return
    
    # Get destinations to process
    destinations = []
    
    if args.destination:
        # Single destination
        parts = [p.strip() for p in args.destination.split(',')]
        if len(parts) != 3:
            print("❌ Destination must be in format: 'City, Region, Country'")
            return
        destinations = [tuple(parts)]
    
    elif args.file:
        # File with destinations
        destinations = load_destinations_file(args.file)
        if not destinations:
            return
    
    else:
        # Interactive mode
        print("🏌️ GOLF DESTINATION GUIDE GENERATOR")
        print("=" * 40)
        print(f"Using model: {args.model}")
        
        while True:
            try:
                dest_input = input("\nEnter destination (City, Region, Country) or 'quit': ").strip()
                if dest_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                parts = [p.strip() for p in dest_input.split(',')]
                if len(parts) != 3:
                    print("❌ Please use format: City, Region, Country")
                    continue
                
                destinations = [tuple(parts)]
                break
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return
    
    if not destinations:
        print("❌ No destinations to process")
        return
    
    # Apply start-from filter for batch processing
    if args.start_from > 0:
        destinations = destinations[args.start_from:]
        print(f"📍 Starting from destination #{args.start_from + 1}")
    
    # Process destinations
    if args.auto_language:
        # For auto-language, we'll calculate total after detecting languages per destination
        print(f"\n🚀 Processing {len(destinations)} destinations with auto-language detection")
        print(f"🤖 Using model: {args.model}")
        print("=" * 60)
        
        # Pre-calculate total operations for progress tracking
        total_operations = 0
        for city, region, country in destinations:
            auto_langs = lang_detector.get_auto_languages(country, args.auto_language_max)
            total_operations += len(auto_langs)
        
        print(f"📊 Estimated total generations: {total_operations}")
    else:
        total_languages = len(target_languages)
        total_operations = len(destinations) * total_languages
        print(f"\n🚀 Processing {len(destinations)} destinations in {total_languages} languages")
        print(f"📊 Total generations: {total_operations}")
        print(f"🤖 Using model: {args.model}")
        print("=" * 60)
    
    # Check for real-time only mode
    if args.realtime_only:
        print("🌐 REAL-TIME DATA ONLY MODE")
        print("=" * 40)
        api = RealTimeDataAPI()
        
        for i, (city, region, country) in enumerate(destinations, 1):
            print(f"\n📍 [{i}/{len(destinations)}] {city}, {region}, {country}")
            print("-" * 40)
            
            real_time_data = api.get_all_destination_data(city, country)
            formatted_data = api.format_data_for_prompt(real_time_data)
            print(formatted_data)
            
            if i < len(destinations):
                print(f"⏱️  Waiting {args.delay} seconds...")
                time.sleep(args.delay)
        
        return
    
    # Determine whether to include real-time data
    include_realtime = not args.no_realtime
    if include_realtime:
        print("🌐 Real-time data fetching: ENABLED")
    else:
        print("⚡ Real-time data fetching: DISABLED (faster generation)")
    
    print(f"\n🚀 Processing {len(destinations)} destinations in {total_languages} languages")
    print(f"📊 Total generations: {total_operations}")
    print(f"🤖 Using model: {args.model}")
    print("=" * 60)
    
    success_count = 0
    failed_destinations = []
    operation_count = 0
    
    for dest_idx, (city, region, country) in enumerate(destinations, args.start_from + 1):
        print(f"\n🏌️ [{dest_idx}/{len(destinations) + args.start_from}] Destination: {city}, {region}, {country}")
        print("=" * 50)
        
        # Determine languages for this specific destination
        if args.auto_language:
            current_target_languages = lang_detector.get_auto_languages(country, args.auto_language_max)
            lang_names = [lang_detector.get_language_name(lang) for lang in current_target_languages]
            print(f"🤖 Auto-detected languages: {', '.join(lang_names)}")
        else:
            current_target_languages = target_languages
        
        destination_success = 0
        destination_failures = []
        
        for lang_idx, language in enumerate(current_target_languages, 1):
            operation_count += 1
            language_name = lang_detector.get_language_name(language)
            
            print(f"\n📍 [{operation_count}/{total_operations}] Generating {language_name} content...")
            print("-" * 40)
            
            # Generate content with real-time data option
            content, error = ollama.generate_guide(
                args.model, city, region, country, 
                args.temperature, args.prompt, language, 
                include_realtime_data=include_realtime
            )
            
            if error:
                print(error)
                destination_failures.append((language, error))
                continue
            
            if not content:
                print(f"❌ No content generated for {city}, {country} ({language})")
                destination_failures.append((language, "No content generated"))
                continue
            
            # Save to database
            destination_obj, status = db.save_destination(city, region, country, content, language)
            
            if destination_obj:
                print(f"✅ {status.title()}: {destination_obj.name} ({language_name})")
                print(f"🔗 URL: {destination_obj.get_absolute_url(language)}")
                destination_success += 1
                success_count += 1
            else:
                print(f"❌ Failed to save: {city}, {country} ({language})")
                destination_failures.append((language, "Database save failed"))
            
            # Add delay between language generations
            if lang_idx < len(current_target_languages) and args.delay > 0:
                print(f"⏱️  Language delay: {args.delay} seconds...")
                time.sleep(args.delay)
        
        # Show destination summary
        print(f"\n📊 Destination Summary: {city}, {country}")
        print(f"✅ Successful languages: {destination_success}/{len(current_target_languages)}")
        if destination_failures:
            print("❌ Failed languages:")
            for lang, reason in destination_failures:
                lang_name = lang_detector.get_language_name(lang)
                print(f"   - {lang_name}: {reason}")
        
        # Show available languages for this destination
        if destination_success > 0:
            # Get updated destination to show all available languages
            updated_dest = Destination.objects.filter(
                city__iexact=city,
                region_or_state__iexact=region,
                country__iexact=country
            ).first()
            if updated_dest:
                available_langs = updated_dest.get_available_languages()
                lang_names = [lang_detector.get_language_name(lang) for lang in available_langs]
                print(f"🌍 Available languages: {', '.join(lang_names)}")
        
        # Add delay between destinations
        if dest_idx < len(destinations) + args.start_from and len(current_target_languages) > 1:
            print(f"\n⏱️  Destination delay: {args.delay * 2} seconds...")
            time.sleep(args.delay * 2)
    
    # Summary
    print("\n" + "=" * 60)
    if args.auto_language:
        print("📊 AUTO-LANGUAGE GENERATION SUMMARY")
    else:
        print("📊 MULTI-LANGUAGE GENERATION SUMMARY")
    print("=" * 60)
    print(f"🏌️ Destinations processed: {len(destinations)}")
    
    if args.auto_language:
        print("🤖 Mode: Auto-language detection")
        print(f"📝 Max languages per destination: {args.auto_language_max}")
    else:
        lang_names = [lang_detector.get_language_name(lang) for lang in target_languages]
        print(f"🌍 Languages: {', '.join(lang_names)}")
    
    print(f"✅ Successful generations: {success_count}/{total_operations}")
    print(f"❌ Failed generations: {total_operations - success_count}")
    print(f"📈 Success rate: {success_count / total_operations * 100:.1f}%")
    
    # Show detailed breakdown by destination
    print(f"\n📋 Destination breakdown:")
    for city, region, country in destinations:
        dest_obj = Destination.objects.filter(
            city__iexact=city,
            region_or_state__iexact=region,
            country__iexact=country
        ).first()
        
        if dest_obj:
            available_langs = dest_obj.get_available_languages()
            lang_names = [lang_detector.get_language_name(lang) for lang in available_langs]
            
            if args.auto_language:
                expected_langs = lang_detector.get_auto_languages(country, args.auto_language_max)
                print(f"   🌍 {city}, {country}: {len(available_langs)}/{len(expected_langs)} languages ({', '.join(lang_names)})")
            else:
                print(f"   🌍 {city}, {country}: {len(available_langs)}/{len(target_languages)} languages ({', '.join(lang_names)})")
        else:
            print(f"   ❌ {city}, {country}: No content generated")
