#!/usr/bin/env python
"""
Add Golf Destination Cities

This script adds cities known for their golf scenes to reach 500+ total destinations.
Focus on cities with multiple golf courses and golf tourism.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination

# Golf destination CITIES (not individual courses)
NEW_GOLF_CITIES = [
    # UNITED STATES - Additional Golf Cities
    {"name": "Myrtle Beach Golf Destination", "city": "Myrtle Beach", "region_or_state": "South Carolina", "country": "USA", "description": "Golf capital of the world with 100+ courses", "latitude": 33.6891, "longitude": -78.8867},
    {"name": "Pinehurst Golf Destination", "city": "Pinehurst", "region_or_state": "North Carolina", "country": "USA", "description": "Historic golf resort town", "latitude": 35.1954, "longitude": -79.4689},
    {"name": "Scottsdale Golf Scene", "city": "Scottsdale", "region_or_state": "Arizona", "country": "USA", "description": "Desert golf paradise", "latitude": 33.4942, "longitude": -111.9261},
    {"name": "Palm Springs Golf", "city": "Palm Springs", "region_or_state": "California", "country": "USA", "description": "California desert golf destination", "latitude": 33.8303, "longitude": -116.5453},
    {"name": "Naples Golf", "city": "Naples", "region_or_state": "Florida", "country": "USA", "description": "Southwest Florida golf haven", "latitude": 26.1420, "longitude": -81.7948},
    {"name": "Hilton Head Golf", "city": "Hilton Head Island", "region_or_state": "South Carolina", "country": "USA", "description": "Lowcountry golf destination", "latitude": 32.2163, "longitude": -80.7526},
    {"name": "Williamsburg Golf", "city": "Williamsburg", "region_or_state": "Virginia", "country": "USA", "description": "Historic Virginia golf", "latitude": 37.2707, "longitude": -76.7075},
    {"name": "Branson Golf", "city": "Branson", "region_or_state": "Missouri", "country": "USA", "description": "Ozark mountain golf", "latitude": 36.6437, "longitude": -93.2185},
    {"name": "Ocean City Golf", "city": "Ocean City", "region_or_state": "Maryland", "country": "USA", "description": "Atlantic coast golf", "latitude": 38.3365, "longitude": -75.0849},
    {"name": "Virginia Beach Golf", "city": "Virginia Beach", "region_or_state": "Virginia", "country": "USA", "description": "Coastal Virginia golf", "latitude": 36.8529, "longitude": -75.9780},
    {"name": "Morgantown Golf", "city": "Morgantown", "region_or_state": "West Virginia", "country": "USA", "description": "Mountain golf in West Virginia", "latitude": 39.6295, "longitude": -79.9553},
    {"name": "Key West Golf", "city": "Key West", "region_or_state": "Florida", "country": "USA", "description": "Tropical Keys golf", "latitude": 24.5551, "longitude": -81.7800},
    {"name": "Traverse City Golf", "city": "Traverse City", "region_or_state": "Michigan", "country": "USA", "description": "Great Lakes golf destination", "latitude": 44.7631, "longitude": -85.6206},
    {"name": "Door County Golf", "city": "Sturgeon Bay", "region_or_state": "Wisconsin", "country": "USA", "description": "Wisconsin peninsula golf", "latitude": 44.8342, "longitude": -87.3770},
    {"name": "Lake Tahoe Golf", "city": "South Lake Tahoe", "region_or_state": "California", "country": "USA", "description": "Alpine lake golf", "latitude": 38.9399, "longitude": -119.9772},
    {"name": "Park City Golf", "city": "Park City", "region_or_state": "Utah", "country": "USA", "description": "Mountain resort golf", "latitude": 40.6461, "longitude": -111.4980},
    {"name": "Jackson Hole Golf", "city": "Jackson", "region_or_state": "Wyoming", "country": "USA", "description": "Rocky Mountain golf", "latitude": 43.4799, "longitude": -110.7624},
    {"name": "Bend Golf", "city": "Bend", "region_or_state": "Oregon", "country": "USA", "description": "Central Oregon golf", "latitude": 44.0582, "longitude": -121.3153},
    {"name": "Coeur d'Alene Golf", "city": "Coeur d'Alene", "region_or_state": "Idaho", "country": "USA", "description": "Idaho lake golf", "latitude": 47.6777, "longitude": -116.7804},
    {"name": "Sun Valley Golf", "city": "Sun Valley", "region_or_state": "Idaho", "country": "USA", "description": "Idaho mountain golf", "latitude": 43.6963, "longitude": -114.3576},
    
    # CANADA - Golf Cities
    {"name": "Whistler Golf", "city": "Whistler", "region_or_state": "British Columbia", "country": "Canada", "description": "Mountain resort golf", "latitude": 50.1163, "longitude": -122.9574},
    {"name": "Banff Golf", "city": "Banff", "region_or_state": "Alberta", "country": "Canada", "description": "Canadian Rockies golf", "latitude": 51.1784, "longitude": -115.5708},
    {"name": "Niagara Falls Golf", "city": "Niagara Falls", "region_or_state": "Ontario", "country": "Canada", "description": "Niagara region golf", "latitude": 43.0896, "longitude": -79.0849},
    {"name": "Charlottetown Golf", "city": "Charlottetown", "region_or_state": "Prince Edward Island", "country": "Canada", "description": "Prince Edward Island golf", "latitude": 46.2382, "longitude": -63.1311},
    {"name": "Muskoka Golf", "city": "Huntsville", "region_or_state": "Ontario", "country": "Canada", "description": "Ontario cottage country golf", "latitude": 45.3269, "longitude": -79.2186},
    
    # MEXICO - Golf Destinations
    {"name": "Cabo San Lucas Golf", "city": "Cabo San Lucas", "region_or_state": "Baja California Sur", "country": "Mexico", "description": "Baja peninsula golf", "latitude": 22.8905, "longitude": -109.9167},
    {"name": "Puerto Vallarta Golf", "city": "Puerto Vallarta", "region_or_state": "Jalisco", "country": "Mexico", "description": "Pacific coast golf", "latitude": 20.6534, "longitude": -105.2253},
    {"name": "Riviera Maya Golf", "city": "Playa del Carmen", "region_or_state": "Quintana Roo", "country": "Mexico", "description": "Caribbean coast golf", "latitude": 20.6296, "longitude": -87.0739},
    {"name": "Mazatlán Golf", "city": "Mazatlán", "region_or_state": "Sinaloa", "country": "Mexico", "description": "Pacific Mexico golf", "latitude": 23.2494, "longitude": -106.4103},
    {"name": "Acapulco Golf", "city": "Acapulco", "region_or_state": "Guerrero", "country": "Mexico", "description": "Classic Mexico resort golf", "latitude": 16.8531, "longitude": -99.8237},
    
    # CARIBBEAN - Golf Islands
    {"name": "Turks and Caicos Golf", "city": "Providenciales", "region_or_state": "Providenciales", "country": "Turks and Caicos", "description": "Caribbean island golf", "latitude": 21.7947, "longitude": -72.2656},
    {"name": "Cayman Islands Golf", "city": "George Town", "region_or_state": "Grand Cayman", "country": "Cayman Islands", "description": "Cayman Islands golf", "latitude": 19.2866, "longitude": -81.3744},
    {"name": "Aruba Golf", "city": "Oranjestad", "region_or_state": "Aruba", "country": "Aruba", "description": "Caribbean golf paradise", "latitude": 12.5204, "longitude": -70.0393},
    {"name": "Saint Lucia Golf", "city": "Castries", "region_or_state": "Castries", "country": "Saint Lucia", "description": "Tropical island golf", "latitude": 14.0101, "longitude": -60.9875},
    {"name": "Martinique Golf", "city": "Fort-de-France", "region_or_state": "Martinique", "country": "France", "description": "French Caribbean golf", "latitude": 14.6037, "longitude": -61.0730},
    
    # SOUTH AMERICA - Golf Cities  
    {"name": "Punta del Este Golf", "city": "Punta del Este", "region_or_state": "Maldonado", "country": "Uruguay", "description": "South American resort golf", "latitude": -34.9671, "longitude": -54.9332},
    {"name": "Viña del Mar Golf", "city": "Viña del Mar", "region_or_state": "Valparaíso", "country": "Chile", "description": "Chilean coast golf", "latitude": -33.0247, "longitude": -71.5516},
    {"name": "Mar del Plata Golf", "city": "Mar del Plata", "region_or_state": "Buenos Aires", "country": "Argentina", "description": "Argentine coast golf", "latitude": -38.0055, "longitude": -57.5426},
    {"name": "Medellín Golf", "city": "Medellín", "region_or_state": "Antioquia", "country": "Colombia", "description": "Colombian mountain golf", "latitude": 6.2442, "longitude": -75.5812},
    {"name": "Cartagena Golf", "city": "Cartagena", "region_or_state": "Bolívar", "country": "Colombia", "description": "Caribbean Colombia golf", "latitude": 10.3910, "longitude": -75.4794},
    
    # EUROPE - Additional Golf Cities
    {"name": "St Andrews Golf", "city": "St Andrews", "region_or_state": "Fife", "country": "Scotland", "description": "Home of golf", "latitude": 56.3398, "longitude": -2.7967},
    {"name": "Carnoustie Golf Town", "city": "Carnoustie", "region_or_state": "Angus", "country": "Scotland", "description": "Championship golf town", "latitude": 56.5016, "longitude": -2.7098},
    {"name": "Turnberry Golf", "city": "Turnberry", "region_or_state": "South Ayrshire", "country": "Scotland", "description": "Scottish links golf", "latitude": 55.3092, "longitude": -4.8472},
    {"name": "Dornoch Golf", "city": "Dornoch", "region_or_state": "Sutherland", "country": "Scotland", "description": "Highland golf destination", "latitude": 57.8792, "longitude": -4.0294},
    {"name": "Lahinch Golf Village", "city": "Lahinch", "region_or_state": "County Clare", "country": "Ireland", "description": "Irish links golf village", "latitude": 52.9324, "longitude": -9.3421},
    {"name": "Waterville Golf", "city": "Waterville", "region_or_state": "County Kerry", "country": "Ireland", "description": "Ring of Kerry golf", "latitude": 51.8316, "longitude": -10.1698},
    {"name": "Portmarnock Golf", "city": "Portmarnock", "region_or_state": "County Dublin", "country": "Ireland", "description": "Dublin links golf", "latitude": 53.4213, "longitude": -6.1396},
    {"name": "Costa Brava Golf", "city": "Girona", "region_or_state": "Catalonia", "country": "Spain", "description": "Mediterranean golf", "latitude": 41.9794, "longitude": 2.8214},
    {"name": "Costa del Sol Golf", "city": "Mijas", "region_or_state": "Andalusia", "country": "Spain", "description": "Spanish sun coast golf", "latitude": 36.5908, "longitude": -4.6361},
    {"name": "Algarve Golf", "city": "Lagos", "region_or_state": "Algarve", "country": "Portugal", "description": "Portuguese golf coast", "latitude": 37.1020, "longitude": -8.6743},
    {"name": "Cascais Golf", "city": "Cascais", "region_or_state": "Lisbon", "country": "Portugal", "description": "Lisbon coast golf", "latitude": 38.6979, "longitude": -9.4215},
    {"name": "Cannes Golf", "city": "Cannes", "region_or_state": "Alpes-Maritimes", "country": "France", "description": "French Riviera golf", "latitude": 43.5528, "longitude": 7.0174},
    {"name": "Deauville Golf", "city": "Deauville", "region_or_state": "Calvados", "country": "France", "description": "Normandy coast golf", "latitude": 49.3598, "longitude": 0.0750},
    {"name": "Biarritz Golf", "city": "Biarritz", "region_or_state": "Pyrénées-Atlantiques", "country": "France", "description": "Basque coast golf", "latitude": 43.4832, "longitude": -1.5586},
    {"name": "Kitzbuehel Golf", "city": "Kitzbühel", "region_or_state": "Tyrol", "country": "Austria", "description": "Alpine golf destination", "latitude": 47.4467, "longitude": 12.3925},
    {"name": "Gstaad Golf", "city": "Gstaad", "region_or_state": "Bern", "country": "Switzerland", "description": "Swiss Alps golf", "latitude": 46.4751, "longitude": 7.2861},
    {"name": "St Moritz Golf", "city": "St. Moritz", "region_or_state": "Grisons", "country": "Switzerland", "description": "Engadin valley golf", "latitude": 46.4908, "longitude": 9.8355},
    
    # ASIA - Golf Destinations
    {"name": "Hua Hin Golf", "city": "Hua Hin", "region_or_state": "Prachuap Khiri Khan", "country": "Thailand", "description": "Royal Thai golf resort", "latitude": 12.5664, "longitude": 99.9581},
    {"name": "Chiang Mai Golf", "city": "Chiang Mai", "region_or_state": "Chiang Mai", "country": "Thailand", "description": "Northern Thailand golf", "latitude": 18.7883, "longitude": 98.9853},
    {"name": "Pattaya Golf", "city": "Pattaya", "region_or_state": "Chonburi", "country": "Thailand", "description": "Thai beach golf", "latitude": 12.9236, "longitude": 100.8825},
    {"name": "Langkawi Golf", "city": "Langkawi", "region_or_state": "Kedah", "country": "Malaysia", "description": "Malaysian island golf", "latitude": 6.3500, "longitude": 99.8000},
    {"name": "Bintan Golf", "city": "Bintan", "region_or_state": "Riau Islands", "country": "Indonesia", "description": "Indonesian resort golf", "latitude": 1.1372, "longitude": 104.4529},
    {"name": "Bali Golf", "city": "Nusa Dua", "region_or_state": "Bali", "country": "Indonesia", "description": "Balinese golf paradise", "latitude": -8.7984, "longitude": 115.2369},
    {"name": "Jeju Golf", "city": "Jeju City", "region_or_state": "Jeju", "country": "South Korea", "description": "Korean island golf", "latitude": 33.5101, "longitude": 126.5219},
    {"name": "Busan Golf", "city": "Busan", "region_or_state": "Busan", "country": "South Korea", "description": "Korean coastal golf", "latitude": 35.1796, "longitude": 129.0756},
    {"name": "Incheon Golf", "city": "Incheon", "region_or_state": "Incheon", "country": "South Korea", "description": "Korean metropolitan golf", "latitude": 37.4563, "longitude": 126.7052},
    {"name": "Hakone Golf", "city": "Hakone", "region_or_state": "Kanagawa", "country": "Japan", "description": "Mount Fuji golf", "latitude": 35.2321, "longitude": 139.1067},
    {"name": "Karuizawa Golf", "city": "Karuizawa", "region_or_state": "Nagano", "country": "Japan", "description": "Japanese highland golf", "latitude": 36.3428, "longitude": 138.6245},
    {"name": "Okinawa Golf", "city": "Naha", "region_or_state": "Okinawa", "country": "Japan", "description": "Tropical Japan golf", "latitude": 26.2124, "longitude": 127.6792},
    
    # AUSTRALIA & NEW ZEALAND - Golf Cities
    {"name": "Gold Coast Golf", "city": "Gold Coast", "region_or_state": "Queensland", "country": "Australia", "description": "Australian beach golf", "latitude": -28.0167, "longitude": 153.4000},
    {"name": "Cairns Golf", "city": "Cairns", "region_or_state": "Queensland", "country": "Australia", "description": "Tropical north golf", "latitude": -16.9203, "longitude": 145.7781},
    {"name": "Sunshine Coast Golf", "city": "Sunshine Coast", "region_or_state": "Queensland", "country": "Australia", "description": "Queensland coast golf", "latitude": -26.6500, "longitude": 153.0667},
    {"name": "Tasmania Golf", "city": "Hobart", "region_or_state": "Tasmania", "country": "Australia", "description": "Tasmanian island golf", "latitude": -42.8821, "longitude": 147.3272},
    {"name": "Rotorua Golf", "city": "Rotorua", "region_or_state": "Bay of Plenty", "country": "New Zealand", "description": "Geothermal golf", "latitude": -38.1368, "longitude": 176.2497},
    {"name": "Taupo Golf", "city": "Taupo", "region_or_state": "Waikato", "country": "New Zealand", "description": "Lake Taupo golf", "latitude": -38.6857, "longitude": 176.0702},
    {"name": "Queenstown Golf", "city": "Queenstown", "region_or_state": "Otago", "country": "New Zealand", "description": "Adventure capital golf", "latitude": -45.0302, "longitude": 168.6626},
    
    # MIDDLE EAST - Golf Cities
    {"name": "Sharm El Sheikh Golf", "city": "Sharm El Sheikh", "region_or_state": "South Sinai", "country": "Egypt", "description": "Red Sea golf", "latitude": 27.9158, "longitude": 34.3300},
    {"name": "Hurghada Golf", "city": "Hurghada", "region_or_state": "Red Sea", "country": "Egypt", "description": "Egyptian resort golf", "latitude": 27.2574, "longitude": 33.8129},
    {"name": "Eilat Golf", "city": "Eilat", "region_or_state": "Southern District", "country": "Israel", "description": "Desert oasis golf", "latitude": 29.5581, "longitude": 34.9482},
    {"name": "Aqaba Golf", "city": "Aqaba", "region_or_state": "Aqaba", "country": "Jordan", "description": "Red Sea Jordan golf", "latitude": 29.5321, "longitude": 35.0063},
    
    # AFRICA - Golf Cities
    {"name": "Marrakech Golf", "city": "Marrakech", "region_or_state": "Marrakech-Safi", "country": "Morocco", "description": "Imperial city golf", "latitude": 31.6295, "longitude": -7.9811},
    {"name": "Agadir Golf", "city": "Agadir", "region_or_state": "Souss-Massa", "country": "Morocco", "description": "Atlantic Morocco golf", "latitude": 30.4278, "longitude": -9.5981},
    {"name": "Stellenbosch Golf", "city": "Stellenbosch", "region_or_state": "Western Cape", "country": "South Africa", "description": "Wine country golf", "latitude": -33.9321, "longitude": 18.8602},
    {"name": "Knysna Golf", "city": "Knysna", "region_or_state": "Western Cape", "country": "South Africa", "description": "Garden Route golf", "latitude": -34.0391, "longitude": 23.0473},
    {"name": "Hermanus Golf", "city": "Hermanus", "region_or_state": "Western Cape", "country": "South Africa", "description": "Whale coast golf", "latitude": -34.4187, "longitude": 19.2345},
    
    # PACIFIC ISLANDS - Golf Destinations
    {"name": "Maui Golf", "city": "Kahului", "region_or_state": "Hawaii", "country": "USA", "description": "Valley Isle golf", "latitude": 20.8947, "longitude": -156.4700},
    {"name": "Kauai Golf", "city": "Lihue", "region_or_state": "Hawaii", "country": "USA", "description": "Garden Isle golf", "latitude": 21.9788, "longitude": -159.3665},
    {"name": "Big Island Golf", "city": "Kailua-Kona", "region_or_state": "Hawaii", "country": "USA", "description": "Big Island resort golf", "latitude": 19.6390, "longitude": -155.9969},
    {"name": "Fiji Golf", "city": "Suva", "region_or_state": "Central Division", "country": "Fiji", "description": "South Pacific golf", "latitude": -18.1248, "longitude": 178.4501},
    {"name": "Guam Golf", "city": "Hagatna", "region_or_state": "Guam", "country": "USA", "description": "Micronesian golf", "latitude": 13.4745, "longitude": 144.7504},
]

# ADDITIONAL GOLF CITIES - Phase 2 to reach 500+
ADDITIONAL_GOLF_CITIES = [
    
    # UNITED STATES - More Golf Cities
    {"name": "Kiawah Island Golf", "city": "Kiawah Island", "region_or_state": "South Carolina", "country": "USA", "description": "Championship resort golf", "latitude": 32.6135, "longitude": -80.0852},
    {"name": "Sea Island Golf", "city": "Sea Island", "region_or_state": "Georgia", "country": "USA", "description": "Georgia coast luxury golf", "latitude": 31.1309, "longitude": -81.3937},
    {"name": "Amelia Island Golf", "city": "Fernandina Beach", "region_or_state": "Florida", "country": "USA", "description": "Historic Florida island golf", "latitude": 30.6691, "longitude": -81.4611},
    {"name": "Marco Island Golf", "city": "Marco Island", "region_or_state": "Florida", "country": "USA", "description": "Southwest Florida island golf", "latitude": 25.9412, "longitude": -81.7273},
    {"name": "Sanibel Golf", "city": "Sanibel", "region_or_state": "Florida", "country": "USA", "description": "Shell island golf paradise", "latitude": 26.4482, "longitude": -82.1226},
    {"name": "Duck Golf", "city": "Duck", "region_or_state": "North Carolina", "country": "USA", "description": "Outer Banks golf", "latitude": 36.1835, "longitude": -75.7454},
    {"name": "Rehoboth Beach Golf", "city": "Rehoboth Beach", "region_or_state": "Delaware", "country": "USA", "description": "Delaware beach golf", "latitude": 38.7193, "longitude": -75.0760},
    {"name": "Cape May Golf", "city": "Cape May", "region_or_state": "New Jersey", "country": "USA", "description": "Victorian seaside golf", "latitude": 38.9351, "longitude": -74.9060},
    {"name": "Martha's Vineyard Golf", "city": "Oak Bluffs", "region_or_state": "Massachusetts", "country": "USA", "description": "Island golf retreat", "latitude": 41.4558, "longitude": -70.5578},
    {"name": "Nantucket Golf", "city": "Nantucket", "region_or_state": "Massachusetts", "country": "USA", "description": "Historic island golf", "latitude": 41.2835, "longitude": -70.0995},
    {"name": "Block Island Golf", "city": "New Shoreham", "region_or_state": "Rhode Island", "country": "USA", "description": "New England island golf", "latitude": 41.1681, "longitude": -71.5776},
    {"name": "Mackinac Island Golf", "city": "Mackinac Island", "region_or_state": "Michigan", "country": "USA", "description": "Victorian island golf", "latitude": 45.8492, "longitude": -84.6196},
    {"name": "Door County Golf", "city": "Fish Creek", "region_or_state": "Wisconsin", "country": "USA", "description": "Great Lakes peninsula golf", "latitude": 45.1341, "longitude": -87.2487},
    {"name": "Mackinaw City Golf", "city": "Mackinaw City", "region_or_state": "Michigan", "country": "USA", "description": "Straits of Mackinac golf", "latitude": 45.7773, "longitude": -84.7278},
    {"name": "Petoskey Golf", "city": "Petoskey", "region_or_state": "Michigan", "country": "USA", "description": "Northern Michigan golf", "latitude": 45.3736, "longitude": -84.9553},
    {"name": "Boyne City Golf", "city": "Boyne City", "region_or_state": "Michigan", "country": "USA", "description": "Michigan resort golf", "latitude": 45.2178, "longitude": -85.0136},
    {"name": "Gaylord Golf", "city": "Gaylord", "region_or_state": "Michigan", "country": "USA", "description": "Alpine village golf", "latitude": 45.0275, "longitude": -84.6747},
    {"name": "Charlevoix Golf", "city": "Charlevoix", "region_or_state": "Michigan", "country": "USA", "description": "Lake Michigan golf", "latitude": 45.3178, "longitude": -85.2581},
    {"name": "Harbor Springs Golf", "city": "Harbor Springs", "region_or_state": "Michigan", "country": "USA", "description": "Michigan lake resort golf", "latitude": 45.4011, "longitude": -84.9897},
    {"name": "Frankfort Golf", "city": "Frankfort", "region_or_state": "Michigan", "country": "USA", "description": "Lake Michigan shore golf", "latitude": 44.6331, "longitude": -86.2370},
    
    # CANADA - Additional Golf Cities
    {"name": "Mont-Tremblant Golf", "city": "Mont-Tremblant", "region_or_state": "Quebec", "country": "Canada", "description": "Laurentian mountain golf", "latitude": 46.1692, "longitude": -74.5956},
    {"name": "Blue Mountain Golf", "city": "Collingwood", "region_or_state": "Ontario", "country": "Canada", "description": "Ontario resort golf", "latitude": 44.5006, "longitude": -80.2167},
    {"name": "Kelowna Golf", "city": "Kelowna", "region_or_state": "British Columbia", "country": "Canada", "description": "Okanagan valley golf", "latitude": 49.8880, "longitude": -119.4960},
    {"name": "Canmore Golf", "city": "Canmore", "region_or_state": "Alberta", "country": "Canada", "description": "Bow Valley mountain golf", "latitude": 51.0886, "longitude": -115.3681},
    {"name": "Prince Edward County Golf", "city": "Picton", "region_or_state": "Ontario", "country": "Canada", "description": "Wine country golf", "latitude": 44.0072, "longitude": -77.1411},
    {"name": "Timmins Golf", "city": "Timmins", "region_or_state": "Ontario", "country": "Canada", "description": "Northern Ontario golf", "latitude": 48.4758, "longitude": -81.3304},
    {"name": "Sault Ste. Marie Golf", "city": "Sault Ste. Marie", "region_or_state": "Ontario", "country": "Canada", "description": "Great Lakes golf", "latitude": 46.5197, "longitude": -84.3467},
    {"name": "Thunder Bay Golf", "city": "Thunder Bay", "region_or_state": "Ontario", "country": "Canada", "description": "Northwestern Ontario golf", "latitude": 48.3809, "longitude": -89.2477},
    {"name": "Sudbury Golf", "city": "Sudbury", "region_or_state": "Ontario", "country": "Canada", "description": "Nickel City golf", "latitude": 46.4917, "longitude": -80.9930},
    {"name": "North Bay Golf", "city": "North Bay", "region_or_state": "Ontario", "country": "Canada", "description": "Nipissing lake golf", "latitude": 46.3091, "longitude": -79.4608},
    
    # EUROPE - Additional Golf Destinations
    {"name": "St. Andrews Bay Golf", "city": "St. Andrews", "region_or_state": "Fife", "country": "Scotland", "description": "Old Course golf town", "latitude": 56.3398, "longitude": -2.7967},
    {"name": "Royal Troon Golf", "city": "Troon", "region_or_state": "South Ayrshire", "country": "Scotland", "description": "Championship links golf", "latitude": 55.5425, "longitude": -4.6567},
    {"name": "Prestwick Golf", "city": "Prestwick", "region_or_state": "South Ayrshire", "country": "Scotland", "description": "Historic links golf", "latitude": 55.4942, "longitude": -4.6133},
    {"name": "Muirfield Golf", "city": "Gullane", "region_or_state": "East Lothian", "country": "Scotland", "description": "Honourable Company golf", "latitude": 56.0431, "longitude": -2.8244},
    {"name": "North Berwick Golf", "city": "North Berwick", "region_or_state": "East Lothian", "country": "Scotland", "description": "Scottish seaside golf", "latitude": 56.0585, "longitude": -2.7230},
    {"name": "Machrihanish Golf", "city": "Machrihanish", "region_or_state": "Argyll and Bute", "country": "Scotland", "description": "Remote links golf", "latitude": 55.4267, "longitude": -5.7142},
    {"name": "Islay Golf", "city": "Port Ellen", "region_or_state": "Argyll and Bute", "country": "Scotland", "description": "Whisky island golf", "latitude": 55.6278, "longitude": -6.1889},
    {"name": "Ballybunion Golf", "city": "Ballybunion", "region_or_state": "County Kerry", "country": "Ireland", "description": "Irish links masterpiece", "latitude": 52.5114, "longitude": -9.6739},
    {"name": "Royal County Down Golf", "city": "Newcastle", "region_or_state": "County Down", "country": "Northern Ireland", "description": "Mourne mountain golf", "latitude": 54.2161, "longitude": -5.8947},
    {"name": "Royal Portrush Golf", "city": "Portrush", "region_or_state": "County Antrim", "country": "Northern Ireland", "description": "Open Championship golf", "latitude": 55.2044, "longitude": -6.6544},
    {"name": "Kinsale Golf", "city": "Kinsale", "region_or_state": "County Cork", "country": "Ireland", "description": "Irish coastal golf", "latitude": 51.7058, "longitude": -8.5306},
    {"name": "Killarney Golf", "city": "Killarney", "region_or_state": "County Kerry", "country": "Ireland", "description": "Lakes of Killarney golf", "latitude": 52.0599, "longitude": -9.5044},
    {"name": "Connemara Golf", "city": "Clifden", "region_or_state": "County Galway", "country": "Ireland", "description": "Wild Atlantic Way golf", "latitude": 53.4889, "longitude": -10.0206},
    
    # ASIA-PACIFIC - Additional Cities
    {"name": "Mission Hills Golf", "city": "Shenzhen", "region_or_state": "Guangdong", "country": "China", "description": "World's largest golf resort", "latitude": 22.5431, "longitude": 114.0579},
    {"name": "Zhongshan Golf", "city": "Zhongshan", "region_or_state": "Guangdong", "country": "China", "description": "Pearl River Delta golf", "latitude": 22.5150, "longitude": 113.3927},
    {"name": "Hainan Golf", "city": "Sanya", "region_or_state": "Hainan", "country": "China", "description": "Tropical island golf", "latitude": 18.2528, "longitude": 109.5117},
    {"name": "Boracay Golf", "city": "Malay", "region_or_state": "Aklan", "country": "Philippines", "description": "White beach island golf", "latitude": 11.9804, "longitude": 121.9189},
    {"name": "Baguio Golf", "city": "Baguio", "region_or_state": "Benguet", "country": "Philippines", "description": "Mountain city golf", "latitude": 16.4023, "longitude": 120.5960},
    {"name": "Tagaytay Golf", "city": "Tagaytay", "region_or_state": "Cavite", "country": "Philippines", "description": "Ridge top golf", "latitude": 14.1053, "longitude": 120.9628},
    {"name": "Da Nang Golf", "city": "Da Nang", "region_or_state": "Da Nang", "country": "Vietnam", "description": "Central Vietnam golf", "latitude": 16.0471, "longitude": 108.2068},
    {"name": "Dalat Golf", "city": "Da Lat", "region_or_state": "Lam Dong", "country": "Vietnam", "description": "Highland golf retreat", "latitude": 11.9404, "longitude": 108.4583},
    {"name": "Nha Trang Golf", "city": "Nha Trang", "region_or_state": "Khanh Hoa", "country": "Vietnam", "description": "Beach resort golf", "latitude": 12.2388, "longitude": 109.1967},
    {"name": "Colombo Golf", "city": "Colombo", "region_or_state": "Western Province", "country": "Sri Lanka", "description": "Ceylon golf heritage", "latitude": 6.9271, "longitude": 79.8612},
    {"name": "Kandy Golf", "city": "Kandy", "region_or_state": "Central Province", "country": "Sri Lanka", "description": "Hill country golf", "latitude": 7.2906, "longitude": 80.6337},
    {"name": "Galle Golf", "city": "Galle", "region_or_state": "Southern Province", "country": "Sri Lanka", "description": "Fort city golf", "latitude": 6.0535, "longitude": 80.2210},
    
    # MIDDLE EAST - Additional Golf Cities
    {"name": "Doha Golf", "city": "Doha", "region_or_state": "Ad Dawhah", "country": "Qatar", "description": "Desert oasis golf", "latitude": 25.2854, "longitude": 51.5310},
    {"name": "Muscat Golf", "city": "Muscat", "region_or_state": "Muscat Governorate", "country": "Oman", "description": "Arabian gulf golf", "latitude": 23.5859, "longitude": 58.4059},
    {"name": "Manama Golf", "city": "Manama", "region_or_state": "Capital Governorate", "country": "Bahrain", "description": "Island kingdom golf", "latitude": 26.2235, "longitude": 50.5876},
    {"name": "Kuwait City Golf", "city": "Kuwait City", "region_or_state": "Al Asimah", "country": "Kuwait", "description": "Persian Gulf golf", "latitude": 29.3759, "longitude": 47.9774},
    {"name": "Amman Golf", "city": "Amman", "region_or_state": "Amman Governorate", "country": "Jordan", "description": "Historic city golf", "latitude": 31.9454, "longitude": 35.9284},
    {"name": "Beirut Golf", "city": "Beirut", "region_or_state": "Beirut Governorate", "country": "Lebanon", "description": "Mediterranean golf", "latitude": 33.8938, "longitude": 35.5018},
    
    # SOUTH AMERICA - Additional Cities
    {"name": "Bariloche Golf", "city": "San Carlos de Bariloche", "region_or_state": "Río Negro", "country": "Argentina", "description": "Patagonian lake golf", "latitude": -41.1335, "longitude": -71.3103},
    {"name": "Mendoza Golf", "city": "Mendoza", "region_or_state": "Mendoza", "country": "Argentina", "description": "Wine country golf", "latitude": -32.8908, "longitude": -68.8272},
    {"name": "Córdoba Golf", "city": "Córdoba", "region_or_state": "Córdoba", "country": "Argentina", "description": "Argentine heartland golf", "latitude": -31.4201, "longitude": -64.1888},
    {"name": "Gramado Golf", "city": "Gramado", "region_or_state": "Rio Grande do Sul", "country": "Brazil", "description": "Mountain resort golf", "latitude": -29.3788, "longitude": -50.8740},
    {"name": "Búzios Golf", "city": "Armação dos Búzios", "region_or_state": "Rio de Janeiro", "country": "Brazil", "description": "Brazilian riviera golf", "latitude": -22.7469, "longitude": -41.8819},
    {"name": "Florianópolis Golf", "city": "Florianópolis", "region_or_state": "Santa Catarina", "country": "Brazil", "description": "Magic island golf", "latitude": -27.5954, "longitude": -48.5480},
    {"name": "Salvador Golf", "city": "Salvador", "region_or_state": "Bahia", "country": "Brazil", "description": "Bahian coast golf", "latitude": -12.9777, "longitude": -38.5016},
    {"name": "Fortaleza Golf", "city": "Fortaleza", "region_or_state": "Ceará", "country": "Brazil", "description": "Northeastern Brazil golf", "latitude": -3.7327, "longitude": -38.5267},
    {"name": "Quito Golf", "city": "Quito", "region_or_state": "Pichincha", "country": "Ecuador", "description": "Equatorial highland golf", "latitude": -0.1807, "longitude": -78.4678},
    {"name": "Lima Golf", "city": "Lima", "region_or_state": "Lima", "country": "Peru", "description": "Pacific coast golf", "latitude": -12.0464, "longitude": -77.0428},
    {"name": "La Paz Golf", "city": "La Paz", "region_or_state": "La Paz", "country": "Bolivia", "description": "World's highest capital golf", "latitude": -16.5000, "longitude": -68.1193},
    {"name": "Asunción Golf", "city": "Asunción", "region_or_state": "Capital District", "country": "Paraguay", "description": "River city golf", "latitude": -25.2637, "longitude": -57.5759},
    {"name": "Santiago Golf", "city": "Santiago", "region_or_state": "Santiago Metropolitan", "country": "Chile", "description": "Andean foothills golf", "latitude": -33.4489, "longitude": -70.6693},
    {"name": "Valparaíso Golf", "city": "Valparaíso", "region_or_state": "Valparaíso", "country": "Chile", "description": "Historic port golf", "latitude": -33.0458, "longitude": -71.6197},
    
    # AFRICA - Additional Golf Cities
    {"name": "Marrakech Palmeraie Golf", "city": "Marrakech", "region_or_state": "Marrakech-Safi", "country": "Morocco", "description": "Palm grove golf", "latitude": 31.6295, "longitude": -7.9811},
    {"name": "Casablanca Golf", "city": "Casablanca", "region_or_state": "Casablanca-Settat", "country": "Morocco", "description": "Atlantic coast golf", "latitude": 33.5731, "longitude": -7.5898},
    {"name": "Cairo Golf", "city": "Cairo", "region_or_state": "Cairo Governorate", "country": "Egypt", "description": "Nile delta golf", "latitude": 30.0444, "longitude": 31.2357},
    {"name": "Nairobi Golf", "city": "Nairobi", "region_or_state": "Nairobi County", "country": "Kenya", "description": "Equatorial highland golf", "latitude": -1.2921, "longitude": 36.8219},
    {"name": "Lagos Golf", "city": "Lagos", "region_or_state": "Lagos State", "country": "Nigeria", "description": "West African golf", "latitude": 6.5244, "longitude": 3.3792},
    {"name": "Accra Golf", "city": "Accra", "region_or_state": "Greater Accra Region", "country": "Ghana", "description": "Gold Coast golf", "latitude": 5.6037, "longitude": -0.1870},
    {"name": "Abidjan Golf", "city": "Abidjan", "region_or_state": "Lagunes", "country": "Côte d'Ivoire", "description": "Ivory Coast golf", "latitude": 5.3600, "longitude": -4.0083},
    {"name": "Dakar Golf", "city": "Dakar", "region_or_state": "Dakar Region", "country": "Senegal", "description": "Westernmost Africa golf", "latitude": 14.7167, "longitude": -17.4677},
    {"name": "Tunis Golf", "city": "Tunis", "region_or_state": "Tunis Governorate", "country": "Tunisia", "description": "Mediterranean Africa golf", "latitude": 36.8065, "longitude": 10.1815},
    {"name": "Windhoek Golf", "city": "Windhoek", "region_or_state": "Khomas Region", "country": "Namibia", "description": "Desert capital golf", "latitude": -22.5597, "longitude": 17.0832},
    {"name": "Gaborone Golf", "city": "Gaborone", "region_or_state": "South-East District", "country": "Botswana", "description": "Kalahari golf", "latitude": -24.6282, "longitude": 25.9231},
    {"name": "Harare Golf", "city": "Harare", "region_or_state": "Harare Province", "country": "Zimbabwe", "description": "Highveld golf", "latitude": -17.8252, "longitude": 31.0335},
    {"name": "Lusaka Golf", "city": "Lusaka", "region_or_state": "Lusaka Province", "country": "Zambia", "description": "Central African golf", "latitude": -15.3875, "longitude": 28.3228},
    {"name": "Mauritius Golf", "city": "Port Louis", "region_or_state": "Port Louis District", "country": "Mauritius", "description": "Indian Ocean island golf", "latitude": -20.1619, "longitude": 57.5012},
    {"name": "Seychelles Golf", "city": "Victoria", "region_or_state": "Mahé", "country": "Seychelles", "description": "Tropical paradise golf", "latitude": -4.6796, "longitude": 55.4920},
    
    # CARIBBEAN - Additional Islands
    {"name": "Barbados Golf", "city": "Bridgetown", "region_or_state": "Saint Michael", "country": "Barbados", "description": "Caribbean reef golf", "latitude": 13.1134, "longitude": -59.5985},
    {"name": "Trinidad Golf", "city": "Port of Spain", "region_or_state": "Port of Spain", "country": "Trinidad and Tobago", "description": "Twin island golf", "latitude": 10.6596, "longitude": -61.5019},
    {"name": "Jamaica Golf", "city": "Montego Bay", "region_or_state": "Saint James Parish", "country": "Jamaica", "description": "Blue Mountain golf", "latitude": 18.4762, "longitude": -77.8939},
    {"name": "Antigua Golf", "city": "St. John's", "region_or_state": "Saint John", "country": "Antigua and Barbuda", "description": "365 beaches golf", "latitude": 17.1274, "longitude": -61.8468},
    {"name": "St. Kitts Golf", "city": "Basseterre", "region_or_state": "Saint George Basseterre", "country": "Saint Kitts and Nevis", "description": "Volcanic island golf", "latitude": 17.2948, "longitude": -62.7257},
    {"name": "Grenada Golf", "city": "St. George's", "region_or_state": "Saint George", "country": "Grenada", "description": "Spice island golf", "latitude": 12.0565, "longitude": -61.7485},
    {"name": "Dominica Golf", "city": "Roseau", "region_or_state": "Saint George", "country": "Dominica", "description": "Nature island golf", "latitude": 15.3092, "longitude": -61.3794},
    {"name": "St. Vincent Golf", "city": "Kingstown", "region_or_state": "Saint George", "country": "Saint Vincent and the Grenadines", "description": "Windward islands golf", "latitude": 13.1579, "longitude": -61.2248},
]

# FINAL PHASE - Additional Cities to Reach 500+
FINAL_GOLF_CITIES = [
    
    # MORE US GOLF CITIES
    {"name": "Kiawah Golf Resort", "city": "Johns Island", "region_or_state": "South Carolina", "country": "USA", "description": "Lowcountry championship golf", "latitude": 32.6023, "longitude": -80.0659},
    {"name": "Greenbrier Golf", "city": "White Sulphur Springs", "region_or_state": "West Virginia", "country": "USA", "description": "Historic mountain resort golf", "latitude": 37.7985, "longitude": -80.3009},
    {"name": "French Lick Golf", "city": "French Lick", "region_or_state": "Indiana", "country": "USA", "description": "Indiana resort golf", "latitude": 38.5489, "longitude": -86.6197},
    {"name": "Kohler Golf", "city": "Kohler", "region_or_state": "Wisconsin", "country": "USA", "description": "Destination resort golf", "latitude": 43.7403, "longitude": -87.7834},
    {"name": "Bandon Golf", "city": "Bandon", "region_or_state": "Oregon", "country": "USA", "description": "Pacific coast links golf", "latitude": 43.1196, "longitude": -124.4085},
    {"name": "Chambers Bay Golf", "city": "University Place", "region_or_state": "Washington", "country": "USA", "description": "Puget Sound links golf", "latitude": 47.2529, "longitude": -122.5015},
    {"name": "Streamsong Golf", "city": "Bowling Green", "region_or_state": "Florida", "country": "USA", "description": "Central Florida golf destination", "latitude": 27.6386, "longitude": -81.8256},
    {"name": "Erin Hills Golf", "city": "Erin", "region_or_state": "Wisconsin", "country": "USA", "description": "Wisconsin championship golf", "latitude": 43.1839, "longitude": -88.3326},
    {"name": "Sand Valley Golf", "city": "Nekoosa", "region_or_state": "Wisconsin", "country": "USA", "description": "Wisconsin sand dunes golf", "latitude": 44.3136, "longitude": -89.9068},
    {"name": "Cabot Links Golf", "city": "Inverness", "region_or_state": "Nova Scotia", "country": "Canada", "description": "Atlantic Canada links golf", "latitude": 46.2044, "longitude": -61.1125},
    {"name": "Cabot Cliffs Golf", "city": "Inverness", "region_or_state": "Nova Scotia", "country": "Canada", "description": "Cape Breton links golf", "latitude": 46.2044, "longitude": -61.1125},
    
    # MORE INTERNATIONAL CITIES
    {"name": "Doonbeg Golf", "city": "Doonbeg", "region_or_state": "County Clare", "country": "Ireland", "description": "Wild Atlantic links golf", "latitude": 52.7431, "longitude": -9.5408},
    {"name": "Old Head Golf", "city": "Kinsale", "region_or_state": "County Cork", "country": "Ireland", "description": "Cliff-top golf experience", "latitude": 51.6047, "longitude": -8.5331},
    {"name": "Trump Turnberry Golf", "city": "Turnberry", "region_or_state": "South Ayrshire", "country": "Scotland", "description": "Ailsa Course championship golf", "latitude": 55.3092, "longitude": -4.8472},
    {"name": "Kingsbarns Golf", "city": "Kingsbarns", "region_or_state": "Fife", "country": "Scotland", "description": "Scottish coast golf links", "latitude": 56.2789, "longitude": -2.6658},
    {"name": "Castle Stuart Golf", "city": "Inverness", "region_or_state": "Highland", "country": "Scotland", "description": "Scottish Highland golf", "latitude": 57.4778, "longitude": -4.2247},
    {"name": "Loch Lomond Golf", "city": "Luss", "region_or_state": "Argyll and Bute", "country": "Scotland", "description": "Scottish loch golf", "latitude": 56.1000, "longitude": -4.6333},
    {"name": "Adare Manor Golf", "city": "Adare", "region_or_state": "County Limerick", "country": "Ireland", "description": "Championship parkland golf", "latitude": 52.5642, "longitude": -8.7839},
    {"name": "Mount Juliet Golf", "city": "Thomastown", "region_or_state": "County Kilkenny", "country": "Ireland", "description": "Jack Nicklaus signature golf", "latitude": 52.5264, "longitude": -7.1378},
    {"name": "K Club Golf", "city": "Straffan", "region_or_state": "County Kildare", "country": "Ireland", "description": "Ryder Cup championship golf", "latitude": 53.3086, "longitude": -6.6289},
    {"name": "Druids Glen Golf", "city": "Newtownmountkennedy", "region_or_state": "County Wicklow", "country": "Ireland", "description": "Garden of Ireland golf", "latitude": 53.1025, "longitude": -6.1011},
    {"name": "Emirates Golf", "city": "Dubai", "region_or_state": "Dubai", "country": "United Arab Emirates", "description": "Desert oasis championship golf", "latitude": 25.2048, "longitude": 55.2708},
    {"name": "Abu Dhabi Golf", "city": "Abu Dhabi", "region_or_state": "Abu Dhabi", "country": "United Arab Emirates", "description": "Capital city desert golf", "latitude": 24.4539, "longitude": 54.3773},
    {"name": "Al Ain Golf", "city": "Al Ain", "region_or_state": "Abu Dhabi", "country": "United Arab Emirates", "description": "Oasis city golf", "latitude": 24.2075, "longitude": 55.7447},
    {"name": "Ras Al Khaimah Golf", "city": "Ras Al Khaimah", "region_or_state": "Ras Al Khaimah", "country": "United Arab Emirates", "description": "Northern Emirates golf", "latitude": 25.7889, "longitude": 55.9758},
    {"name": "Fujairah Golf", "city": "Fujairah", "region_or_state": "Fujairah", "country": "United Arab Emirates", "description": "East coast UAE golf", "latitude": 25.1164, "longitude": 56.3394},
    {"name": "Sharjah Golf", "city": "Sharjah", "region_or_state": "Sharjah", "country": "United Arab Emirates", "description": "Cultural emirate golf", "latitude": 25.3463, "longitude": 55.4209},
    {"name": "Ajman Golf", "city": "Ajman", "region_or_state": "Ajman", "country": "United Arab Emirates", "description": "Compact emirate golf", "latitude": 25.4052, "longitude": 55.5136},
    {"name": "Umm Al Quwain Golf", "city": "Umm Al Quwain", "region_or_state": "Umm Al Quwain", "country": "United Arab Emirates", "description": "Peaceful emirate golf", "latitude": 25.5644, "longitude": 55.6906},
    {"name": "Riyadh Golf", "city": "Riyadh", "region_or_state": "Riyadh Province", "country": "Saudi Arabia", "description": "Capital city desert golf", "latitude": 24.7136, "longitude": 46.6753},
    {"name": "Jeddah Golf", "city": "Jeddah", "region_or_state": "Makkah Province", "country": "Saudi Arabia", "description": "Red Sea port golf", "latitude": 21.4858, "longitude": 39.1925},
    {"name": "Dammam Golf", "city": "Dammam", "region_or_state": "Eastern Province", "country": "Saudi Arabia", "description": "Eastern Saudi golf", "latitude": 26.4207, "longitude": 50.0888},
    {"name": "Al Khobar Golf", "city": "Al Khobar", "region_or_state": "Eastern Province", "country": "Saudi Arabia", "description": "Gulf coast golf", "latitude": 26.2172, "longitude": 50.1971},
    {"name": "Tabuk Golf", "city": "Tabuk", "region_or_state": "Tabuk Province", "country": "Saudi Arabia", "description": "Northwest Saudi golf", "latitude": 28.3998, "longitude": 36.5700},
    {"name": "Abha Golf", "city": "Abha", "region_or_state": "Asir Province", "country": "Saudi Arabia", "description": "Mountain resort golf", "latitude": 18.2164, "longitude": 42.5047},
    {"name": "Yanbu Golf", "city": "Yanbu", "region_or_state": "Al Madinah Province", "country": "Saudi Arabia", "description": "Red Sea industrial golf", "latitude": 24.0900, "longitude": 38.0618},
    {"name": "Al Jubail Golf", "city": "Al Jubail", "region_or_state": "Eastern Province", "country": "Saudi Arabia", "description": "Industrial city golf", "latitude": 27.0174, "longitude": 49.6603},
    {"name": "Taif Golf", "city": "Taif", "region_or_state": "Makkah Province", "country": "Saudi Arabia", "description": "Mountain summer golf", "latitude": 21.2703, "longitude": 40.4158},
    
    # MORE ASIA-PACIFIC
    {"name": "Coron Golf", "city": "Coron", "region_or_state": "Palawan", "country": "Philippines", "description": "Island paradise golf", "latitude": 12.0050, "longitude": 120.2114},
    {"name": "El Nido Golf", "city": "El Nido", "region_or_state": "Palawan", "country": "Philippines", "description": "Limestone cliff golf", "latitude": 11.1850, "longitude": 119.4094},
    {"name": "Siargao Golf", "city": "General Luna", "region_or_state": "Surigao del Norte", "country": "Philippines", "description": "Surfing island golf", "latitude": 9.7700, "longitude": 126.1542},
]

def add_golf_cities():
    """Add golf destination cities to the database"""
    print("🏌️ Adding golf destination cities...")
    print("=" * 60)
    
    added_count = 0
    skipped_count = 0
    errors = []
    
    for city_data in NEW_GOLF_CITIES + ADDITIONAL_GOLF_CITIES + FINAL_GOLF_CITIES:
        try:
            # Check if destination already exists (by city and country)
            existing = Destination.objects.filter(
                city=city_data['city'], 
                country=city_data['country']
            ).first()
            
            if existing:
                print(f"⚠️  Skipping {city_data['city']}, {city_data['country']} - already exists")
                skipped_count += 1
                continue
            
            # Create new destination
            destination = Destination.objects.create(
                name=city_data['name'],
                city=city_data['city'],
                region_or_state=city_data['region_or_state'],
                country=city_data['country'],
                description=city_data['description'],
                latitude=Decimal(str(city_data['latitude'])),
                longitude=Decimal(str(city_data['longitude'])),
                image_url='',  # Will be populated later if needed
            )
            
            print(f"✅ Added: {destination.city}, {destination.country} - {destination.description}")
            added_count += 1
            
        except Exception as e:
            error_msg = f"Error adding {city_data.get('city', 'Unknown')}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    print("\n" + "=" * 60)
    print("🎉 Golf city addition completed!")
    print(f"📊 Summary:")
    print(f"   • New cities added: {added_count}")
    print(f"   • Cities skipped (already exist): {skipped_count}")
    print(f"   • Errors: {len(errors)}")
    
    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   • ... and {len(errors) - 5} more errors")
    
    # Final count
    total_destinations = Destination.objects.count()
    print(f"\n📈 Total destinations in database: {total_destinations}")
    
    if total_destinations >= 500:
        print("🎯 Goal achieved! Over 500 destinations!")
    else:
        print(f"📊 {500 - total_destinations} more needed to reach 500")
    
    return added_count, skipped_count, len(errors)

if __name__ == "__main__":
    try:
        added, skipped, errors = add_golf_cities()
        print(f"\n✨ Process complete! Added {added} cities, skipped {skipped}, {errors} errors.")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
