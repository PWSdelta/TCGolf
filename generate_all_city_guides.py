#!/usr/bin/env python
"""
Generate ALL City Guides - No Menu, Just Run
Automatically generates city guides for all destinations that don't have them.
"""
import os
import django
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

def generate_all_missing_guides():
    """Generate city guides for ALL destinations that don't have them"""
    
    print("🌍 AUTO-GENERATING ALL MISSING CITY GUIDES")
    print("=" * 50)
    
    # Get ALL destinations that don't have city guides
    destinations_without_guides = []
    for dest in Destination.objects.all():
        if not CityGuide.objects.filter(destination=dest, language_code='en').exists():
            destinations_without_guides.append(dest)
    
    total_destinations = Destination.objects.count()
    existing_guides = CityGuide.objects.filter(language_code='en').count()
    
    print(f"📊 Current Status:")
    print(f"   🌍 Total destinations: {total_destinations}")
    print(f"   📚 Existing city guides: {existing_guides}")
    print(f"   🎯 Destinations needing guides: {len(destinations_without_guides)}")
    
    if not destinations_without_guides:
        print("✅ ALL DESTINATIONS ALREADY HAVE CITY GUIDES!")
        print("🎉 MISSION COMPLETE!")
        return
    
    print(f"\n🚀 AUTO-GENERATING {len(destinations_without_guides)} CITY GUIDES...")
    print("   Running continuously until all are complete...")
    
    # Import the generator
    from city_guide_generator import CityGuideGenerator
    
    generator = CityGuideGenerator()
    
    success_count = 0
    error_count = 0
    start_time = datetime.now()
    
    for i, dest in enumerate(destinations_without_guides, 1):
        print(f"\n📝 {i}/{len(destinations_without_guides)}: {dest.city}, {dest.country}")
        
        try:
            guide = generator.generate_city_guide(dest, 'en')
            if guide:
                success_count += 1
                print(f"   ✅ SUCCESS: {guide.word_count} words, {guide.get_reading_time()} min read")
                
                # Show progress every 25 guides
                if i % 25 == 0:
                    remaining = len(destinations_without_guides) - i
                    elapsed = datetime.now() - start_time
                    avg_time = elapsed.total_seconds() / i
                    estimated_remaining = remaining * avg_time / 60
                    print(f"\n📊 PROGRESS: {i}/{len(destinations_without_guides)} complete")
                    print(f"   ⏱️  Elapsed: {elapsed.total_seconds()/60:.1f} min")
                    print(f"   🔮 Estimated remaining: {estimated_remaining:.1f} min")
                    print(f"   📈 Success rate: {(success_count/i)*100:.1f}%")
            else:
                error_count += 1
                print(f"   ❌ FAILED: Could not create guide")
        except Exception as e:
            error_count += 1
            print(f"   ❌ ERROR: {e}")
            continue
    
    # Final results
    total_time = datetime.now() - start_time
    
    print(f"\n🎉 GENERATION COMPLETE!")
    print("=" * 50)
    print(f"   ✅ Successfully created: {success_count} guides")
    print(f"   ❌ Failed: {error_count} guides")
    print(f"   ⏱️  Total time: {total_time.total_seconds()/60:.1f} minutes")
    
    # Final stats
    final_guides = CityGuide.objects.count()
    final_destinations = Destination.objects.count()
    coverage = (final_guides / final_destinations) * 100 if final_destinations > 0 else 0
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   🌍 Total destinations: {final_destinations}")
    print(f"   📚 Total city guides: {final_guides}")
    print(f"   📈 Coverage: {coverage:.1f}%")
    
    if coverage >= 99:
        print(f"\n🎯 TARGET ACHIEVED!")
        print(f"   🏆 All (or nearly all) destinations now have city guides!")
        print(f"   🚀 Ready for production!")
    else:
        remaining = final_destinations - final_guides
        print(f"\n🔄 Status: {remaining} destinations still need guides")
        print(f"   💡 You can run this script again to continue")

if __name__ == "__main__":
    generate_all_missing_guides()
