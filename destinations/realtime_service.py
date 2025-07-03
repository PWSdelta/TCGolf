"""
Real-time data service for golf destinations
Integrates with external APIs to provide current weather, time, and exchange rate data
"""

import requests
import json
from datetime import datetime
from urllib.parse import quote
try:
    from django.core.cache import cache
    DJANGO_CACHE_AVAILABLE = True
except:
    DJANGO_CACHE_AVAILABLE = False
import logging

logger = logging.getLogger(__name__)

class RealTimeDestinationData:
    """Service to fetch real-time data for golf destinations"""
    
    def __init__(self):
        # Free API services (no keys required for basic usage)
        self.weather_api = "http://wttr.in"
        self.timezone_api = "http://worldtimeapi.org/api"
        self.exchange_api = "https://api.exchangerate-api.com/v4/latest"
        self.country_api = "https://restcountries.com/v3.1"
        
        # Cache timeout in seconds (15 minutes for weather, 1 hour for exchange rates)
        self.weather_cache_timeout = 900  # 15 minutes
        self.exchange_cache_timeout = 3600  # 1 hour
        self.timezone_cache_timeout = 86400  # 24 hours
    
    def get_cache_key(self, data_type, location):
        """Generate cache key for data storage"""
        return f"realtime_{data_type}_{location.lower().replace(' ', '_').replace(',', '')}"
    
    def get_weather_data(self, city, country):
        """Get current weather data with caching"""
        cache_key = self.get_cache_key('weather', f"{city}_{country}")
        
        # Try to get cached data if Django cache is available
        cached_data = None
        if DJANGO_CACHE_AVAILABLE:
            try:
                cached_data = cache.get(cache_key)
            except:
                cached_data = None
        
        if cached_data:
            return cached_data
        
        try:
            location = f"{city},{country}"
            response = requests.get(
                f"{self.weather_api}/{quote(location)}?format=j1",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_condition', [{}])[0]
                
                weather_data = {
                    'temperature_c': current.get('temp_C', 'N/A'),
                    'temperature_f': current.get('temp_F', 'N/A'),
                    'condition': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    'humidity': current.get('humidity', 'N/A'),
                    'wind_speed_kmh': current.get('windspeedKmph', 'N/A'),
                    'wind_speed_mph': current.get('windspeedMiles', 'N/A'),
                    'visibility_km': current.get('visibility', 'N/A'),
                    'uv_index': current.get('uvIndex', 'N/A'),
                    'feels_like_c': current.get('FeelsLikeC', 'N/A'),
                    'feels_like_f': current.get('FeelsLikeF', 'N/A'),
                    'icon': self._get_weather_icon(current.get('weatherDesc', [{}])[0].get('value', '')),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Cache the data if Django cache is available
                if DJANGO_CACHE_AVAILABLE:
                    try:
                        cache.set(cache_key, weather_data, self.weather_cache_timeout)
                    except:
                        pass  # Continue without caching
                return weather_data
                
        except Exception as e:
            logger.warning(f"Weather API error for {city}, {country}: {e}")
        
        return None
    
    def get_timezone_data(self, country):
        """Get current local time data with caching"""
        cache_key = self.get_cache_key('timezone', country)
        
        # Try to get cached data if Django cache is available
        cached_data = None
        if DJANGO_CACHE_AVAILABLE:
            try:
                cached_data = cache.get(cache_key)
            except:
                cached_data = None
        
        if cached_data:
            return cached_data
        
        try:
            # Country to timezone mapping
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
                'South Africa': 'Africa/Johannesburg',
                'Mexico': 'America/Mexico_City',
                'Canada': 'America/Toronto',
                'Brazil': 'America/Sao_Paulo',
                'Argentina': 'America/Buenos_Aires',
                'Chile': 'America/Santiago'
            }
            
            timezone = country_zones.get(country, 'UTC')
            response = requests.get(
                f"{self.timezone_api}/timezone/{timezone}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse datetime
                dt_str = data.get('datetime', '')
                if 'T' in dt_str:
                    date_part, time_part = dt_str.split('T')
                    local_time = time_part[:8] if len(time_part) >= 8 else time_part
                    local_date = date_part
                else:
                    local_time = 'N/A'
                    local_date = 'N/A'
                
                timezone_data = {
                    'timezone': data.get('timezone', timezone),
                    'local_time': local_time,
                    'local_date': local_date,
                    'utc_offset': data.get('utc_offset', 'N/A'),
                    'day_of_week': data.get('day_of_week', 'N/A'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Cache the data if Django cache is available
                if DJANGO_CACHE_AVAILABLE:
                    try:
                        cache.set(cache_key, timezone_data, self.timezone_cache_timeout)
                    except:
                        pass  # Continue without caching
                return timezone_data
                
        except Exception as e:
            logger.warning(f"Timezone API error for {country}: {e}")
        
        return None
    
    def get_exchange_data(self, country):
        """Get exchange rate data with caching"""
        cache_key = self.get_cache_key('exchange', country)
        
        # Try to get cached data if Django cache is available
        cached_data = None
        if DJANGO_CACHE_AVAILABLE:
            try:
                cached_data = cache.get(cache_key)
            except:
                cached_data = None
        
        if cached_data:
            return cached_data
        
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
                'South Africa': 'ZAR',
                'Mexico': 'MXN',
                'Canada': 'CAD',
                'Brazil': 'BRL',
                'Argentina': 'ARS',
                'Chile': 'CLP'
            }
            
            currency = currency_map.get(country, 'USD')
            
            # Get rates from USD base
            response = requests.get(f"{self.exchange_api}/USD", timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                exchange_data = {
                    'currency': currency,
                    'currency_symbol': self._get_currency_symbol(currency),
                    'usd_to_local': rates.get(currency, 1),
                    'eur_to_local': rates.get(currency, 1) / rates.get('EUR', 1) if rates.get('EUR') else None,
                    'gbp_to_local': rates.get(currency, 1) / rates.get('GBP', 1) if rates.get('GBP') else None,
                    'last_updated': data.get('date', 'N/A'),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Cache the data if Django cache is available
                if DJANGO_CACHE_AVAILABLE:
                    try:
                        cache.set(cache_key, exchange_data, self.exchange_cache_timeout)
                    except:
                        pass  # Continue without caching
                return exchange_data
                
        except Exception as e:
            logger.warning(f"Exchange rate API error for {country}: {e}")
        
        return None
    
    def get_all_destination_data(self, city, country):
        """Get all real-time data for a destination"""
        return {
            'weather': self.get_weather_data(city, country),
            'timezone': self.get_timezone_data(country),
            'exchange': self.get_exchange_data(country),
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_weather_icon(self, condition):
        """Map weather conditions to emoji icons"""
        condition_lower = condition.lower()
        
        if 'sunny' in condition_lower or 'clear' in condition_lower:
            return '☀️'
        elif 'partly cloudy' in condition_lower or 'partly cloud' in condition_lower:
            return '⛅'
        elif 'cloudy' in condition_lower or 'overcast' in condition_lower:
            return '☁️'
        elif 'rain' in condition_lower or 'shower' in condition_lower:
            return '🌧️'
        elif 'thunder' in condition_lower or 'storm' in condition_lower:
            return '⛈️'
        elif 'snow' in condition_lower:
            return '❄️'
        elif 'fog' in condition_lower or 'mist' in condition_lower:
            return '🌫️'
        elif 'wind' in condition_lower:
            return '💨'
        else:
            return '🌤️'  # Default
    
    def _get_currency_symbol(self, currency_code):
        """Get currency symbol for common currencies"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'KRW': '₩',
            'AUD': 'A$',
            'CAD': 'C$',
            'CHF': 'Fr',
            'CNY': '¥',
            'INR': '₹',
            'THB': '฿',
            'SGD': 'S$',
            'MYR': 'RM',
            'IDR': 'Rp',
            'PHP': '₱',
            'AED': 'د.إ',
            'ZAR': 'R',
            'MXN': '$',
            'BRL': 'R$',
            'ARS': '$',
            'CLP': '$'
        }
        return symbols.get(currency_code, currency_code)
