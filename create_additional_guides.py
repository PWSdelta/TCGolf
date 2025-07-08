#!/usr/bin/env python
"""
Create additional mock CityGuide data for testing
"""
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

def create_additional_guides():
    """Create additional mock CityGuides for variety"""
    
    # Create Las Vegas destination and guide
    vegas_dest, created = Destination.objects.get_or_create(
        city='Las Vegas',
        region_or_state='Nevada',
        country='United States',
        defaults={
            'name': 'Las Vegas Golf Club',
            'description': 'World-class golf in the entertainment capital',
            'latitude': 36.1699,
            'longitude': -115.1398,
            'image_url': 'https://example.com/vegas-golf.jpg',
        }
    )
    
    vegas_guide, created = CityGuide.objects.get_or_create(
        destination=vegas_dest,
        language_code='en',
        defaults={
            'overview': """Las Vegas is the entertainment capital of the world, where luxury meets excitement in a desert oasis. Beyond the famous Strip, this vibrant city offers world-class dining, spectacular shows, championship golf courses, and unique desert experiences. From high-end shopping to thrilling nightlife, Las Vegas delivers unforgettable experiences 24/7.""",
            
            'neighborhoods': {
                'The Strip': {
                    'description': 'Iconic 4.2-mile stretch of Las Vegas Boulevard with world-famous casinos, hotels, and entertainment.',
                    'highlights': ['Bellagio Fountains', 'High Roller Observation Wheel', 'Forum Shops', 'Fremont Street Experience'],
                    'best_for': 'First-time visitors, shows, gambling, luxury shopping'
                },
                'Downtown Las Vegas': {
                    'description': 'Historic core of Las Vegas with vintage casinos, the famous Fremont Street, and emerging arts district.',
                    'highlights': ['Fremont Street Experience', 'Neon Museum', 'Arts District', 'Container Park'],
                    'best_for': 'History buffs, authentic Vegas experience, arts and culture'
                },
                'Summerlin': {
                    'description': 'Upscale master-planned community with golf courses, shopping, and dining.',
                    'highlights': ['Red Rock Canyon', 'Downtown Summerlin', 'TPC Las Vegas', 'Trails and parks'],
                    'best_for': 'Outdoor activities, golf, family-friendly attractions'
                }
            },
            
            'attractions': {
                'Bellagio Fountains': {
                    'description': 'Iconic water show with choreographed fountains set to music.',
                    'category': 'Entertainment',
                    'tips': 'Best viewed from the Bellagio terrace or across the street for photos.'
                },
                'High Roller': {
                    'description': 'World\'s largest observation wheel offering 360-degree views of Las Vegas.',
                    'category': 'Observation/Entertainment',
                    'tips': 'Book sunset rides for the best views and photos.'
                },
                'Red Rock Canyon': {
                    'description': 'Stunning desert landscape with hiking trails and scenic drives.',
                    'category': 'Nature/Recreation',
                    'tips': 'Visit early morning or late afternoon to avoid heat and crowds.'
                }
            },
            
            'dining': {
                'Joël Robuchon': {
                    'description': 'Three-Michelin-starred French restaurant offering exquisite fine dining.',
                    'cuisine_type': 'French',
                    'price_range': '$$$$'
                },
                'Lotus of Siam': {
                    'description': 'Award-winning Thai restaurant known for authentic Northern Thai cuisine.',
                    'cuisine_type': 'Thai',
                    'price_range': '$$'
                },
                'In-N-Out Burger': {
                    'description': 'California-based burger chain famous for fresh ingredients and secret menu.',
                    'cuisine_type': 'American',
                    'price_range': '$'
                }
            },
            
            'nightlife': {
                'Omnia': {
                    'description': 'Ultra-modern nightclub with world-class DJs and stunning visual effects.',
                    'type': 'Nightclub',
                    'atmosphere': 'High-energy, electronic music, VIP experience'
                },
                'Fremont Street Experience': {
                    'description': 'Outdoor entertainment district with live music, street performers, and LED canopy.',
                    'type': 'Entertainment District',
                    'atmosphere': 'Casual, diverse crowd, vintage Vegas charm'
                }
            },
            
            'shopping': {
                'Forum Shops at Caesars': {
                    'description': 'Luxury shopping mall with high-end brands and unique architecture.',
                    'specialty': 'Luxury fashion, jewelry, entertainment',
                    'price_range': '$$$-$$$$'
                },
                'Grand Canal Shoppes': {
                    'description': 'Venetian-themed shopping center with gondola rides and street performers.',
                    'specialty': 'Mixed retail, dining, entertainment',
                    'price_range': '$$-$$$'
                }
            },
            
            'transportation': {
                'Monorail': {
                    'description': 'Elevated train system connecting major Strip hotels and convention center.',
                    'cost': '$13-15 per day',
                    'tips': 'Most convenient for Strip travel, but limited stops.'
                },
                'Rideshare': {
                    'description': 'Uber and Lyft widely available with designated pickup areas.',
                    'cost': 'Variable',
                    'tips': 'Use designated rideshare pickup zones to avoid confusion.'
                }
            },
            
            'accommodation': {
                'Bellagio': {
                    'description': 'Luxury resort with iconic fountains, fine dining, and elegant rooms.',
                    'area': 'Las Vegas Strip',
                    'price_range': '$$$-$$$$'
                },
                'The Venetian': {
                    'description': 'All-suite hotel with Italian-inspired architecture and gondola rides.',
                    'area': 'Las Vegas Strip',
                    'price_range': '$$$'
                }
            },
            
            'seasonal_guide': {
                'Winter (Dec-Feb)': {
                    'weather': 'Cool and pleasant, 45-65°F, perfect for outdoor activities',
                    'activities': 'Peak season for golf, hiking, outdoor dining',
                    'events': 'CES, Winter festivals, holiday shows'
                },
                'Summer (Jun-Aug)': {
                    'weather': 'Very hot, 85-110°F, mostly indoor activities recommended',
                    'activities': 'Pool parties, indoor attractions, air-conditioned venues',
                    'events': 'Summer residencies, pool club events'
                }
            },
            
            'practical_info': {
                'Tipping': {
                    'details': 'Tipping is expected: 15-20% restaurants, $1-2 per drink, $5-10 valet',
                    'tips': 'Cocktail servers, dealers, and hotel staff rely on tips'
                },
                'Gambling': {
                    'details': 'Must be 21+, casinos are smoke-free in some areas',
                    'tips': 'Set limits, learn basic rules, join players clubs for comps'
                }
            },
            
            'golf_summary': """Las Vegas offers some of the most spectacular golf experiences in the world, with courses designed by legends like Jack Nicklaus and Pete Dye. The desert landscape provides dramatic backdrops with stunning mountain views. Many courses feature unique desert landscaping and challenging layouts that test golfers of all skill levels.

<a href="#" class="golf-link">Discover Las Vegas golf courses →</a>""",
            
            'meta_description': 'Complete Las Vegas travel guide: attractions, dining, nightlife, shopping, and insider tips for the Entertainment Capital.',
            'is_published': True,
            'is_featured': True,
        }
    )
    
    # Create New York destination and guide
    ny_dest, created = Destination.objects.get_or_create(
        city='New York',
        region_or_state='New York',
        country='United States',
        defaults={
            'name': 'New York Golf Club',
            'description': 'Golf experiences in the Big Apple',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'image_url': 'https://example.com/ny-golf.jpg',
        }
    )
    
    ny_guide, created = CityGuide.objects.get_or_create(
        destination=ny_dest,
        language_code='en',
        defaults={
            'overview': """New York City is the ultimate urban playground, where towering skyscrapers meet world-class culture, cuisine, and entertainment. From the bright lights of Times Square to the tranquil paths of Central Park, NYC offers endless possibilities. This city never sleeps, providing 24/7 excitement with Broadway shows, world-renowned museums, diverse neighborhoods, and culinary adventures from every corner of the globe.""",
            
            'neighborhoods': {
                'Manhattan': {
                    'description': 'The heart of NYC with iconic landmarks, Broadway, and bustling streets.',
                    'highlights': ['Times Square', 'Central Park', 'Empire State Building', 'Broadway theaters'],
                    'best_for': 'First-time visitors, business travelers, theater enthusiasts'
                },
                'Brooklyn': {
                    'description': 'Trendy borough with artisanal shops, hip restaurants, and stunning Manhattan views.',
                    'highlights': ['Brooklyn Bridge', 'DUMBO', 'Williamsburg', 'Prospect Park'],
                    'best_for': 'Local experiences, craft food scene, waterfront views'
                },
                'SoHo': {
                    'description': 'Chic neighborhood known for cast-iron architecture, high-end shopping, and art galleries.',
                    'highlights': ['Designer boutiques', 'Art galleries', 'Cast-iron buildings', 'Trendy restaurants'],
                    'best_for': 'Shopping, art lovers, architectural enthusiasts'
                }
            },
            
            'attractions': {
                'Statue of Liberty': {
                    'description': 'Iconic symbol of freedom and democracy, accessible by ferry from Battery Park.',
                    'category': 'Historic Monument',
                    'tips': 'Book tickets in advance, especially for crown access. Allow full day for visit.'
                },
                'Central Park': {
                    'description': '843-acre green oasis in Manhattan with lakes, trails, and recreational activities.',
                    'category': 'Park/Recreation',
                    'tips': 'Rent bikes, visit during different seasons, explore hidden gems like Bethesda Fountain.'
                },
                'Metropolitan Museum of Art': {
                    'description': 'World-class art museum with extensive collections spanning 5,000 years.',
                    'category': 'Museum/Art',
                    'tips': 'Suggested admission for NY residents, plan multiple visits, don\'t miss the rooftop garden.'
                }
            },
            
            'dining': {
                'Eleven Madison Park': {
                    'description': 'World-renowned fine dining restaurant with innovative plant-based cuisine.',
                    'cuisine_type': 'Contemporary American',
                    'price_range': '$$$$'
                },
                'Joe\'s Pizza': {
                    'description': 'Famous NYC pizza joint serving classic New York-style slices.',
                    'cuisine_type': 'Pizza',
                    'price_range': '$'
                },
                'Katz\'s Delicatessen': {
                    'description': 'Historic Jewish deli famous for pastrami sandwiches and classic NYC atmosphere.',
                    'cuisine_type': 'Deli',
                    'price_range': '$$'
                }
            },
            
            'nightlife': {
                'Broadway Shows': {
                    'description': 'World-class theater productions in the Theater District.',
                    'type': 'Theater',
                    'atmosphere': 'Elegant, cultural, diverse shows for all tastes'
                },
                'Rooftop Bars': {
                    'description': 'Sky-high venues with stunning city views and craft cocktails.',
                    'type': 'Rooftop Bars',
                    'atmosphere': 'Sophisticated, scenic, Instagram-worthy'
                }
            },
            
            'shopping': {
                'Fifth Avenue': {
                    'description': 'Luxury shopping corridor with flagship stores and designer boutiques.',
                    'specialty': 'Luxury fashion, jewelry, department stores',
                    'price_range': '$$$-$$$$'
                },
                'SoHo': {
                    'description': 'Trendy neighborhood with unique boutiques, vintage shops, and art galleries.',
                    'specialty': 'Independent brands, vintage, art',
                    'price_range': '$$-$$$'
                }
            },
            
            'transportation': {
                'Subway': {
                    'description': 'Extensive public transit system covering all five boroughs.',
                    'cost': '$2.90 per ride',
                    'tips': 'Get MetroCard or use contactless payment, avoid rush hours when possible.'
                },
                'Taxi/Rideshare': {
                    'description': 'Yellow cabs and rideshare services available throughout the city.',
                    'cost': 'Variable + tolls',
                    'tips': 'Walking is often faster for short distances, especially in midtown.'
                }
            },
            
            'accommodation': {
                'The Plaza': {
                    'description': 'Iconic luxury hotel overlooking Central Park with timeless elegance.',
                    'area': 'Midtown Manhattan',
                    'price_range': '$$$$'
                },
                'Pod Hotels': {
                    'description': 'Modern, efficient hotels with stylish small rooms and great locations.',
                    'area': 'Multiple locations',
                    'price_range': '$$'
                }
            },
            
            'seasonal_guide': {
                'Fall (Sep-Nov)': {
                    'weather': 'Crisp and beautiful, 50-70°F, perfect for walking',
                    'activities': 'Central Park foliage, outdoor dining, festivals',
                    'events': 'Fashion Week, Harvest festivals, holiday season begins'
                },
                'Winter (Dec-Feb)': {
                    'weather': 'Cold with potential snow, 30-45°F, dress warmly',
                    'activities': 'Ice skating, holiday displays, indoor attractions',
                    'events': 'Holiday markets, New Year\'s Eve, winter sales'
                }
            },
            
            'practical_info': {
                'Tipping': {
                    'details': 'Standard 18-20% restaurants, $1-2 per drink, 15-20% taxis',
                    'tips': 'Doormen, concierge, and housekeeping appreciate tips'
                },
                'Safety': {
                    'details': 'Generally safe in tourist areas, use standard urban precautions',
                    'tips': 'Stay aware of surroundings, avoid empty subway cars late at night'
                }
            },
            
            'golf_summary': """While NYC may not be known for golf, the surrounding area offers excellent courses with stunning views. From classic parkland layouts to modern designs, golfers can find challenging courses within reach of the city. Many courses offer unique urban backdrops and convenient access from Manhattan.

<a href="#" class="golf-link">Explore NYC area golf courses →</a>""",
            
            'meta_description': 'Ultimate New York City guide: attractions, dining, Broadway shows, neighborhoods, and insider tips for the Big Apple.',
            'is_published': True,
            'is_featured': False,
        }
    )
    
    print(f"Created/Updated Vegas guide: {vegas_guide}")
    print(f"Created/Updated NYC guide: {ny_guide}")
    
    # Create Spanish version of Miami guide for multilingual example
    miami_dest = Destination.objects.get(city='Miami')
    miami_es_guide, created = CityGuide.objects.get_or_create(
        destination=miami_dest,
        language_code='es',
        defaults={
            'overview': """Miami es una ciudad internacional vibrante conocida por sus hermosas playas, arquitectura Art Deco, gastronomía de clase mundial y vida nocturna pulsante. Esta metrópolis bañada por el sol ofrece la combinación perfecta de cultura latinoamericana, lujo costero y sofisticación urbana. Desde las coloridas calles de La Pequeña Habana hasta las glamorosas costas de South Beach, Miami ofrece una experiencia inolvidable.""",
            
            'neighborhoods': {
                'South Beach': {
                    'description': 'Distrito icónico frente al mar famoso por su arquitectura Art Deco, hoteles de moda y vida nocturna vibrante.',
                    'highlights': ['Ocean Drive', 'Lincoln Road', 'Distrito Histórico Art Deco', 'Playa Lummus Park'],
                    'best_for': 'Vida nocturna, actividades de playa, compras, gastronomía'
                },
                'La Pequeña Habana': {
                    'description': 'Corazón cultural de la comunidad cubana de Miami con auténtica comida, música y tradiciones.',
                    'highlights': ['Calle Ocho', 'Parque Dominó', 'Restaurante Versailles', 'Bulevar Memorial Cubano'],
                    'best_for': 'Experiencias culturales, comida cubana auténtica, música en vivo'
                }
            },
            
            'attractions': {
                'Distrito Histórico Art Deco': {
                    'description': 'La colección más grande del mundo de arquitectura Art Deco con más de 800 edificios preservados.',
                    'category': 'Arquitectura/Historia',
                    'tips': 'Toma un tour guiado para aprender sobre la historia y detalles arquitectónicos.'
                }
            },
            
            'dining': {
                'Versailles': {
                    'description': 'Restaurante cubano icónico en La Pequeña Habana que sirve auténtica cocina cubana.',
                    'cuisine_type': 'Cubana',
                    'price_range': '$$'
                }
            },
            
            'nightlife': {
                'LIV': {
                    'description': 'Discoteca mundialmente famosa en el hotel Fontainebleau con DJs internacionales.',
                    'type': 'Discoteca',
                    'atmosphere': 'Alta energía, elegante, punto de encuentro de celebridades'
                }
            },
            
            'shopping': {
                'Lincoln Road Mall': {
                    'description': 'Calle comercial peatonal con marcas internacionales y cafés al aire libre.',
                    'specialty': 'Comercio mixto, gastronomía, observación de gente',
                    'price_range': '$-$$$'
                }
            },
            
            'transportation': {
                'Metromover': {
                    'description': 'Sistema de tránsito automatizado gratuito que conecta el centro de Miami y Brickell.',
                    'cost': 'Gratis',
                    'tips': 'Excelente para moverse por el centro y área de Brickell rápidamente.'
                }
            },
            
            'accommodation': {
                'The Fontainebleau': {
                    'description': 'Resort de lujo icónico en Miami Beach con piscinas, spa y vida nocturna.',
                    'area': 'Mid-Beach',
                    'price_range': '$$$-$$$$'
                }
            },
            
            'seasonal_guide': {
                'Invierno (Dic-Feb)': {
                    'weather': 'Clima perfecto con temperaturas de 21-27°C, baja humedad, lluvia mínima',
                    'activities': 'Temporada alta turística, actividades al aire libre, tiempo de playa',
                    'events': 'Art Basel Miami Beach, Miami International Boat Show'
                }
            },
            
            'practical_info': {
                'Idioma': {
                    'details': 'Inglés y español son ampliamente hablados',
                    'tips': 'Frases básicas en español son útiles en La Pequeña Habana'
                }
            },
            
            'golf_summary': """Miami ofrece experiencias de golf de clase mundial con condiciones de juego durante todo el año. El área cuenta con campos de campeonato diseñados por arquitectos legendarios como Jack Nicklaus y Greg Norman.

<a href="#" class="golf-link">Explora la guía completa de golf de Miami →</a>""",
            
            'meta_description': 'Guía completa de Miami: vecindarios, atracciones, gastronomía, vida nocturna y consejos de viaje.',
            'is_published': True,
            'is_featured': False,
        }
    )
    
    print(f"Created/Updated Miami Spanish guide: {miami_es_guide}")
    
    # Print summary
    total_guides = CityGuide.objects.count()
    featured_guides = CityGuide.objects.filter(is_featured=True).count()
    languages = CityGuide.objects.values_list('language_code', flat=True).distinct()
    
    print(f"\n📊 Summary:")
    print(f"Total city guides: {total_guides}")
    print(f"Featured guides: {featured_guides}")
    print(f"Languages: {', '.join(languages)}")
    
    return total_guides

if __name__ == "__main__":
    try:
        count = create_additional_guides()
        print(f"\n✅ Successfully created/updated {count} city guides!")
    except Exception as e:
        print(f"❌ Error creating mock data: {e}")
        import traceback
        traceback.print_exc()
