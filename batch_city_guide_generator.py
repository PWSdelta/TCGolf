#!/usr/bin/env python
"""
Batch City Guide Generator
Simple interface for generating city guides in bulk
"""
import os
import django
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

def generate_all_guides():
    """Generate city guides for ALL destinations that don't have them"""
    
    print("🌍 Complete City Guide Generator")
    print("=" * 40)
    
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
        print("✅ All destinations already have city guides!")
        return
    
    print(f"\n🚀 Will generate {len(destinations_without_guides)} city guides automatically...")
    print("   (No confirmation needed - running continuously until complete)")
    
    # Auto-confirm - no user input needed
    confirm = 'y'
    
    # Import the generator
    from city_guide_generator import CityGuideGenerator
    
    generator = CityGuideGenerator()
    
    print(f"\n🚀 Starting continuous generation...")
    success_count = 0
    error_count = 0
    
    for i, dest in enumerate(destinations_without_guides, 1):
        print(f"\n📝 {i}/{len(destinations_without_guides)}: Generating guide for {dest.city}, {dest.country}...")
        
        try:
            guide = generator.generate_city_guide(dest, 'en')
            if guide:
                success_count += 1
                print(f"   ✅ Created guide: {guide.word_count} words, {guide.get_reading_time()} min read")
                print(f"   🔗 URL: {guide.get_absolute_url()}")
                
                # Show progress every 10 guides
                if i % 10 == 0:
                    remaining = len(destinations_without_guides) - i
                    print(f"\n📊 Progress Update: {i}/{len(destinations_without_guides)} complete ({remaining} remaining)")
            else:
                error_count += 1
                print(f"   ❌ Failed to create guide")
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error: {e}")
            # Continue processing even if one fails
            continue
    
    print(f"\n🎉 Complete Generation Finished!")
    print(f"   ✅ Success: {success_count}/{len(destinations_without_guides)} guides created")
    print(f"   ❌ Failed: {error_count}")
    
    # Show comprehensive final stats
    total_guides = CityGuide.objects.count()
    total_destinations = Destination.objects.count()
    coverage = (total_guides / total_destinations) * 100 if total_destinations > 0 else 0
    
    print(f"\n📊 Final Stats:")
    print(f"   🌍 Total destinations: {total_destinations}")
    print(f"   📚 Total city guides: {total_guides}")
    print(f"   📈 Coverage: {coverage:.1f}%")
    
    if coverage == 100:
        print(f"   🎯 TARGET ACHIEVED: All destinations now have city guides!")
    else:
        remaining = total_destinations - total_guides
        print(f"   🔄 Remaining: {remaining} destinations still need guides")
    
    # Show recent guides
    recent_guides = CityGuide.objects.order_by('-created_at')[:10]
    print(f"\n🆕 Most Recent City Guides:")
    for guide in recent_guides:
        print(f"   • {guide.destination.city}, {guide.destination.country} ({guide.language_code.upper()})")
        print(f"     {guide.word_count} words, {guide.get_reading_time()} min read")

def generate_sample_guides():
    """Generate sample city guides for testing (deprecated - use generate_all_guides)"""
    print("ℹ️  This function is deprecated. Use 'Generate ALL city guides' instead.")
    print("   Redirecting to complete generation...")
    generate_all_guides()

def generate_multilingual_guides():
    """Generate guides in multiple languages"""
    
    print("🌐 Multilingual City Guide Generator")
    print("=" * 40)
    
    # Get destinations with existing English guides
    destinations_with_en_guides = []
    for guide in CityGuide.objects.filter(language_code='en'):
        destinations_with_en_guides.append(guide.destination)
    
    if not destinations_with_en_guides:
        print("❌ No English city guides found. Generate English guides first.")
        return
    
    print(f"📍 Found {len(destinations_with_en_guides)} destinations with English guides")
    
    # Language selection
    available_languages = ['es', 'fr', 'de', 'it', 'pt']
    print(f"\nAvailable languages: {', '.join(available_languages)}")
    
    language = input("Enter language code (es/fr/de/it/pt): ").strip().lower()
    
    if language not in available_languages:
        print(f"❌ Invalid language. Available: {', '.join(available_languages)}")
        return
    
    # Check which destinations need this language
    destinations_needing_lang = []
    for dest in destinations_with_en_guides:
        if not CityGuide.objects.filter(destination=dest, language_code=language).exists():
            destinations_needing_lang.append(dest)
    
    if not destinations_needing_lang:
        print(f"✅ All destinations already have {language.upper()} guides!")
        return
    
    print(f"\n📍 {len(destinations_needing_lang)} destinations need {language.upper()} guides:")
    for i, dest in enumerate(destinations_needing_lang[:5], 1):
        print(f"   {i}. {dest.city}, {dest.country}")
    
    if len(destinations_needing_lang) > 5:
        print(f"   ... and {len(destinations_needing_lang) - 5} more")
    
    # Confirm generation
    confirm = input(f"\nGenerate {language.upper()} guides for {len(destinations_needing_lang)} destinations? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Import the generator
    from city_guide_generator import CityGuideGenerator
    
    generator = CityGuideGenerator()
    
    print(f"\n🚀 Starting {language.upper()} guide generation...")
    success_count = 0
    
    for i, dest in enumerate(destinations_needing_lang, 1):
        print(f"\n📝 {i}/{len(destinations_needing_lang)}: Generating {language.upper()} guide for {dest.city}...")
        
        try:
            guide = generator.generate_city_guide(dest, language)
            if guide:
                success_count += 1
                print(f"   ✅ Created guide: {guide.word_count} words, {guide.get_reading_time()} min read")
                print(f"   🔗 URL: {guide.get_absolute_url()}")
            else:
                print(f"   ❌ Failed to create guide")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 {language.upper()} Generation Complete!")
    print(f"   ✅ Success: {success_count}/{len(destinations_needing_lang)} guides created")

def show_city_guide_stats():
    """Show comprehensive city guide statistics"""
    
    print("📊 City Guide Statistics")
    print("=" * 40)
    
    # Basic stats
    total_destinations = Destination.objects.count()
    total_guides = CityGuide.objects.count()
    
    print(f"🌍 Total destinations: {total_destinations}")
    print(f"📚 Total city guides: {total_guides}")
    
    if total_destinations > 0:
        coverage = (total_guides / total_destinations) * 100
        print(f"📈 Coverage: {coverage:.1f}%")
    
    # Language breakdown
    print(f"\n🗣️  Language Breakdown:")
    languages = CityGuide.objects.values_list('language_code', flat=True)
    from collections import Counter
    lang_counts = Counter(languages)
    
    for lang, count in lang_counts.items():
        print(f"   {lang.upper()}: {count} guides")
    
    # Featured guides
    featured_count = CityGuide.objects.filter(is_featured=True).count()
    print(f"\n⭐ Featured guides: {featured_count}")
    
    # Word count stats
    guides_with_words = CityGuide.objects.filter(word_count__gt=0)
    if guides_with_words.exists():
        total_words = sum(guide.word_count for guide in guides_with_words)
        avg_words = total_words / guides_with_words.count()
        print(f"\n📝 Content Statistics:")
        print(f"   Total words: {total_words:,}")
        print(f"   Average words per guide: {avg_words:.0f}")
        print(f"   Estimated total reading time: {total_words // 200} minutes")
    
    # Top guides by word count
    top_guides = CityGuide.objects.order_by('-word_count')[:5]
    print(f"\n🏆 Top Guides by Word Count:")
    for i, guide in enumerate(top_guides, 1):
        print(f"   {i}. {guide.destination.city}, {guide.destination.country} ({guide.language_code.upper()})")
        print(f"      {guide.word_count} words, {guide.get_reading_time()} min read")
    
    # Recent guides
    recent_guides = CityGuide.objects.order_by('-created_at')[:5]
    print(f"\n🆕 Most Recent Guides:")
    for guide in recent_guides:
        print(f"   • {guide.destination.city}, {guide.destination.country} ({guide.language_code.upper()})")
        print(f"     Created: {guide.created_at.strftime('%Y-%m-%d %H:%M')}")

def main():
    """Main menu for batch city guide generation"""
    
    print("🌍 City Guide Management System")
    print("=" * 40)
    
    # Show current status first
    total_destinations = Destination.objects.count()
    total_guides = CityGuide.objects.count()
    remaining = total_destinations - total_guides
    
    print(f"\n📊 Current Status:")
    print(f"   🌍 Total destinations: {total_destinations}")
    print(f"   📚 Total city guides: {total_guides}")
    print(f"   🎯 Remaining to generate: {remaining}")
    
    if remaining == 0:
        print("   ✅ ALL DESTINATIONS HAVE CITY GUIDES!")
    else:
        print(f"   📈 Coverage: {(total_guides/total_destinations)*100:.1f}%")
    
    while True:
        print("\nOptions:")
        print("1. Generate ALL missing city guides (AUTO-RUN)")
        print("2. Generate multilingual guides")
        print("3. Show city guide statistics")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            generate_all_guides()
        elif choice == '2':
            generate_multilingual_guides()
        elif choice == '3':
            show_city_guide_stats()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()
