#!/usr/bin/env python3
"""
Golf Destination Content Generator

This script generates comprehensive golf destination articles using LLM chains:
1. Topic Generator: Creates relevant questions and topics for a destination
2. Article Generator: Processes topics into full articles
3. Database Uploader: Adds generated content to Django database

Usage:
    python content_generator.py --destination "Tokyo, Japan" --generate-topics
    python content_generator.py --destination "Tokyo, Japan" --generate-article
    python content_generator.py --destination "Tokyo, Japan" --upload
"""

import os
import sys
import json
import argparse
import requests
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
import django
from pathlib import Path

# Add the Django project to Python path
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination
from destinations.management.commands.import_destinations import get_coordinates

@dataclass
class GolfDestination:
    """Represents a golf destination with all necessary data"""
    name: str
    city: str
    region_or_state: str
    country: str
    description: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    image_url: str = ""
    article_content: str = ""

class LLMContentGenerator:
    """Handles LLM API calls for content generation"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            print("⚠️  No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
            print("   Alternatively, you can use any LLM API by modifying the generate_content method.")
    
    def generate_content(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate content using LLM API"""
        if not self.api_key:
            return self._mock_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Error calling LLM API: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response for testing without API key"""
        if "topics and questions" in prompt.lower():
            return """1. Course Rankings & Reviews
2. Best Times to Play & Weather
3. Local Golf Culture & Etiquette
4. Accommodation & Travel Tips
5. Dining & Entertainment
6. Equipment & Pro Shop Recommendations
7. Booking & Pricing Information
8. Transportation & Getting Around"""
        else:
            return f"# Golf Guide for {prompt.split('for')[-1] if 'for' in prompt else 'Destination'}\n\nThis is a mock article generated for testing purposes. Replace with actual LLM-generated content."

class TopicGenerator:
    """Generates relevant topics and questions for golf destinations"""
    
    def __init__(self, llm: LLMContentGenerator):
        self.llm = llm
    
    def generate_topics(self, destination: GolfDestination) -> List[str]:
        """Generate comprehensive topics for a golf destination"""
        prompt = f"""
Generate 8-10 comprehensive topics for a golf destination guide about {destination.city}, {destination.region_or_state}, {destination.country}.

The guide should be practical, engaging, and useful for golfers planning a trip. Include topics that cover:
- Course reviews and rankings
- Local golf culture and customs
- Practical travel information
- Seasonal considerations
- Local amenities and attractions
- Booking and pricing insights

Format as a numbered list. Be specific to the location when possible.

Example format:
1. Course Rankings & Reviews
2. Best Times to Play & Weather Considerations
etc.
"""
        
        response = self.llm.generate_content(prompt, max_tokens=500)
        return self._parse_topics(response)
    
    def _parse_topics(self, response: str) -> List[str]:
        """Parse LLM response into list of topics"""
        topics = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering and clean up
                topic = line
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '-', '*']:
                    if topic.startswith(prefix):
                        topic = topic[len(prefix):].strip()
                        break
                if topic:
                    topics.append(topic)
        return topics

class ArticleGenerator:
    """Generates full articles from topics"""
    
    def __init__(self, llm: LLMContentGenerator):
        self.llm = llm
    
    def generate_article(self, destination: GolfDestination, topics: List[str]) -> str:
        """Generate a comprehensive golf destination article"""
        
        # Create the main prompt
        topics_text = '\n'.join([f"- {topic}" for topic in topics])
        
        prompt = f"""
Write a comprehensive golf destination guide for {destination.city}, {destination.region_or_state}, {destination.country}.

Cover these topics in detail:
{topics_text}

Guidelines:
- Write in a friendly, informative tone for golf enthusiasts
- Include specific course names, prices, and practical details when possible
- Use markdown formatting with headers (##) and bullet points
- Make it 2000-3000 words
- Include a brief introduction and conclusion
- Format course information with bold labels like **Signature Hole:** and **Notable Features:**
- Use numbered headers for major sections like **1. Course Rankings & Reviews**

Start with this structure:
# The {destination.city} Golf Guide: Your Definitive Resource for {destination.region_or_state}'s Links

## Introduction: Welcome to {destination.city} Golf
[Engaging introduction paragraph]

Then cover each topic as a major section with detailed content.
"""
        
        return self.llm.generate_content(prompt, max_tokens=4000)

class ContentUploader:
    """Handles uploading generated content to Django database"""
    
    def upload_destination(self, destination: GolfDestination) -> bool:
        """Upload destination to Django database"""
        try:
            # Check if destination already exists
            existing = Destination.objects.filter(
                city__iexact=destination.city,
                region_or_state__iexact=destination.region_or_state,
                country__iexact=destination.country
            ).first()
            
            if existing:
                print(f"⚠️  Destination {destination.city}, {destination.country} already exists. Updating...")
                existing.name = destination.name
                existing.description = destination.description
                existing.article_content = destination.article_content
                existing.image_url = destination.image_url
                if destination.latitude and destination.longitude:
                    existing.latitude = destination.latitude
                    existing.longitude = destination.longitude
                existing.save()
                return True
            
            # Get coordinates if not provided
            if not destination.latitude or not destination.longitude:
                coords = get_coordinates(destination.city, destination.region_or_state, destination.country)
                if coords:
                    destination.latitude, destination.longitude = coords
                else:
                    print(f"⚠️  Could not get coordinates for {destination.city}, {destination.country}")
                    destination.latitude, destination.longitude = 0.0, 0.0
            
            # Create new destination
            new_dest = Destination.objects.create(
                name=destination.name,
                city=destination.city,
                region_or_state=destination.region_or_state,
                country=destination.country,
                description=destination.description,
                latitude=destination.latitude,
                longitude=destination.longitude,
                image_url=destination.image_url,
                article_content=destination.article_content
            )
            
            print(f"✅ Successfully uploaded: {new_dest.name}")
            print(f"   URL: {new_dest.get_absolute_url()}")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading destination: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Generate golf destination content')
    parser.add_argument('--destination', required=True, help='Destination in format "City, Region, Country"')
    parser.add_argument('--generate-topics', action='store_true', help='Generate topics for the destination')
    parser.add_argument('--generate-article', action='store_true', help='Generate full article')
    parser.add_argument('--upload', action='store_true', help='Upload to database')
    parser.add_argument('--all', action='store_true', help='Run all steps: topics -> article -> upload')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='LLM model to use')
    
    args = parser.parse_args()
    
    # Parse destination
    parts = [p.strip() for p in args.destination.split(',')]
    if len(parts) != 3:
        print("❌ Destination must be in format: 'City, Region, Country'")
        sys.exit(1)
    
    city, region, country = parts
    destination = GolfDestination(
        name=f"{city}, {region}",
        city=city,
        region_or_state=region,
        country=country,
        description=f"Golf destination guide for {city}, {region}"
    )
    
    # Initialize components
    llm = LLMContentGenerator(api_key=args.api_key, model=args.model)
    topic_gen = TopicGenerator(llm)
    article_gen = ArticleGenerator(llm)
    uploader = ContentUploader()
    
    # Create output directory
    output_dir = Path("generated_content")
    output_dir.mkdir(exist_ok=True)
    
    # File paths
    topics_file = output_dir / f"{city}_{region}_{country}_topics.txt"
    article_file = output_dir / f"{city}_{region}_{country}_article.md"
    
    if args.all or args.generate_topics:
        print(f"🔄 Generating topics for {destination.name}, {destination.country}...")
        topics = topic_gen.generate_topics(destination)
        
        # Save topics
        with open(topics_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(topics))
        
        print(f"✅ Generated {len(topics)} topics:")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic}")
        print(f"   Saved to: {topics_file}")
    
    if args.all or args.generate_article:
        # Load topics if they exist
        if topics_file.exists():
            with open(topics_file, 'r', encoding='utf-8') as f:
                topics = [line.strip() for line in f.readlines() if line.strip()]
        else:
            print("❌ No topics file found. Run --generate-topics first.")
            sys.exit(1)
        
        print(f"🔄 Generating article for {destination.name}, {destination.country}...")
        article = article_gen.generate_article(destination, topics)
        destination.article_content = article
        
        # Save article
        with open(article_file, 'w', encoding='utf-8') as f:
            f.write(article)
        
        print(f"✅ Generated article ({len(article)} characters)")
        print(f"   Saved to: {article_file}")
    
    if args.all or args.upload:
        # Load article if it exists
        if article_file.exists():
            with open(article_file, 'r', encoding='utf-8') as f:
                destination.article_content = f.read()
        else:
            print("❌ No article file found. Run --generate-article first.")
            sys.exit(1)
        
        print(f"🔄 Uploading {destination.name}, {destination.country} to database...")
        success = uploader.upload_destination(destination)
        
        if success:
            print("✅ Upload completed successfully!")
        else:
            print("❌ Upload failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
