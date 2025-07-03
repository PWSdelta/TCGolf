#!/usr/bin/env python
"""
Add More International Golf Destinations

This script adds additional destinations to reach 500+ total destinations.
Focus on underrepresented regions and popular golf destinations worldwide.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination

# Additional international golf destinations
NEW_DESTINATIONS = [
    # ASIA-PACIFIC (Major Golf Destinations)
    {"name": "Mission Hills Golf Club", "city": "Shenzhen", "region_or_state": "Guangdong", "country": "China", "description": "World's largest golf facility", "latitude": 22.7000, "longitude": 114.0000},
    {"name": "Hirono Golf Club", "city": "Kobe", "region_or_state": "Hyogo", "country": "Japan", "description": "Classic Japanese golf experience", "latitude": 34.8000, "longitude": 135.2000},
    {"name": "Kawana Golf Course", "city": "Ito", "region_or_state": "Shizuoka", "country": "Japan", "description": "Spectacular ocean views", "latitude": 34.9000, "longitude": 139.1000},
    {"name": "Nine Bridges Golf Club", "city": "Jeju Island", "region_or_state": "Jeju", "country": "South Korea", "description": "Premium Korean golf destination", "latitude": 33.3000, "longitude": 126.5000},
    {"name": "Laguna Golf Bintan", "city": "Bintan", "region_or_state": "Riau Islands", "country": "Indonesia", "description": "Tropical island golf paradise", "latitude": 1.1000, "longitude": 104.4000},
    {"name": "Bali National Golf Club", "city": "Nusa Dua", "region_or_state": "Bali", "country": "Indonesia", "description": "Championship course in paradise", "latitude": -8.8000, "longitude": 115.2000},
    {"name": "The Els Club", "city": "Kuala Lumpur", "region_or_state": "Selangor", "country": "Malaysia", "description": "Ernie Els designed masterpiece", "latitude": 3.1000, "longitude": 101.7000},
    {"name": "Royal Melbourne Golf Club", "city": "Melbourne", "region_or_state": "Victoria", "country": "Australia", "description": "Australia's premier golf club", "latitude": -37.9000, "longitude": 145.0000},
    {"name": "Kingston Heath Golf Club", "city": "Melbourne", "region_or_state": "Victoria", "country": "Australia", "description": "Legendary Australian sand belt", "latitude": -37.9500, "longitude": 145.0500},
    {"name": "The Australian Golf Club", "city": "Sydney", "region_or_state": "New South Wales", "country": "Australia", "description": "Historic championship venue", "latitude": -33.9000, "longitude": 151.2000},
    
    # EUROPE (Additional Premium Destinations)
    {"name": "Royal County Down", "city": "Newcastle", "region_or_state": "County Down", "country": "Northern Ireland", "description": "World's best golf course", "latitude": 54.2500, "longitude": -5.9000},
    {"name": "Ballybunion Golf Club", "city": "Ballybunion", "region_or_state": "County Kerry", "country": "Ireland", "description": "Spectacular links golf", "latitude": 52.5000, "longitude": -9.7000},
    {"name": "Lahinch Golf Club", "city": "Lahinch", "region_or_state": "County Clare", "country": "Ireland", "description": "Traditional Irish links", "latitude": 52.9000, "longitude": -9.3000},
    {"name": "Royal Dornoch", "city": "Dornoch", "region_or_state": "Scotland", "country": "United Kingdom", "description": "Highland links perfection", "latitude": 57.9000, "longitude": -4.0000},
    {"name": "Kingsbarns Golf Links", "city": "St Andrews", "region_or_state": "Fife", "country": "Scotland", "description": "Modern Scottish links", "latitude": 56.3000, "longitude": -2.6000},
    {"name": "Carnoustie Golf Links", "city": "Carnoustie", "region_or_state": "Angus", "country": "Scotland", "description": "Championship links venue", "latitude": 56.5000, "longitude": -2.7000},
    {"name": "Royal Birkdale", "city": "Southport", "region_or_state": "England", "country": "United Kingdom", "description": "Open Championship venue", "latitude": 53.6000, "longitude": -3.0000},
    {"name": "Wentworth Golf Club", "city": "Virginia Water", "region_or_state": "Surrey", "country": "United Kingdom", "description": "Home of the PGA Championship", "latitude": 51.4000, "longitude": -0.6000},
    {"name": "Club de Golf Valderrama", "city": "San Roque", "region_or_state": "Andalusia", "country": "Spain", "description": "Europe's finest golf course", "latitude": 36.3000, "longitude": -5.3000},
    {"name": "Fancourt Golf Estate", "city": "George", "region_or_state": "Western Cape", "country": "South Africa", "description": "Links course excellence", "latitude": -33.9000, "longitude": 22.4000},
    
    # MIDDLE EAST & AFRICA
    {"name": "Emirates Golf Club", "city": "Dubai", "region_or_state": "Dubai", "country": "United Arab Emirates", "description": "Desert golf pioneer", "latitude": 25.2000, "longitude": 55.2000},
    {"name": "Earth Course at Jumeirah Golf Estates", "city": "Dubai", "region_or_state": "Dubai", "country": "United Arab Emirates", "description": "European Tour finale venue", "latitude": 25.0000, "longitude": 55.1000},
    {"name": "The Address Montgomerie Dubai", "city": "Dubai", "region_or_state": "Dubai", "country": "United Arab Emirates", "description": "Colin Montgomerie design", "latitude": 25.1000, "longitude": 55.2000},
    {"name": "Gary Player Golf Course", "city": "Sun City", "region_or_state": "North West", "country": "South Africa", "description": "Desert golf masterpiece", "latitude": -25.3000, "longitude": 27.1000},
    {"name": "Leopard Creek Country Club", "city": "Malelane", "region_or_state": "Mpumalanga", "country": "South Africa", "description": "African bush golf", "latitude": -25.4000, "longitude": 31.5000},
    {"name": "Royal Golf Dar Es Salam", "city": "Rabat", "region_or_state": "Rabat-Salé", "country": "Morocco", "description": "Royal Moroccan golf", "latitude": 34.0000, "longitude": -6.8000},
    {"name": "The Cascades Golf Resort", "city": "Soma Bay", "region_or_state": "Red Sea", "country": "Egypt", "description": "Red Sea golf paradise", "latitude": 26.8000, "longitude": 34.0000},
    
    # AMERICAS (Additional US & International)
    {"name": "Cypress Point Club", "city": "Pebble Beach", "region_or_state": "California", "country": "USA", "description": "Most exclusive golf course", "latitude": 36.5500, "longitude": -121.9500},
    {"name": "Seminole Golf Club", "city": "Juno Beach", "region_or_state": "Florida", "country": "USA", "description": "Donald Ross masterpiece", "latitude": 26.9000, "longitude": -80.0500},
    {"name": "Crystal Downs Country Club", "city": "Frankfort", "region_or_state": "Michigan", "country": "USA", "description": "MacKenzie/Maxwell design", "latitude": 44.6000, "longitude": -86.2000},
    {"name": "The National Golf Links", "city": "Southampton", "region_or_state": "New York", "country": "USA", "description": "America's St Andrews", "latitude": 40.9000, "longitude": -72.4000},
    {"name": "Prairie Dunes Country Club", "city": "Hutchinson", "region_or_state": "Kansas", "country": "USA", "description": "Prairie links golf", "latitude": 38.0000, "longitude": -97.9000},
    {"name": "Sand Hills Golf Club", "city": "Mullen", "region_or_state": "Nebraska", "country": "USA", "description": "Modern links masterpiece", "latitude": 42.0000, "longitude": -101.0000},
    {"name": "Fishers Island Club", "city": "Fishers Island", "region_or_state": "New York", "country": "USA", "description": "Island golf perfection", "latitude": 41.3000, "longitude": -72.0000},
    {"name": "Casa de Campo", "city": "La Romana", "region_or_state": "La Romana", "country": "Dominican Republic", "description": "Teeth of the Dog course", "latitude": 18.4000, "longitude": -68.9000},
    {"name": "Cap Cana Golf Club", "city": "Punta Cana", "region_or_state": "La Altagracia", "country": "Dominican Republic", "description": "Jack Nicklaus design", "latitude": 18.5000, "longitude": -68.4000},
    {"name": "Tryall Golf Club", "city": "Montego Bay", "region_or_state": "Saint James", "country": "Jamaica", "description": "Caribbean golf paradise", "latitude": 18.4000, "longitude": -77.9000},
    {"name": "Four Seasons Golf Club Nevis", "city": "Charlestown", "region_or_state": "Nevis", "country": "Saint Kitts and Nevis", "description": "Volcanic island golf", "latitude": 17.1000, "longitude": -62.6000},
    {"name": "Casa de Campo Marina", "city": "La Romana", "region_or_state": "La Romana", "country": "Dominican Republic", "description": "Dye Fore course", "latitude": 18.4200, "longitude": -68.8800},
    
    # SOUTH AMERICA
    {"name": "Jockey Club Brasileiro", "city": "São Paulo", "region_or_state": "São Paulo", "country": "Brazil", "description": "Brazil's premier golf club", "latitude": -23.6000, "longitude": -46.7000},
    {"name": "Campo de Golf del Jockey Club", "city": "Buenos Aires", "region_or_state": "Buenos Aires", "country": "Argentina", "description": "Classic Argentine golf", "latitude": -34.5000, "longitude": -58.5000},
    {"name": "Los Leones Golf Club", "city": "Santiago", "region_or_state": "Santiago Metropolitan", "country": "Chile", "description": "Andes mountain golf", "latitude": -33.4000, "longitude": -70.5000},
    {"name": "Country Club de Bogotá", "city": "Bogotá", "region_or_state": "Bogotá", "country": "Colombia", "description": "High altitude golf", "latitude": 4.7000, "longitude": -74.0000},
    {"name": "Club de Golf La Dehesa", "city": "Santiago", "region_or_state": "Santiago Metropolitan", "country": "Chile", "description": "Mountain course excellence", "latitude": -33.3500, "longitude": -70.5500},
    
    # ADDITIONAL EUROPEAN GEMS
    {"name": "Morfontaine Golf Club", "city": "Senlis", "region_or_state": "Oise", "country": "France", "description": "French golf sanctuary", "latitude": 49.2000, "longitude": 2.6000},
    {"name": "Le Golf National", "city": "Saint-Quentin-en-Yvelines", "region_or_state": "Yvelines", "country": "France", "description": "Ryder Cup venue", "latitude": 48.7000, "longitude": 2.1000},
    {"name": "Club zur Vahr", "city": "Bremen", "region_or_state": "Bremen", "country": "Germany", "description": "Classic German golf", "latitude": 53.1000, "longitude": 8.9000},
    {"name": "Golf Club Crans-sur-Sierre", "city": "Crans-Montana", "region_or_state": "Valais", "country": "Switzerland", "description": "Alpine golf perfection", "latitude": 46.3000, "longitude": 7.5000},
    {"name": "Kennemer Golf Club", "city": "Zandvoort", "region_or_state": "North Holland", "country": "Netherlands", "description": "Links by the sea", "latitude": 52.4000, "longitude": 4.5000},
    {"name": "Real Golf de Pedreña", "city": "Pedreña", "region_or_state": "Cantabria", "country": "Spain", "description": "Seve Ballesteros home course", "latitude": 43.4000, "longitude": -3.9000},
    {"name": "Vilamoura Old Course", "city": "Vilamoura", "region_or_state": "Algarve", "country": "Portugal", "description": "Portuguese golf classic", "latitude": 37.1000, "longitude": -8.1000},
    {"name": "Penha Longa Resort", "city": "Sintra", "region_or_state": "Lisbon", "country": "Portugal", "description": "Atlantic golf course", "latitude": 38.8000, "longitude": -9.4000},
    
    # SCANDINAVIAN DESTINATIONS
    {"name": "Halmstad Golf Club", "city": "Halmstad", "region_or_state": "Halland", "country": "Sweden", "description": "Swedish golf excellence", "latitude": 56.7000, "longitude": 12.9000},
    {"name": "Barseback Golf Club", "city": "Malmö", "region_or_state": "Skåne", "country": "Sweden", "description": "Donald Steel design", "latitude": 55.7000, "longitude": 12.9000},
    {"name": "Royal Copenhagen Golf Club", "city": "Copenhagen", "region_or_state": "Capital Region", "country": "Denmark", "description": "Danish royal golf", "latitude": 55.7000, "longitude": 12.5000},
    {"name": "Oslo Golf Club", "city": "Oslo", "region_or_state": "Oslo", "country": "Norway", "description": "Norwegian golf tradition", "latitude": 59.9000, "longitude": 10.8000},
    {"name": "Helsinki Golf Club", "city": "Helsinki", "region_or_state": "Uusimaa", "country": "Finland", "description": "Nordic golf experience", "latitude": 60.2000, "longitude": 24.9000},
    
    # EASTERN EUROPE & RUSSIA
    {"name": "PGA Golf Club Slovakia", "city": "Bratislava", "region_or_state": "Bratislava", "country": "Slovakia", "description": "Central European golf", "latitude": 48.1000, "longitude": 17.1000},
    {"name": "Golf Resort Karlovy Vary", "city": "Karlovy Vary", "region_or_state": "Karlovy Vary", "country": "Czech Republic", "description": "Spa town golf", "latitude": 50.2000, "longitude": 12.9000},
    {"name": "Penati Golf Resort", "city": "Senica", "region_or_state": "Trnava", "country": "Slovakia", "description": "Nicklaus design", "latitude": 48.7000, "longitude": 17.4000},
    {"name": "Pestovo Golf Club", "city": "Moscow", "region_or_state": "Moscow Oblast", "country": "Russia", "description": "Russian golf pioneer", "latitude": 55.8000, "longitude": 37.4000},
    {"name": "Moscow Country Club", "city": "Moscow", "region_or_state": "Moscow Oblast", "country": "Russia", "description": "Premier Russian golf", "latitude": 55.8500, "longitude": 37.3500},
    
    # INDIAN SUBCONTINENT
    {"name": "Royal Calcutta Golf Club", "city": "Kolkata", "region_or_state": "West Bengal", "country": "India", "description": "World's oldest golf club outside Britain", "latitude": 22.5000, "longitude": 88.3000},
    {"name": "Delhi Golf Club", "city": "New Delhi", "region_or_state": "Delhi", "country": "India", "description": "Historic Indian golf", "latitude": 28.6000, "longitude": 77.2000},
    {"name": "Tollygunge Club", "city": "Kolkata", "region_or_state": "West Bengal", "country": "India", "description": "Colonial golf heritage", "latitude": 22.5000, "longitude": 88.4000},
    {"name": "Royal Colombo Golf Club", "city": "Colombo", "region_or_state": "Western Province", "country": "Sri Lanka", "description": "Sri Lankan golf tradition", "latitude": 6.9000, "longitude": 79.9000},
    {"name": "Karachi Golf Club", "city": "Karachi", "region_or_state": "Sindh", "country": "Pakistan", "description": "Pakistani golf heritage", "latitude": 24.8000, "longitude": 67.0000},
    
    # SOUTHEAST ASIA EXPANSION
    {"name": "Manila Golf Club", "city": "Makati", "region_or_state": "Metro Manila", "country": "Philippines", "description": "Philippine golf tradition", "latitude": 14.5000, "longitude": 121.0000},
    {"name": "Wack Wack Golf Club", "city": "Mandaluyong", "region_or_state": "Metro Manila", "country": "Philippines", "description": "Championship Philippine golf", "latitude": 14.6000, "longitude": 121.0000},
    {"name": "Royal Bangkok Sports Club", "city": "Bangkok", "region_or_state": "Bangkok", "country": "Thailand", "description": "Thai royal golf", "latitude": 13.7000, "longitude": 100.5000},
    {"name": "Alpine Golf Resort", "city": "Chiang Mai", "region_or_state": "Chiang Mai", "country": "Thailand", "description": "Mountain golf Thailand", "latitude": 18.8000, "longitude": 98.9000},
    {"name": "Sentosa Golf Club", "city": "Singapore", "region_or_state": "Singapore", "country": "Singapore", "description": "Island golf paradise", "latitude": 1.2500, "longitude": 103.8000},
    {"name": "Horizon Hills Golf Club", "city": "Johor Bahru", "region_or_state": "Johor", "country": "Malaysia", "description": "Border golf excellence", "latitude": 1.4000, "longitude": 103.6000},
    {"name": "Saujana Golf Club", "city": "Shah Alam", "region_or_state": "Selangor", "country": "Malaysia", "description": "Malaysian championship golf", "latitude": 3.2000, "longitude": 101.5000},
    
    # OCEANIA EXPANSION
    {"name": "Kauri Cliffs", "city": "Matauri Bay", "region_or_state": "Northland", "country": "New Zealand", "description": "Clifftop golf paradise", "latitude": -35.0000, "longitude": 173.9000},
    {"name": "Cape Kidnappers", "city": "Hawke's Bay", "region_or_state": "Hawke's Bay", "country": "New Zealand", "description": "Dramatic cliff golf", "latitude": -39.6000, "longitude": 177.1000},
    {"name": "Tara Iti Golf Club", "city": "Mangawhai", "region_or_state": "Northland", "country": "New Zealand", "description": "Modern links masterpiece", "latitude": -36.1000, "longitude": 174.6000},
    {"name": "New South Wales Golf Club", "city": "Sydney", "region_or_state": "New South Wales", "country": "Australia", "description": "Historic Australian golf", "latitude": -33.9500, "longitude": 151.2500},
    {"name": "Peninsula Kingswood", "city": "Melbourne", "region_or_state": "Victoria", "country": "Australia", "description": "Australian championship venue", "latitude": -38.1000, "longitude": 145.1000},
    {"name": "The National Golf Club", "city": "Melbourne", "region_or_state": "Victoria", "country": "Australia", "description": "Australian golf excellence", "latitude": -38.2000, "longitude": 145.0000},
    
    # CARIBBEAN EXPANSION
    {"name": "Mid Ocean Club", "city": "Tucker's Town", "region_or_state": "St. George's", "country": "Bermuda", "description": "Atlantic island golf", "latitude": 32.3000, "longitude": -64.7000},
    {"name": "Port Royal Golf Course", "city": "Southampton", "region_or_state": "Southampton", "country": "Bermuda", "description": "Public championship golf", "latitude": 32.2500, "longitude": -64.8000},
    {"name": "Four Seasons Golf Course", "city": "St. John's", "region_or_state": "Saint John", "country": "Antigua and Barbuda", "description": "Caribbean golf paradise", "latitude": 17.1000, "longitude": -61.8000},
    {"name": "Sandy Lane Golf Club", "city": "St. Lawrence Gap", "region_or_state": "Christ Church", "country": "Barbados", "description": "Green Monkey course", "latitude": 13.1000, "longitude": -59.6000},
    {"name": "Cabot Links", "city": "Inverness", "region_or_state": "Nova Scotia", "country": "Canada", "description": "True links golf", "latitude": 46.2000, "longitude": -61.1000},
    {"name": "Cabot Cliffs", "city": "Inverness", "region_or_state": "Nova Scotia", "country": "Canada", "description": "Clifftop golf perfection", "latitude": 46.2100, "longitude": -61.1100},
    
    # PACIFIC ISLANDS
    {"name": "Mauna Kea Golf Course", "city": "Waimea", "region_or_state": "Hawaii", "country": "USA", "description": "Big Island golf legend", "latitude": 20.0000, "longitude": -155.8000},
    {"name": "Plantation Course at Kapalua", "city": "Lahaina", "region_or_state": "Hawaii", "country": "USA", "description": "PGA Tour venue", "latitude": 20.9000, "longitude": -156.7000},
    {"name": "Natadola Bay Golf Course", "city": "Natadola", "region_or_state": "Ba", "country": "Fiji", "description": "Tropical island golf", "latitude": -18.0000, "longitude": 177.4000},
    {"name": "Laguna Golf Phuket", "city": "Phuket", "region_or_state": "Phuket", "country": "Thailand", "description": "Tropical golf paradise", "latitude": 8.0000, "longitude": 98.3000},
    
    # CENTRAL ASIA & MONGOLIA  
    {"name": "Ala-Archa Golf Club", "city": "Bishkek", "region_or_state": "Chuy", "country": "Kyrgyzstan", "description": "Mountain golf adventure", "latitude": 42.9000, "longitude": 74.6000},
    {"name": "Nurbek Golf Club", "city": "Almaty", "region_or_state": "Almaty", "country": "Kazakhstan", "description": "Central Asian golf", "latitude": 43.2000, "longitude": 76.9000},
    {"name": "Mount Pleasant Golf Club", "city": "Ulaanbaatar", "region_or_state": "Ulaanbaatar", "country": "Mongolia", "description": "Mongolian steppe golf", "latitude": 47.9000, "longitude": 106.9000},
    
    # ADDITIONAL LUXURY RESORTS
    {"name": "Kiawah Island Golf Resort", "city": "Kiawah Island", "region_or_state": "South Carolina", "country": "USA", "description": "Ocean Course championship", "latitude": 32.6000, "longitude": -80.1000},
    {"name": "TPC Sawgrass", "city": "Ponte Vedra Beach", "region_or_state": "Florida", "country": "USA", "description": "Players Championship venue", "latitude": 30.2000, "longitude": -81.4000},
    {"name": "Bay Hill Club", "city": "Orlando", "region_or_state": "Florida", "country": "USA", "description": "Arnold Palmer's course", "latitude": 28.4000, "longitude": -81.5000},
    {"name": "Muirfield Village Golf Club", "city": "Dublin", "region_or_state": "Ohio", "country": "USA", "description": "Nicklaus design", "latitude": 40.1000, "longitude": -83.1000},
    {"name": "Harbour Town Golf Links", "city": "Hilton Head", "region_or_state": "South Carolina", "country": "USA", "description": "RBC Heritage venue", "latitude": 32.1000, "longitude": -80.8000},
    {"name": "Riviera Country Club", "city": "Pacific Palisades", "region_or_state": "California", "country": "USA", "description": "Genesis Invitational venue", "latitude": 34.0500, "longitude": -118.5000},
    {"name": "Torrey Pines Golf Course", "city": "La Jolla", "region_or_state": "California", "country": "USA", "description": "US Open venue", "latitude": 32.9000, "longitude": -117.2500},
    {"name": "Whistling Straits", "city": "Sheboygan", "region_or_state": "Wisconsin", "country": "USA", "description": "PGA Championship venue", "latitude": 43.8000, "longitude": -87.6000},
    {"name": "Bethpage Black", "city": "Farmingdale", "region_or_state": "New York", "country": "USA", "description": "Public championship golf", "latitude": 40.7000, "longitude": -73.5000},
    {"name": "Chambers Bay", "city": "University Place", "region_or_state": "Washington", "country": "USA", "description": "US Open links venue", "latitude": 47.2000, "longitude": -122.6000},
]

def add_destinations():
    """Add new destinations to the database"""
    print("🏌️ Adding new international golf destinations...")
    print("=" * 60)
    
    added_count = 0
    skipped_count = 0
    errors = []
    
    for dest_data in NEW_DESTINATIONS:
        try:
            # Check if destination already exists (by city and country)
            existing = Destination.objects.filter(
                city=dest_data['city'], 
                country=dest_data['country']
            ).first()
            
            if existing:
                print(f"⚠️  Skipping {dest_data['city']}, {dest_data['country']} - already exists")
                skipped_count += 1
                continue
            
            # Create new destination
            destination = Destination.objects.create(
                name=dest_data['name'],
                city=dest_data['city'],
                region_or_state=dest_data['region_or_state'],
                country=dest_data['country'],
                description=dest_data['description'],
                latitude=Decimal(str(dest_data['latitude'])),
                longitude=Decimal(str(dest_data['longitude'])),
                image_url='',  # Will be populated later if needed
            )
            
            print(f"✅ Added: {destination.name} - {destination.city}, {destination.country}")
            added_count += 1
            
        except Exception as e:
            error_msg = f"Error adding {dest_data.get('city', 'Unknown')}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    print("\n" + "=" * 60)
    print("🎉 Destination addition completed!")
    print(f"📊 Summary:")
    print(f"   • New destinations added: {added_count}")
    print(f"   • Destinations skipped (already exist): {skipped_count}")
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
        added, skipped, errors = add_destinations()
        print(f"\n✨ Process complete! Added {added} destinations, skipped {skipped}, {errors} errors.")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
