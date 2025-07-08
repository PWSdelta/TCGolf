#!/usr/bin/env python
"""
Create mock CityGuide data for testing
"""
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

def create_mock_cityguide():
    """Create a comprehensive mock CityGuide for Miami"""
    
    # Create or get Miami destination
    miami_dest, created = Destination.objects.get_or_create(
        city='Miami',
        region_or_state='Florida',
        country='United States',
        defaults={
            'name': 'Miami Golf Resort',
            'description': 'Premium golf destination in Miami, Florida',
            'latitude': 25.7617,
            'longitude': -80.1918,
            'image_url': 'https://example.com/miami-golf.jpg',
        }
    )
    
    if created:
        print(f"Created new destination: {miami_dest}")
    else:
        print(f"Using existing destination: {miami_dest}")
    
    # Create or update Miami CityGuide
    city_guide, created = CityGuide.objects.get_or_create(
        destination=miami_dest,
        language_code='en',
        defaults={
            'overview': """Miami is a vibrant international city known for its stunning beaches, Art Deco architecture, world-class dining, and pulsating nightlife. This sun-soaked metropolis offers the perfect blend of Latin American culture, coastal luxury, and urban sophistication. From the colorful streets of Little Havana to the glamorous shores of South Beach, Miami delivers an unforgettable experience for travelers seeking both relaxation and excitement.""",
            
            'neighborhoods': {
                'South Beach': {
                    'description': 'Iconic beachfront district famous for Art Deco architecture, trendy hotels, and vibrant nightlife.',
                    'highlights': ['Ocean Drive', 'Lincoln Road', 'Art Deco Historic District', 'Lummus Park Beach'],
                    'best_for': 'Nightlife, beach activities, shopping, dining'
                },
                'Little Havana': {
                    'description': 'Cultural heart of Miami\'s Cuban community with authentic cuisine, music, and traditions.',
                    'highlights': ['Calle Ocho', 'Domino Park', 'Versailles Restaurant', 'Cuban Memorial Boulevard'],
                    'best_for': 'Cultural experiences, authentic Cuban food, live music'
                },
                'Wynwood': {
                    'description': 'Trendy arts district featuring colorful murals, galleries, and hip restaurants.',
                    'highlights': ['Wynwood Walls', 'Wynwood Art Walk', 'Craft breweries', 'Street art tours'],
                    'best_for': 'Art enthusiasts, Instagram photos, craft beer, creative dining'
                },
                'Brickell': {
                    'description': 'Modern financial district with luxury condos, upscale shopping, and fine dining.',
                    'highlights': ['Brickell City Centre', 'Mary Brickell Village', 'Brickell Key', 'Rooftop bars'],
                    'best_for': 'Luxury shopping, fine dining, business travelers, modern architecture'
                },
                'Coconut Grove': {
                    'description': 'Bohemian neighborhood with lush greenery, waterfront views, and laid-back atmosphere.',
                    'highlights': ['CocoWalk', 'Vizcaya Museum', 'Peacock Park', 'Sailing clubs'],
                    'best_for': 'Families, outdoor activities, cultural attractions, waterfront dining'
                },
                'Design District': {
                    'description': 'Luxury shopping and design hub with high-end boutiques and contemporary architecture.',
                    'highlights': ['Miami Design District', 'Luxury flagship stores', 'Design galleries', 'Institute of Contemporary Art'],
                    'best_for': 'Luxury shopping, design enthusiasts, contemporary art'
                }
            },
            
            'attractions': {
                'Art Deco Historic District': {
                    'description': 'World\'s largest collection of Art Deco architecture with over 800 preserved buildings.',
                    'category': 'Architecture/History',
                    'tips': 'Take a guided walking tour to learn about the history and architectural details.'
                },
                'Vizcaya Museum and Gardens': {
                    'description': 'Stunning Italian Renaissance-style villa with elaborate gardens and art collections.',
                    'category': 'Museum/Gardens',
                    'tips': 'Visit in the morning for better lighting and fewer crowds. Allow 2-3 hours.'
                },
                'Wynwood Walls': {
                    'description': 'Outdoor street art museum featuring large-scale murals by international artists.',
                    'category': 'Art/Culture',
                    'tips': 'Visit during Wynwood Art Walk (second Saturday of each month) for galleries and events.'
                },
                'Bayside Marketplace': {
                    'description': 'Waterfront shopping and entertainment complex with boat tours and live music.',
                    'category': 'Shopping/Entertainment',
                    'tips': 'Great starting point for boat tours to see Miami from the water.'
                },
                'Miami Beach Boardwalk': {
                    'description': 'Scenic 2.5-mile walkway along the Atlantic Ocean connecting South Beach to Mid-Beach.',
                    'category': 'Recreation/Beach',
                    'tips': 'Perfect for morning jogs, sunset walks, or bike rides. Rent bikes nearby.'
                },
                'Pérez Art Museum Miami': {
                    'description': 'Contemporary art museum with international modern and contemporary works.',
                    'category': 'Museum/Art',
                    'tips': 'Free admission for Miami-Dade residents and active military with ID.'
                }
            },
            
            'dining': {
                'Joe\'s Stone Crab': {
                    'description': 'Miami Beach institution famous for stone crab claws and Key lime pie since 1913.',
                    'cuisine_type': 'Seafood',
                    'price_range': '$$$'
                },
                'Versailles Restaurant': {
                    'description': 'Iconic Cuban restaurant in Little Havana serving authentic Cuban cuisine.',
                    'cuisine_type': 'Cuban',
                    'price_range': '$$'
                },
                'Zuma Miami': {
                    'description': 'Upscale Japanese restaurant with contemporary robatayaki cuisine and waterfront views.',
                    'cuisine_type': 'Japanese',
                    'price_range': '$$$$'
                },
                'Yardbird': {
                    'description': 'Southern comfort food with a modern twist, famous for fried chicken and biscuits.',
                    'cuisine_type': 'Southern American',
                    'price_range': '$$$'
                },
                'La Carreta': {
                    'description': 'Popular 24-hour Cuban chain serving generous portions of traditional dishes.',
                    'cuisine_type': 'Cuban',
                    'price_range': '$'
                },
                'Stubborn Seed': {
                    'description': 'Michelin-starred restaurant offering innovative American cuisine with global influences.',
                    'cuisine_type': 'Modern American',
                    'price_range': '$$$$'
                }
            },
            
            'nightlife': {
                'LIV': {
                    'description': 'World-famous nightclub at the Fontainebleau hotel with international DJs and celebrities.',
                    'type': 'Nightclub',
                    'atmosphere': 'High-energy, upscale, celebrity hotspot'
                },
                'Story': {
                    'description': 'Multi-level nightclub in South Beach with state-of-the-art sound and lighting systems.',
                    'type': 'Nightclub',
                    'atmosphere': 'Electronic music, young crowd, high-energy'
                },
                'Ball & Chain': {
                    'description': 'Historic Little Havana bar with live Latin music, dancing, and classic cocktails.',
                    'type': 'Live Music Bar',
                    'atmosphere': 'Authentic Cuban, live salsa, intimate setting'
                },
                'Mango\'s Tropical Cafe': {
                    'description': 'Iconic South Beach spot with live Latin music, dancing, and entertainment.',
                    'type': 'Restaurant/Bar',
                    'atmosphere': 'Tropical, lively, tourist-friendly'
                },
                'Sugar': {
                    'description': 'Rooftop bar and garden in Brickell with panoramic city views and craft cocktails.',
                    'type': 'Rooftop Bar',
                    'atmosphere': 'Sophisticated, scenic views, upscale'
                },
                'Nikki Beach': {
                    'description': 'Beachfront club with day parties, dining, and music in a luxurious setting.',
                    'type': 'Beach Club',
                    'atmosphere': 'Beachfront luxury, day parties, international crowd'
                }
            },
            
            'shopping': {
                'Lincoln Road Mall': {
                    'description': 'Pedestrian-only shopping street with international brands, local boutiques, and outdoor cafes.',
                    'specialty': 'Mixed retail, dining, people-watching',
                    'price_range': '$-$$$'
                },
                'Aventura Mall': {
                    'description': 'Upscale shopping center with luxury brands, department stores, and dining options.',
                    'specialty': 'Luxury shopping, department stores',
                    'price_range': '$$-$$$$'
                },
                'Bayside Marketplace': {
                    'description': 'Waterfront shopping complex with souvenir shops, local vendors, and boat tours.',
                    'specialty': 'Souvenirs, local crafts, waterfront dining',
                    'price_range': '$-$$'
                },
                'Miami Design District': {
                    'description': 'Luxury shopping district with flagship stores, designer boutiques, and art galleries.',
                    'specialty': 'Luxury fashion, design, contemporary art',
                    'price_range': '$$$-$$$$'
                },
                'Espanola Way': {
                    'description': 'Charming pedestrian street with unique shops, cafes, and Mediterranean architecture.',
                    'specialty': 'Local boutiques, artisanal goods, cafes',
                    'price_range': '$$-$$$'
                }
            },
            
            'transportation': {
                'Metromover': {
                    'description': 'Free automated transit system connecting downtown Miami and Brickell.',
                    'cost': 'Free',
                    'tips': 'Great for getting around downtown and Brickell area quickly.'
                },
                'Metrobus': {
                    'description': 'Comprehensive bus system serving Miami-Dade County with multiple routes.',
                    'cost': '$2.25 per ride',
                    'tips': 'Purchase a EASY Card for convenient payment and transfers.'
                },
                'Ride-sharing': {
                    'description': 'Uber and Lyft are widely available throughout Miami.',
                    'cost': 'Variable by distance',
                    'tips': 'Surge pricing common during peak hours and events.'
                },
                'Car Rental': {
                    'description': 'Recommended for exploring beyond Miami Beach and downtown areas.',
                    'cost': '$30-80+ per day',
                    'tips': 'Parking can be expensive in South Beach. Consider hotel valet or public garages.'
                },
                'Citi Bike Miami': {
                    'description': 'Bike-sharing system with stations throughout Miami Beach and downtown.',
                    'cost': '$15 per day',
                    'tips': 'Perfect for short trips and exploring the beach area.'
                }
            },
            
            'accommodation': {
                'The Fontainebleau': {
                    'description': 'Iconic luxury resort on Miami Beach with pools, spa, dining, and nightlife.',
                    'area': 'Mid-Beach',
                    'price_range': '$$$-$$$$'
                },
                'The Setai': {
                    'description': 'Ultra-luxury beachfront hotel with Art Deco elegance and world-class service.',
                    'area': 'South Beach',
                    'price_range': '$$$$'
                },
                'W South Beach': {
                    'description': 'Trendy beachfront hotel with contemporary design and vibrant nightlife.',
                    'area': 'South Beach',
                    'price_range': '$$$'
                },
                'Four Seasons Miami': {
                    'description': 'Luxury downtown hotel with skyline views and high-end amenities.',
                    'area': 'Brickell',
                    'price_range': '$$$$'
                },
                'The Confidante': {
                    'description': 'Boutique beachfront hotel with mid-century modern design and rooftop pool.',
                    'area': 'Mid-Beach',
                    'price_range': '$$$'
                }
            },
            
            'seasonal_guide': {
                'Winter (Dec-Feb)': {
                    'weather': 'Perfect weather with temperatures 70-80°F, low humidity, minimal rain',
                    'activities': 'Peak tourist season, outdoor activities, beach time, festivals',
                    'events': 'Art Basel Miami Beach, Miami International Boat Show, Winter Music Conference'
                },
                'Spring (Mar-May)': {
                    'weather': 'Warm and pleasant, 75-85°F, moderate humidity, occasional showers',
                    'activities': 'Great for outdoor activities, less crowded beaches, golf',
                    'events': 'Ultra Music Festival, Miami Open tennis, Spring Break activities'
                },
                'Summer (Jun-Aug)': {
                    'weather': 'Hot and humid, 85-95°F, frequent afternoon thunderstorms',
                    'activities': 'Beach activities, indoor attractions, pool parties, early morning/evening outdoor activities',
                    'events': 'Summer festival season, pool parties, outdoor concerts'
                },
                'Fall (Sep-Nov)': {
                    'weather': 'Warm with decreasing humidity, 75-85°F, hurricane season concerns',
                    'activities': 'Fewer crowds, good weather for activities, hurricane season awareness',
                    'events': 'Miami Fashion Week, food festivals, cultural events'
                }
            },
            
            'practical_info': {
                'Language': {
                    'details': 'English and Spanish are widely spoken',
                    'tips': 'Basic Spanish phrases helpful in Little Havana and some areas'
                },
                'Currency': {
                    'details': 'US Dollar (USD)',
                    'tips': 'Credit cards widely accepted, cash useful for tips and street vendors'
                },
                'Tipping': {
                    'details': 'Standard US tipping: 18-20% restaurants, $1-2 per drink, 15-20% taxi/rideshare',
                    'tips': 'Valet parking typically $5-10, hotel housekeeping $2-5 per day'
                },
                'Safety': {
                    'details': 'Generally safe in tourist areas, use normal urban precautions',
                    'tips': 'Stay aware of surroundings, avoid displaying expensive items, use reputable transportation'
                },
                'Best Time to Visit': {
                    'details': 'November through April for best weather and fewer crowds',
                    'tips': 'Summer offers lower prices but hot, humid weather and potential storms'
                },
                'Getting There': {
                    'details': 'Miami International Airport (MIA) is the main gateway',
                    'tips': 'Airport is about 8 miles from downtown, 30-45 minutes by car depending on traffic'
                }
            },
            
            'golf_summary': """Miami offers world-class golf experiences with year-round playing conditions. The area features championship courses designed by legendary architects like Jack Nicklaus and Greg Norman. From tropical resort courses to exclusive private clubs, Miami's golf scene caters to all skill levels. Many courses offer stunning water views and unique challenges incorporating the natural landscape. 

<a href="#" class="golf-link">Explore Miami's complete golf guide →</a>""",
            
            'meta_description': 'Discover Miami: Ultimate city guide covering neighborhoods, attractions, dining, nightlife, and travel tips for the Magic City.',
            
            'is_published': True,
            'is_featured': True,
        }
    )
    
    if created:
        print(f"Created new CityGuide: {city_guide}")
    else:
        print(f"Updated existing CityGuide: {city_guide}")
        # Update the existing guide with our comprehensive data
        city_guide.overview = """Miami is a vibrant international city known for its stunning beaches, Art Deco architecture, world-class dining, and pulsating nightlife. This sun-soaked metropolis offers the perfect blend of Latin American culture, coastal luxury, and urban sophistication. From the colorful streets of Little Havana to the glamorous shores of South Beach, Miami delivers an unforgettable experience for travelers seeking both relaxation and excitement."""
        
        # Update all the JSON fields as defined above
        city_guide.neighborhoods = {
            'South Beach': {
                'description': 'Iconic beachfront district famous for Art Deco architecture, trendy hotels, and vibrant nightlife.',
                'highlights': ['Ocean Drive', 'Lincoln Road', 'Art Deco Historic District', 'Lummus Park Beach'],
                'best_for': 'Nightlife, beach activities, shopping, dining'
            },
            'Little Havana': {
                'description': 'Cultural heart of Miami\'s Cuban community with authentic cuisine, music, and traditions.',
                'highlights': ['Calle Ocho', 'Domino Park', 'Versailles Restaurant', 'Cuban Memorial Boulevard'],
                'best_for': 'Cultural experiences, authentic Cuban food, live music'
            },
            'Wynwood': {
                'description': 'Trendy arts district featuring colorful murals, galleries, and hip restaurants.',
                'highlights': ['Wynwood Walls', 'Wynwood Art Walk', 'Craft breweries', 'Street art tours'],
                'best_for': 'Art enthusiasts, Instagram photos, craft beer, creative dining'
            },
            'Brickell': {
                'description': 'Modern financial district with luxury condos, upscale shopping, and fine dining.',
                'highlights': ['Brickell City Centre', 'Mary Brickell Village', 'Brickell Key', 'Rooftop bars'],
                'best_for': 'Luxury shopping, fine dining, business travelers, modern architecture'
            },
            'Coconut Grove': {
                'description': 'Bohemian neighborhood with lush greenery, waterfront views, and laid-back atmosphere.',
                'highlights': ['CocoWalk', 'Vizcaya Museum', 'Peacock Park', 'Sailing clubs'],
                'best_for': 'Families, outdoor activities, cultural attractions, waterfront dining'
            },
            'Design District': {
                'description': 'Luxury shopping and design hub with high-end boutiques and contemporary architecture.',
                'highlights': ['Miami Design District', 'Luxury flagship stores', 'Design galleries', 'Institute of Contemporary Art'],
                'best_for': 'Luxury shopping, design enthusiasts, contemporary art'
            }
        }
        
        city_guide.save()
        print(f"Updated CityGuide with comprehensive data")
    
    print(f"\nCityGuide Details:")
    print(f"URL: {city_guide.get_absolute_url()}")
    print(f"Word Count: {city_guide.word_count}")
    print(f"Reading Time: {city_guide.get_reading_time()} minutes")
    print(f"Sections: {', '.join(city_guide.get_sections_summary())}")
    
    return city_guide

if __name__ == "__main__":
    try:
        guide = create_mock_cityguide()
        print("\n✅ Successfully created mock CityGuide!")
    except Exception as e:
        print(f"❌ Error creating mock data: {e}")
        import traceback
        traceback.print_exc()
