#!/usr/bin/env python
"""
CityGuide Content Generator
Automatically generates comprehensive city guides for destinations
"""
import os
import django
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

class CityGuideGenerator:
    """
    Generates comprehensive city guides for destinations
    """
    
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh']
        self.generation_model = "content_generator_v1"
        
    def generate_city_guide(self, destination: Destination, language: str = 'en', 
                          force_regenerate: bool = False) -> Optional[CityGuide]:
        """
        Generate a comprehensive city guide for a destination
        
        Args:
            destination: The destination to generate a guide for
            language: Language code for the guide
            force_regenerate: Whether to regenerate existing guides
            
        Returns:
            CityGuide instance or None if generation failed
        """
        try:
            # Check if guide already exists
            existing_guide = CityGuide.objects.filter(
                destination=destination,
                language_code=language
            ).first()
            
            if existing_guide and not force_regenerate:
                print(f"✅ Guide already exists for {destination.city} ({language})")
                return existing_guide
            
            print(f"🎯 Generating city guide for {destination.city}, {destination.country} ({language})")
            
            # Generate content based on destination data
            guide_data = self._generate_guide_content(destination, language)
            
            # Create or update the guide
            if existing_guide:
                self._update_guide(existing_guide, guide_data)
                print(f"✅ Updated existing guide for {destination.city} ({language})")
                return existing_guide
            else:
                new_guide = self._create_guide(destination, language, guide_data)
                print(f"✅ Created new guide for {destination.city} ({language})")
                return new_guide
                
        except Exception as e:
            print(f"❌ Error generating guide for {destination.city}: {e}")
            return None
    
    def _generate_guide_content(self, destination: Destination, language: str) -> Dict[str, Any]:
        """
        Generate comprehensive content for a city guide
        """
        city = destination.city
        region = destination.region_or_state
        country = destination.country
        
        # Generate content based on language
        if language == 'en':
            return self._generate_english_content(city, region, country)
        elif language == 'es':
            return self._generate_spanish_content(city, region, country)
        elif language == 'fr':
            return self._generate_french_content(city, region, country)
        elif language == 'de':
            return self._generate_german_content(city, region, country)
        else:
            # Default to English template for unsupported languages
            return self._generate_english_content(city, region, country)
    
    def _generate_english_content(self, city: str, region: str, country: str) -> Dict[str, Any]:
        """Generate English content for a city guide"""
        
        # Generate overview based on location
        overview = self._generate_overview(city, region, country, 'en')
        
        # Generate neighborhoods
        neighborhoods = self._generate_neighborhoods(city, region, country, 'en')
        
        # Generate attractions
        attractions = self._generate_attractions(city, region, country, 'en')
        
        # Generate dining
        dining = self._generate_dining(city, region, country, 'en')
        
        # Generate nightlife
        nightlife = self._generate_nightlife(city, region, country, 'en')
        
        # Generate shopping
        shopping = self._generate_shopping(city, region, country, 'en')
        
        # Generate transportation
        transportation = self._generate_transportation(city, region, country, 'en')
        
        # Generate accommodation
        accommodation = self._generate_accommodation(city, region, country, 'en')
        
        # Generate seasonal guide
        seasonal_guide = self._generate_seasonal_guide(city, region, country, 'en')
        
        # Generate practical info
        practical_info = self._generate_practical_info(city, region, country, 'en')
        
        # Generate golf summary
        golf_summary = self._generate_golf_summary(city, region, country, 'en')
        
        # Generate meta description
        meta_description = f"Complete {city} travel guide: attractions, dining, nightlife, shopping, and insider tips for {city}, {country}."
        
        return {
            'overview': overview,
            'neighborhoods': neighborhoods,
            'attractions': attractions,
            'dining': dining,
            'nightlife': nightlife,
            'shopping': shopping,
            'transportation': transportation,
            'accommodation': accommodation,
            'seasonal_guide': seasonal_guide,
            'practical_info': practical_info,
            'golf_summary': golf_summary,
            'meta_description': meta_description,
            'is_published': True,
            'is_featured': False  # Can be set to True manually for featured destinations
        }
    
    def _generate_spanish_content(self, city: str, region: str, country: str) -> Dict[str, Any]:
        """Generate Spanish content for a city guide"""
        
        overview = f"{city} es una ciudad vibrante en {region}, {country}, conocida por su rica cultura, hermosa arquitectura y experiencias únicas. Esta metrópolis ofrece una perfecta combinación de tradición y modernidad, con atracciones fascinantes, excelente gastronomía y vida nocturna emocionante. Desde barrios históricos hasta áreas contemporáneas, {city} brinda una experiencia inolvidable para todos los visitantes."
        
        neighborhoods = {
            'Centro Histórico': {
                'description': f'El corazón histórico de {city} con arquitectura tradicional y sitios culturales importantes.',
                'highlights': ['Arquitectura histórica', 'Sitios culturales', 'Plazas principales'],
                'best_for': 'Historia, cultura, arquitectura'
            },
            'Zona Moderna': {
                'description': f'Área contemporánea de {city} con desarrollos modernos y amenidades actuales.',
                'highlights': ['Edificios modernos', 'Centros comerciales', 'Restaurantes nuevos'],
                'best_for': 'Compras, gastronomía moderna, vida nocturna'
            }
        }
        
        attractions = {
            'Atracción Principal': {
                'description': f'La atracción más importante de {city} que no puedes perderte.',
                'category': 'Turístico',
                'tips': 'Visita temprano por la mañana para evitar multitudes.'
            },
            'Sitio Cultural': {
                'description': f'Importante sitio cultural que representa la esencia de {city}.',
                'category': 'Cultural',
                'tips': 'Considera tomar un tour guiado para mejor comprensión.'
            }
        }
        
        dining = {
            'Restaurante Local': {
                'description': f'Auténtico restaurante que sirve la cocina tradicional de {region}.',
                'cuisine_type': 'Local',
                'price_range': '$$'
            },
            'Gastronomía Internacional': {
                'description': f'Restaurante de alta calidad con cocina internacional en {city}.',
                'cuisine_type': 'Internacional',
                'price_range': '$$$'
            }
        }
        
        nightlife = {
            'Vida Nocturna Local': {
                'description': f'Lugar popular para la vida nocturna en {city}.',
                'type': 'Bar/Club',
                'atmosphere': 'Animado, local, auténtico'
            }
        }
        
        shopping = {
            'Mercado Local': {
                'description': f'Mercado tradicional de {city} con productos locales y artesanías.',
                'specialty': 'Productos locales, artesanías',
                'price_range': '$-$$'
            }
        }
        
        transportation = {
            'Transporte Público': {
                'description': f'Sistema de transporte público de {city}.',
                'cost': 'Variable',
                'tips': 'Obtén pases diarios para ahorrar dinero.'
            }
        }
        
        accommodation = {
            'Hotel Céntrico': {
                'description': f'Hotel bien ubicado en el centro de {city}.',
                'area': 'Centro',
                'price_range': '$$-$$$'
            }
        }
        
        seasonal_guide = {
            'Temporada Alta': {
                'weather': 'Clima agradable, perfecto para actividades al aire libre',
                'activities': 'Turismo, actividades culturales, festivales',
                'events': 'Festivales locales, eventos culturales'
            }
        }
        
        practical_info = {
            'Idioma': {
                'details': 'Español es el idioma principal',
                'tips': 'Aprende frases básicas en español'
            },
            'Moneda': {
                'details': 'Consulta la moneda local',
                'tips': 'Cambia dinero en casas de cambio oficiales'
            }
        }
        
        golf_summary = f"{city} ofrece experiencias de golf únicas con campos que aprovechan el paisaje natural de {region}. Los golfistas pueden disfrutar de desafíos interesantes mientras admiran vistas espectaculares.\n\n<a href=\"#\" class=\"golf-link\">Explora los campos de golf de {city} →</a>"
        
        meta_description = f"Guía completa de {city}: atracciones, gastronomía, vida nocturna y consejos de viaje para {city}, {country}."
        
        return {
            'overview': overview,
            'neighborhoods': neighborhoods,
            'attractions': attractions,
            'dining': dining,
            'nightlife': nightlife,
            'shopping': shopping,
            'transportation': transportation,
            'accommodation': accommodation,
            'seasonal_guide': seasonal_guide,
            'practical_info': practical_info,
            'golf_summary': golf_summary,
            'meta_description': meta_description,
            'is_published': True,
            'is_featured': False
        }
    
    def _generate_french_content(self, city: str, region: str, country: str) -> Dict[str, Any]:
        """Generate French content for a city guide"""
        
        overview = f"{city} est une ville magnifique située dans {region}, {country}, réputée pour sa riche histoire, son architecture impressionnante et ses expériences culturelles uniques. Cette métropole offre un mélange parfait de tradition et de modernité, avec des attractions fascinantes, une excellente gastronomie et une vie nocturne animée. Des quartiers historiques aux zones contemporaines, {city} offre une expérience inoubliable à tous les visiteurs."
        
        neighborhoods = {
            'Centre Historique': {
                'description': f'Le cœur historique de {city} avec une architecture traditionnelle et des sites culturels importants.',
                'highlights': ['Architecture historique', 'Sites culturels', 'Places principales'],
                'best_for': 'Histoire, culture, architecture'
            },
            'Quartier Moderne': {
                'description': f'Zone contemporaine de {city} avec des développements modernes et des commodités actuelles.',
                'highlights': ['Bâtiments modernes', 'Centres commerciaux', 'Nouveaux restaurants'],
                'best_for': 'Shopping, gastronomie moderne, vie nocturne'
            }
        }
        
        attractions = {
            'Attraction Principale': {
                'description': f'L\'attraction la plus importante de {city} à ne pas manquer.',
                'category': 'Touristique',
                'tips': 'Visitez tôt le matin pour éviter la foule.'
            }
        }
        
        dining = {
            'Restaurant Local': {
                'description': f'Restaurant authentique servant la cuisine traditionnelle de {region}.',
                'cuisine_type': 'Locale',
                'price_range': '$$'
            }
        }
        
        nightlife = {
            'Vie Nocturne Locale': {
                'description': f'Lieu populaire pour la vie nocturne à {city}.',
                'type': 'Bar/Club',
                'atmosphere': 'Animé, local, authentique'
            }
        }
        
        shopping = {
            'Marché Local': {
                'description': f'Marché traditionnel de {city} avec des produits locaux et de l\'artisanat.',
                'specialty': 'Produits locaux, artisanat',
                'price_range': '$-$$'
            }
        }
        
        transportation = {
            'Transport Public': {
                'description': f'Système de transport public de {city}.',
                'cost': 'Variable',
                'tips': 'Obtenez des passes journaliers pour économiser.'
            }
        }
        
        accommodation = {
            'Hôtel Central': {
                'description': f'Hôtel bien situé au centre de {city}.',
                'area': 'Centre',
                'price_range': '$$-$$$'
            }
        }
        
        seasonal_guide = {
            'Haute Saison': {
                'weather': 'Climat agréable, parfait pour les activités en plein air',
                'activities': 'Tourisme, activités culturelles, festivals',
                'events': 'Festivals locaux, événements culturels'
            }
        }
        
        practical_info = {
            'Langue': {
                'details': 'Français est la langue principale',
                'tips': 'Apprenez quelques phrases de base en français'
            }
        }
        
        golf_summary = f"{city} offre des expériences de golf uniques avec des parcours qui tirent parti du paysage naturel de {region}. Les golfeurs peuvent profiter de défis intéressants tout en admirant des vues spectaculaires.\n\n<a href=\"#\" class=\"golf-link\">Explorez les terrains de golf de {city} →</a>"
        
        meta_description = f"Guide complet de {city}: attractions, gastronomie, vie nocturne et conseils de voyage pour {city}, {country}."
        
        return {
            'overview': overview,
            'neighborhoods': neighborhoods,
            'attractions': attractions,
            'dining': dining,
            'nightlife': nightlife,
            'shopping': shopping,
            'transportation': transportation,
            'accommodation': accommodation,
            'seasonal_guide': seasonal_guide,
            'practical_info': practical_info,
            'golf_summary': golf_summary,
            'meta_description': meta_description,
            'is_published': True,
            'is_featured': False
        }
    
    def _generate_german_content(self, city: str, region: str, country: str) -> Dict[str, Any]:
        """Generate German content for a city guide"""
        
        overview = f"{city} ist eine lebendige Stadt in {region}, {country}, bekannt für ihre reiche Geschichte, beeindruckende Architektur und einzigartige kulturelle Erlebnisse. Diese Metropole bietet eine perfekte Mischung aus Tradition und Moderne, mit faszinierenden Attraktionen, ausgezeichneter Gastronomie und aufregendem Nachtleben. Von historischen Vierteln bis zu zeitgenössischen Bereichen bietet {city} allen Besuchern ein unvergessliches Erlebnis."
        
        neighborhoods = {
            'Altstadt': {
                'description': f'Das historische Herz von {city} mit traditioneller Architektur und wichtigen kulturellen Stätten.',
                'highlights': ['Historische Architektur', 'Kulturelle Stätten', 'Hauptplätze'],
                'best_for': 'Geschichte, Kultur, Architektur'
            },
            'Moderne Viertel': {
                'description': f'Zeitgenössisches Gebiet von {city} mit modernen Entwicklungen und aktuellen Annehmlichkeiten.',
                'highlights': ['Moderne Gebäude', 'Einkaufszentren', 'Neue Restaurants'],
                'best_for': 'Shopping, moderne Gastronomie, Nachtleben'
            }
        }
        
        attractions = {
            'Hauptattraktion': {
                'description': f'Die wichtigste Attraktion von {city}, die Sie nicht verpassen sollten.',
                'category': 'Touristisch',
                'tips': 'Besuchen Sie früh am Morgen, um Menschenmassen zu vermeiden.'
            }
        }
        
        dining = {
            'Lokales Restaurant': {
                'description': f'Authentisches Restaurant, das traditionelle Küche aus {region} serviert.',
                'cuisine_type': 'Lokal',
                'price_range': '$$'
            }
        }
        
        nightlife = {
            'Lokales Nachtleben': {
                'description': f'Beliebter Ort für das Nachtleben in {city}.',
                'type': 'Bar/Club',
                'atmosphere': 'Lebhaft, lokal, authentisch'
            }
        }
        
        shopping = {
            'Lokaler Markt': {
                'description': f'Traditioneller Markt von {city} mit lokalen Produkten und Kunsthandwerk.',
                'specialty': 'Lokale Produkte, Kunsthandwerk',
                'price_range': '$-$$'
            }
        }
        
        transportation = {
            'Öffentlicher Verkehr': {
                'description': f'Öffentliches Verkehrssystem von {city}.',
                'cost': 'Variabel',
                'tips': 'Holen Sie sich Tageskarten, um Geld zu sparen.'
            }
        }
        
        accommodation = {
            'Zentrales Hotel': {
                'description': f'Gut gelegenes Hotel im Zentrum von {city}.',
                'area': 'Zentrum',
                'price_range': '$$-$$$'
            }
        }
        
        seasonal_guide = {
            'Hochsaison': {
                'weather': 'Angenehmes Klima, perfekt für Outdoor-Aktivitäten',
                'activities': 'Tourismus, kulturelle Aktivitäten, Festivals',
                'events': 'Lokale Festivals, kulturelle Veranstaltungen'
            }
        }
        
        practical_info = {
            'Sprache': {
                'details': 'Deutsch ist die Hauptsprache',
                'tips': 'Lernen Sie einige grundlegende deutsche Phrasen'
            }
        }
        
        golf_summary = f"{city} bietet einzigartige Golferlebnisse mit Plätzen, die die natürliche Landschaft von {region} nutzen. Golfer können interessante Herausforderungen genießen, während sie spektakuläre Aussichten bewundern.\n\n<a href=\"#\" class=\"golf-link\">Erkunden Sie die Golfplätze von {city} →</a>"
        
        meta_description = f"Vollständiger {city} Reiseführer: Attraktionen, Gastronomie, Nachtleben und Reisetipps für {city}, {country}."
        
        return {
            'overview': overview,
            'neighborhoods': neighborhoods,
            'attractions': attractions,
            'dining': dining,
            'nightlife': nightlife,
            'shopping': shopping,
            'transportation': transportation,
            'accommodation': accommodation,
            'seasonal_guide': seasonal_guide,
            'practical_info': practical_info,
            'golf_summary': golf_summary,
            'meta_description': meta_description,
            'is_published': True,
            'is_featured': False
        }
    
    def _generate_overview(self, city: str, region: str, country: str, language: str) -> str:
        """Generate city overview based on location"""
        
        # Template-based overview generation
        templates = {
            'coastal': f"{city} is a stunning coastal destination in {region}, {country}, where pristine beaches meet vibrant urban culture. This seaside gem offers the perfect blend of relaxation and adventure, with world-class dining, exciting nightlife, and breathtaking ocean views. From waterfront promenades to bustling markets, {city} delivers an unforgettable coastal experience.",
            
            'mountain': f"{city} is a picturesque mountain destination nestled in {region}, {country}, surrounded by majestic peaks and natural beauty. This alpine paradise combines outdoor adventures with cultural richness, offering hiking trails, scenic vistas, and authentic local experiences. From cozy mountain lodges to vibrant town centers, {city} provides the perfect mountain getaway.",
            
            'urban': f"{city} is a dynamic urban center in {region}, {country}, known for its innovative architecture, diverse culture, and bustling energy. This metropolitan hub offers a perfect blend of business and pleasure, with world-class shopping, exceptional dining, and rich cultural attractions. From historic districts to modern developments, {city} showcases the best of urban living.",
            
            'historic': f"{city} is a historic gem in {region}, {country}, where centuries of culture and tradition come alive through well-preserved architecture and timeless charm. This heritage destination offers visitors a journey through time, with ancient sites, traditional crafts, and authentic cultural experiences. From cobblestone streets to historic landmarks, {city} tells the story of {region}.",
            
            'resort': f"{city} is a premier resort destination in {region}, {country}, offering luxury accommodations, world-class amenities, and unforgettable experiences. This exclusive getaway combines natural beauty with sophisticated hospitality, featuring championship golf courses, spa treatments, and gourmet dining. From private beaches to elegant suites, {city} delivers the ultimate luxury experience.",
            
            'cultural': f"{city} is a vibrant cultural hub in {region}, {country}, celebrated for its rich artistic heritage, museums, and creative spirit. This cultural destination offers visitors an immersive experience in arts, music, and local traditions. From world-renowned galleries to intimate performance venues, {city} showcases the cultural heart of {region}.",
            
            'default': f"{city} is a captivating destination in {region}, {country}, offering visitors a unique blend of local culture, natural beauty, and modern amenities. This diverse city provides something for every traveler, from historic attractions to contemporary experiences. Whether you're seeking adventure, relaxation, or cultural enrichment, {city} delivers an unforgettable journey."
        }
        
        # Simple logic to determine city type (can be enhanced with external data)
        city_lower = city.lower()
        region_lower = region.lower()
        country_lower = country.lower()
        
        if any(word in city_lower for word in ['beach', 'coast', 'bay', 'harbor', 'port']):
            return templates['coastal']
        elif any(word in city_lower for word in ['mountain', 'alpine', 'peak', 'ridge']):
            return templates['mountain']
        elif any(word in city_lower for word in ['resort', 'spa', 'luxury']):
            return templates['resort']
        elif city_lower in ['paris', 'florence', 'rome', 'athens', 'prague', 'vienna']:
            return templates['historic']
        elif city_lower in ['new york', 'london', 'tokyo', 'sydney', 'chicago', 'singapore']:
            return templates['urban']
        elif city_lower in ['santa fe', 'charleston', 'savannah', 'quebec', 'bruges']:
            return templates['cultural']
        else:
            return templates['default']
    
    def _generate_neighborhoods(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate neighborhood information"""
        
        neighborhoods = {
            'Downtown': {
                'description': f'The bustling heart of {city} with major attractions, shopping, and dining.',
                'highlights': ['Main shopping areas', 'Business district', 'Cultural venues', 'Transportation hub'],
                'best_for': 'First-time visitors, business travelers, shopping enthusiasts'
            },
            'Historic District': {
                'description': f'Charming historic area of {city} with preserved architecture and cultural sites.',
                'highlights': ['Historic buildings', 'Museums', 'Walking tours', 'Local crafts'],
                'best_for': 'History buffs, architecture lovers, cultural experiences'
            },
            'Waterfront': {
                'description': f'Scenic waterfront area of {city} with beautiful views and outdoor activities.',
                'highlights': ['Waterfront promenades', 'Scenic views', 'Water activities', 'Outdoor dining'],
                'best_for': 'Romantic walks, outdoor activities, photography, waterfront dining'
            }
        }
        
        return neighborhoods
    
    def _generate_attractions(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate attraction information"""
        
        attractions = {
            'Main Landmark': {
                'description': f'The most iconic landmark of {city}, representing the city\'s character and history.',
                'category': 'Historic/Cultural',
                'tips': 'Visit early morning or late afternoon for the best lighting and fewer crowds.'
            },
            'Cultural Museum': {
                'description': f'Premier museum in {city} showcasing local history, art, and culture.',
                'category': 'Museum/Education',
                'tips': 'Allow 2-3 hours for a comprehensive visit. Check for special exhibitions.'
            },
            'Scenic Viewpoint': {
                'description': f'Best viewpoint in {city} offering panoramic views of the city and surrounding landscape.',
                'category': 'Scenic/Recreation',
                'tips': 'Perfect for sunset photos. Bring a camera and comfortable walking shoes.'
            }
        }
        
        return attractions
    
    def _generate_dining(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate dining information"""
        
        dining = {
            'Local Specialty Restaurant': {
                'description': f'Authentic restaurant serving traditional cuisine from {region}.',
                'cuisine_type': 'Regional',
                'price_range': '$$'
            },
            'Fine Dining': {
                'description': f'Upscale restaurant in {city} offering gourmet cuisine and excellent service.',
                'cuisine_type': 'Contemporary',
                'price_range': '$$$-$$$$'
            },
            'Casual Dining': {
                'description': f'Popular local spot in {city} known for great food and friendly atmosphere.',
                'cuisine_type': 'International',
                'price_range': '$-$$'
            }
        }
        
        return dining
    
    def _generate_nightlife(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate nightlife information"""
        
        nightlife = {
            'Main Entertainment District': {
                'description': f'The primary entertainment area of {city} with bars, clubs, and live music.',
                'type': 'Entertainment District',
                'atmosphere': 'Lively, diverse crowd, mix of venues'
            },
            'Local Bar': {
                'description': f'Popular local bar in {city} with great drinks and authentic atmosphere.',
                'type': 'Bar/Pub',
                'atmosphere': 'Casual, friendly, local crowd'
            }
        }
        
        return nightlife
    
    def _generate_shopping(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate shopping information"""
        
        shopping = {
            'Main Shopping Area': {
                'description': f'Primary shopping district in {city} with a mix of local and international brands.',
                'specialty': 'Mixed retail, souvenirs, local products',
                'price_range': '$-$$$'
            },
            'Local Market': {
                'description': f'Traditional market in {city} featuring local crafts, foods, and unique items.',
                'specialty': 'Local crafts, fresh produce, authentic souvenirs',
                'price_range': '$-$$'
            }
        }
        
        return shopping
    
    def _generate_transportation(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate transportation information"""
        
        transportation = {
            'Public Transit': {
                'description': f'Public transportation system in {city} including buses and local transit.',
                'cost': 'Varies by distance',
                'tips': 'Purchase day passes for multiple trips. Download local transit apps.'
            },
            'Taxi/Rideshare': {
                'description': f'Taxi and rideshare services available throughout {city}.',
                'cost': 'Meter-based or app pricing',
                'tips': 'Use official taxi services or popular rideshare apps for safety and reliability.'
            },
            'Walking/Biking': {
                'description': f'Pedestrian-friendly areas and bike rentals available in {city}.',
                'cost': 'Free walking, bike rentals vary',
                'tips': 'Many attractions are within walking distance. Ask about bike rental programs.'
            }
        }
        
        return transportation
    
    def _generate_accommodation(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate accommodation information"""
        
        accommodation = {
            'Luxury Hotel': {
                'description': f'Premium hotel in {city} offering luxury amenities and superior service.',
                'area': 'City Center',
                'price_range': '$$$-$$$$'
            },
            'Boutique Hotel': {
                'description': f'Charming boutique hotel in {city} with unique character and personalized service.',
                'area': 'Historic District',
                'price_range': '$$-$$$'
            },
            'Budget-Friendly': {
                'description': f'Affordable accommodation options in {city} for budget-conscious travelers.',
                'area': 'Various locations',
                'price_range': '$-$$'
            }
        }
        
        return accommodation
    
    def _generate_seasonal_guide(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate seasonal guide information"""
        
        seasonal_guide = {
            'Peak Season': {
                'weather': 'Pleasant weather ideal for outdoor activities and sightseeing',
                'activities': 'All attractions open, festivals, outdoor events',
                'events': 'Local festivals, cultural events, seasonal celebrations'
            },
            'Off Season': {
                'weather': 'Cooler temperatures, fewer crowds, authentic local atmosphere',
                'activities': 'Indoor attractions, cultural sites, local experiences',
                'events': 'Local community events, seasonal markets'
            }
        }
        
        return seasonal_guide
    
    def _generate_practical_info(self, city: str, region: str, country: str, language: str) -> Dict[str, Any]:
        """Generate practical information"""
        
        practical_info = {
            'Language': {
                'details': f'Primary language in {city} with English commonly understood in tourist areas',
                'tips': 'Learn basic phrases in the local language for better interactions'
            },
            'Currency': {
                'details': f'Local currency used in {country}',
                'tips': 'Exchange money at banks or official exchange offices for best rates'
            },
            'Tipping': {
                'details': 'Tipping customs vary by service and location',
                'tips': 'Ask locals or hotel staff about appropriate tipping practices'
            },
            'Safety': {
                'details': f'{city} is generally safe for tourists with standard precautions',
                'tips': 'Stay aware of surroundings, keep valuables secure, use reputable transportation'
            }
        }
        
        return practical_info
    
    def _generate_golf_summary(self, city: str, region: str, country: str, language: str) -> str:
        """Generate golf summary"""
        
        golf_summary = f"{city} offers excellent golf experiences with courses that showcase the natural beauty of {region}. Golf enthusiasts can enjoy challenging layouts, scenic views, and well-maintained facilities. The region's unique landscape provides memorable golfing opportunities for players of all skill levels.\n\n<a href=\"#\" class=\"golf-link\">Explore {city}'s golf courses →</a>"
        
        return golf_summary
    
    def _create_guide(self, destination: Destination, language: str, guide_data: Dict[str, Any]) -> CityGuide:
        """Create a new city guide"""
        
        guide = CityGuide(
            destination=destination,
            language_code=language,
            **guide_data
        )
        guide.save()
        return guide
    
    def _update_guide(self, guide: CityGuide, guide_data: Dict[str, Any]) -> None:
        """Update existing city guide"""
        
        for key, value in guide_data.items():
            setattr(guide, key, value)
        guide.save()
    
    def bulk_generate_guides(self, destination_ids: List[int] = None, 
                           languages: List[str] = None, 
                           force_regenerate: bool = False) -> Dict[str, int]:
        """
        Generate city guides for multiple destinations and languages
        
        Args:
            destination_ids: List of destination IDs to generate guides for
            languages: List of language codes to generate guides in
            force_regenerate: Whether to regenerate existing guides
            
        Returns:
            Dictionary with generation statistics
        """
        
        if languages is None:
            languages = ['en']  # Default to English only
        
        if destination_ids is None:
            destinations = Destination.objects.all()
        else:
            destinations = Destination.objects.filter(id__in=destination_ids)
        
        stats = {
            'total_destinations': destinations.count(),
            'total_languages': len(languages),
            'guides_created': 0,
            'guides_updated': 0,
            'guides_skipped': 0,
            'errors': 0
        }
        
        print(f"🚀 Starting bulk generation for {stats['total_destinations']} destinations in {stats['total_languages']} languages")
        
        for destination in destinations:
            for language in languages:
                try:
                    existing_guide = CityGuide.objects.filter(
                        destination=destination,
                        language_code=language
                    ).first()
                    
                    if existing_guide and not force_regenerate:
                        stats['guides_skipped'] += 1
                        continue
                    
                    guide = self.generate_city_guide(destination, language, force_regenerate)
                    
                    if guide:
                        if existing_guide:
                            stats['guides_updated'] += 1
                        else:
                            stats['guides_created'] += 1
                    else:
                        stats['errors'] += 1
                        
                except Exception as e:
                    print(f"❌ Error processing {destination.city} ({language}): {e}")
                    stats['errors'] += 1
        
        print(f"\n📊 Generation Complete:")
        print(f"   Created: {stats['guides_created']}")
        print(f"   Updated: {stats['guides_updated']}")
        print(f"   Skipped: {stats['guides_skipped']}")
        print(f"   Errors: {stats['errors']}")
        
        return stats

def main():
    """Main function to run the city guide generator"""
    
    generator = CityGuideGenerator()
    
    print("🌍 CityGuide Content Generator")
    print("=" * 40)
    
    # Get user input
    print("\nOptions:")
    print("1. Generate guides for specific destinations")
    print("2. Generate guides for all destinations")
    print("3. Generate guides in multiple languages")
    print("4. Regenerate existing guides")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        # Generate for specific destinations
        destination_ids = input("Enter destination IDs (comma-separated): ").strip()
        if destination_ids:
            destination_ids = [int(id.strip()) for id in destination_ids.split(',')]
        else:
            destination_ids = None
        
        language = input("Enter language code (default: en): ").strip() or 'en'
        
        generator.bulk_generate_guides(
            destination_ids=destination_ids,
            languages=[language],
            force_regenerate=False
        )
    
    elif choice == '2':
        # Generate for all destinations
        language = input("Enter language code (default: en): ").strip() or 'en'
        
        generator.bulk_generate_guides(
            languages=[language],
            force_regenerate=False
        )
    
    elif choice == '3':
        # Generate in multiple languages
        languages = input("Enter language codes (comma-separated, default: en): ").strip()
        if languages:
            languages = [lang.strip() for lang in languages.split(',')]
        else:
            languages = ['en']
        
        generator.bulk_generate_guides(
            languages=languages,
            force_regenerate=False
        )
    
    elif choice == '4':
        # Regenerate existing guides
        language = input("Enter language code (default: en): ").strip() or 'en'
        
        generator.bulk_generate_guides(
            languages=[language],
            force_regenerate=True
        )
    
    else:
        print("Invalid choice. Generating English guides for first 5 destinations as demo...")
        
        # Demo: Generate English guides for first 5 destinations
        first_5_destinations = list(Destination.objects.all()[:5].values_list('id', flat=True))
        
        generator.bulk_generate_guides(
            destination_ids=first_5_destinations,
            languages=['en'],
            force_regenerate=False
        )

if __name__ == "__main__":
    main()
