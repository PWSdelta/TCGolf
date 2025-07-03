#!/usr/bin/env python3
"""
Batch Golf Destination Generator

This script processes multiple destinations from a list and generates content for all of them.
Great for scaling up content generation across many international golf destinations.

Usage:
    python batch_generator.py --input destinations.txt --all
    python batch_generator.py --input destinations.txt --generate-topics-only
"""

import os
import sys
import time
import argparse
from pathlib import Path
import subprocess

def read_destinations(file_path: str) -> list:
    """Read destinations from a text file"""
    destinations = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    destinations.append(line)
        return destinations
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []

def run_content_generator(destination: str, action: str, api_key: str = None) -> bool:
    """Run the content generator for a single destination"""
    cmd = ['python', 'content_generator.py', '--destination', destination]
    
    if action == 'all':
        cmd.append('--all')
    elif action == 'topics':
        cmd.append('--generate-topics')
    elif action == 'article':
        cmd.append('--generate-article')
    elif action == 'upload':
        cmd.append('--upload')
    
    if api_key:
        cmd.extend(['--api-key', api_key])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"✅ Success: {destination}")
            return True
        else:
            print(f"❌ Failed: {destination}")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {destination} (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {destination} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Batch generate golf destination content')
    parser.add_argument('--input', required=True, help='Input file with destinations (one per line)')
    parser.add_argument('--all', action='store_true', help='Run all steps for each destination')
    parser.add_argument('--generate-topics-only', action='store_true', help='Only generate topics')
    parser.add_argument('--generate-articles-only', action='store_true', help='Only generate articles')
    parser.add_argument('--upload-only', action='store_true', help='Only upload existing content')
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--delay', type=int, default=2, help='Delay between requests (seconds)')
    parser.add_argument('--start-from', type=int, default=0, help='Start from destination number (0-based)')
    
    args = parser.parse_args()
    
    # Determine action
    if args.all:
        action = 'all'
    elif args.generate_topics_only:
        action = 'topics'
    elif args.generate_articles_only:
        action = 'article'
    elif args.upload_only:
        action = 'upload'
    else:
        print("❌ Must specify one action: --all, --generate-topics-only, --generate-articles-only, or --upload-only")
        sys.exit(1)
    
    # Read destinations
    destinations = read_destinations(args.input)
    if not destinations:
        print("❌ No destinations found in input file")
        sys.exit(1)
    
    # Apply start-from filter
    if args.start_from > 0:
        destinations = destinations[args.start_from:]
        print(f"📍 Starting from destination #{args.start_from + 1}")
    
    print(f"🚀 Processing {len(destinations)} destinations with action: {action}")
    print(f"⏱️  Delay between requests: {args.delay} seconds")
    print("=" * 60)
    
    success_count = 0
    failed_destinations = []
    
    for i, destination in enumerate(destinations, args.start_from + 1):
        print(f"\n📍 [{i}/{len(destinations) + args.start_from}] Processing: {destination}")
        print("-" * 40)
        
        success = run_content_generator(destination, action, args.api_key)
        
        if success:
            success_count += 1
        else:
            failed_destinations.append(destination)
        
        # Add delay between requests to be respectful to APIs
        if i < len(destinations) + args.start_from:
            print(f"⏱️  Waiting {args.delay} seconds...")
            time.sleep(args.delay)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {len(failed_destinations)}")
    print(f"📈 Success Rate: {success_count / len(destinations) * 100:.1f}%")
    
    if failed_destinations:
        print(f"\n❌ Failed destinations:")
        for dest in failed_destinations:
            print(f"   - {dest}")
        
        # Save failed destinations for retry
        failed_file = Path("failed_destinations.txt")
        with open(failed_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(failed_destinations))
        print(f"\n💾 Failed destinations saved to: {failed_file}")
        print("   You can retry with: python batch_generator.py --input failed_destinations.txt --all")

if __name__ == "__main__":
    main()
