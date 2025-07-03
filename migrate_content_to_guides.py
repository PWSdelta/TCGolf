#!/usr/bin/env python
"""
Data Migration Script: Move content from Destination to DestinationGuide

This script migrates existing content from:
- Destination.article_content (main field)
- Destination.article_content_multilang (JSON field)

To the new DestinationGuide model structure.
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, DestinationGuide
from django.db import transaction

def migrate_content():
    """Migrate all existing content to DestinationGuide records"""
    print("🚀 Starting content migration...")
    print("=" * 60)
    
    destinations = Destination.objects.all()
    total_destinations = destinations.count()
    total_guides_created = 0
    errors = []
    
    print(f"📊 Found {total_destinations} destinations to process")
    
    with transaction.atomic():
        for i, dest in enumerate(destinations, 1):
            print(f"\n📍 Processing [{i}/{total_destinations}]: {dest.city}, {dest.country}")
            
            guides_created_for_dest = 0
            
            # 1. Check main article_content field (English)
            if dest.article_content and dest.article_content.strip():
                try:
                    guide, created = DestinationGuide.objects.get_or_create(
                        destination=dest,
                        language_code='en',
                        defaults={
                            'title': f"Golf Guide to {dest.city}, {dest.country}",
                            'content': dest.article_content,
                            'meta_description': f"Complete golf guide for {dest.city}, {dest.country}. Discover the best golf courses, tips, and local insights.",
                            'generated_by': 'imported',
                            'generation_model': 'legacy_import',
                            'last_generated_at': dest.created_at if dest.created_at else datetime.now()
                        }
                    )
                    if created:
                        guides_created_for_dest += 1
                        print(f"  ✅ Created English guide from article_content ({len(dest.article_content)} chars)")
                    else:
                        print(f"  ⚠️  English guide already exists")
                except Exception as e:
                    error_msg = f"Error creating English guide for {dest.city}: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            
            # 2. Check multilang field for additional languages
            if dest.article_content_multilang:
                for lang_code, content in dest.article_content_multilang.items():
                    if content and content.strip() and lang_code != 'en':  # Skip EN as we handled it above
                        try:
                            guide, created = DestinationGuide.objects.get_or_create(
                                destination=dest,
                                language_code=lang_code,
                                defaults={
                                    'title': f"Golf Guide to {dest.city}, {dest.country}",
                                    'content': content,
                                    'meta_description': f"Complete golf guide for {dest.city}, {dest.country}",
                                    'generated_by': 'imported',
                                    'generation_model': 'legacy_multilang_import',
                                    'last_generated_at': dest.created_at if dest.created_at else datetime.now()
                                }
                            )
                            if created:
                                guides_created_for_dest += 1
                                print(f"  ✅ Created {lang_code.upper()} guide from multilang field ({len(content)} chars)")
                            else:
                                print(f"  ⚠️  {lang_code.upper()} guide already exists")
                        except Exception as e:
                            error_msg = f"Error creating {lang_code} guide for {dest.city}: {e}"
                            errors.append(error_msg)
                            print(f"  ❌ {error_msg}")
                
                # Handle case where multilang 'en' exists but main article_content doesn't
                if 'en' in dest.article_content_multilang and not (dest.article_content and dest.article_content.strip()):
                    content = dest.article_content_multilang['en']
                    if content and content.strip():
                        try:
                            guide, created = DestinationGuide.objects.get_or_create(
                                destination=dest,
                                language_code='en',
                                defaults={
                                    'title': f"Golf Guide to {dest.city}, {dest.country}",
                                    'content': content,
                                    'meta_description': f"Complete golf guide for {dest.city}, {dest.country}. Discover the best golf courses, tips, and local insights.",
                                    'generated_by': 'imported',
                                    'generation_model': 'legacy_multilang_en_import',
                                    'last_generated_at': dest.created_at if dest.created_at else datetime.now()
                                }
                            )
                            if created:
                                guides_created_for_dest += 1
                                print(f"  ✅ Created English guide from multilang['en'] ({len(content)} chars)")
                        except Exception as e:
                            error_msg = f"Error creating English guide from multilang for {dest.city}: {e}"
                            errors.append(error_msg)
                            print(f"  ❌ {error_msg}")
            
            # 3. Handle destinations with no content
            if guides_created_for_dest == 0:
                if not dest.article_content and not dest.article_content_multilang:
                    print(f"  ⚪ No content found - skipping")
                else:
                    print(f"  ⚠️  Content exists but no guides created")
            
            total_guides_created += guides_created_for_dest
            
            # Progress indicator
            if i % 10 == 0:
                print(f"\n📈 Progress: {i}/{total_destinations} destinations processed, {total_guides_created} guides created")
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed!")
    print(f"📊 Summary:")
    print(f"   • Destinations processed: {total_destinations}")
    print(f"   • Total guides created: {total_guides_created}")
    print(f"   • Average guides per destination: {total_guides_created/total_destinations:.1f}")
    
    if errors:
        print(f"\n⚠️  Errors encountered ({len(errors)}):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   • {error}")
        if len(errors) > 10:
            print(f"   • ... and {len(errors) - 10} more errors")
    
    # Final verification
    final_guide_count = DestinationGuide.objects.count()
    language_distribution = {}
    for guide in DestinationGuide.objects.all():
        lang = guide.language_code
        language_distribution[lang] = language_distribution.get(lang, 0) + 1
    
    print(f"\n📈 Final verification:")
    print(f"   • Total DestinationGuide records: {final_guide_count}")
    print(f"   • Language distribution:")
    for lang, count in sorted(language_distribution.items()):
        print(f"     - {lang.upper()}: {count} guides")
    
    return total_guides_created, len(errors)

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    # Check for destinations with content but no guides
    destinations_with_content = Destination.objects.filter(
        models.Q(article_content__isnull=False) & ~models.Q(article_content='')
    ).count()
    
    destinations_with_guides = Destination.objects.filter(guides__isnull=False).distinct().count()
    
    print(f"   • Destinations with original content: {destinations_with_content}")
    print(f"   • Destinations with guides: {destinations_with_guides}")
    
    # Sample a few to check content matches
    sample_destinations = Destination.objects.filter(guides__isnull=False).distinct()[:3]
    
    print(f"\n📋 Sample content verification:")
    for dest in sample_destinations:
        guides = dest.guides.all()
        print(f"   • {dest.city}, {dest.country}:")
        for guide in guides:
            original_len = len(dest.article_content or "")
            guide_len = len(guide.content)
            match_status = "✅" if abs(original_len - guide_len) < 100 else "⚠️"
            print(f"     - {guide.language_code.upper()}: {guide_len} chars {match_status}")

if __name__ == "__main__":
    try:
        from django.db import models
        guides_created, error_count = migrate_content()
        verify_migration()
        
        print(f"\n✨ Migration complete! Created {guides_created} guides with {error_count} errors.")
        
        if error_count == 0:
            print("🎯 All content migrated successfully!")
        else:
            print("⚠️  Some errors occurred - check the output above.")
            
    except Exception as e:
        print(f"\n💥 Fatal error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
