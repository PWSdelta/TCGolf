#!/usr/bin/env python
"""
GolfPlex CityGuide Content Generation Worker

This script generates comprehensive city guides using Ollama LLM.
It creates structured content for all sections of the CityGuide model:
- Overview
- Neighborhoods
- Attractions  
- Dining
- Nightlife
- Shopping
- Transportation
- Accommodation
- Seasonal Guide
- Practical Info
- Golf Summary

Usage:
    python worker_cityguides.py --model llama3.1 --max-items 10
"""

import requests
import json
import argparse
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class CityGuideWorker:
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434", 
                 output_dir: str = "generated_cityguides", 
                 model_name: str = "llama3.1"):
        self.ollama_url = ollama_url.rstrip('/')
        self.model_name = model_name
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Timing tracking
        self.worker_start_time = None
        self.generation_timings = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Test Ollama connection
        self.test_ollama_connection()
        
        # Language names for prompts
        self.language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French', 
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
    
    def test_ollama_connection(self):
        """Test connection to Ollama and check if model is available"""
        try:
            print(f"🔌 Testing connection to Ollama at {self.ollama_url}...")
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            print(f"📋 Found {len(model_names)} available models")
            
            if not any(self.model_name in name for name in model_names):
                print(f"⚠️  Model '{self.model_name}' not found in available models.")
                print(f"💡 You can pull the model with: ollama pull {self.model_name}")
                print("🔄 Attempting to continue anyway (model might be available)...")
            else:
                print(f"✅ Connected to Ollama, using model: {self.model_name}")
                
        except requests.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
            print(f"Error: {e}")
            print(f"💡 Make sure Ollama is running: ollama serve")
            raise e
    
    def call_ollama(self, prompt: str, system_prompt: str = "", section_name: str = "") -> str:
        """Make a request to Ollama API with streaming output"""
        try:
            section_display = f" ({section_name})" if section_name else ""
            print(f"🤖 Calling Ollama{section_display}...")
            start_time = time.time()
            
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=600,  # 10 minute timeout
                stream=True
            )
            response.raise_for_status()
            
            generated_text = ""
            chars_streamed = 0
            last_progress_update = time.time()
            
            print(f"📝 Streaming content{section_display}...")
            print("─" * 60)
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            text_chunk = chunk['response']
                            generated_text += text_chunk
                            chars_streamed += len(text_chunk)
                            
                            # Stream output to console
                            print(text_chunk, end='', flush=True)
                            
                            # Show progress every 2 seconds
                            current_time = time.time()
                            if current_time - last_progress_update > 2.0:
                                elapsed = current_time - start_time
                                chars_per_sec = chars_streamed / elapsed if elapsed > 0 else 0
                                print(f"\n[📊 {chars_streamed} chars, {chars_per_sec:.0f} chars/sec]", end='', flush=True)
                                last_progress_update = current_time
                        
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            print("\n" + "─" * 60)
            print(f"✅ Generation complete{section_display}!")
            print(f"⏱️  Time: {generation_time:.1f}s")
            print(f"📊 Length: {len(generated_text)} chars ({len(generated_text.split())} words)")
            print(f"🚀 Speed: {len(generated_text)/generation_time:.0f} chars/sec")
            
            return generated_text.strip()
            
        except requests.RequestException as e:
            print(f"❌ Ollama API error{section_display}: {e}")
            return ""
        except Exception as e:
            print(f"❌ Unexpected error{section_display}: {e}")
            return ""

    def generate_overview(self, city: str, region: str, country: str, language: str = 'en') -> str:
        """Generate city overview section"""
        system_prompt = "You are a professional travel writer creating comprehensive city guides."
        
        prompt = f"""Write an engaging overview for a city guide about {city}, {region}, {country}.

REQUIREMENTS:
- 150-250 words
- Capture the essence and personality of the city
- Mention key highlights that make it special
- Write in an engaging, travel guide style
- Focus on what makes this destination unique
- Include cultural, historical, or geographical context

Write only the overview text, no headers or formatting."""
        
        return self.call_ollama(prompt, system_prompt, "Overview")

    def generate_neighborhoods(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate neighborhoods section with structured data"""
        system_prompt = "You are a local expert creating detailed neighborhood guides for travelers."
        
        prompt = f"""Create a comprehensive neighborhoods guide for {city}, {region}, {country}.

REQUIREMENTS:
- Identify 3-6 key neighborhoods/districts
- For each neighborhood provide: description, highlights (3-4 items), best_for
- Focus on areas tourists and visitors would find interesting
- Include both touristy and authentic local areas
- Each description should be 2-3 sentences

FORMAT: Return as valid JSON with this structure:
{{
  "neighborhood_name": {{
    "description": "2-3 sentence description",
    "highlights": ["highlight 1", "highlight 2", "highlight 3"],
    "best_for": "brief description of what this area is best for"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Neighborhoods")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse neighborhoods JSON, returning empty dict")
            return {}

    def generate_attractions(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate attractions section with structured data"""
        system_prompt = "You are a travel expert specializing in must-see attractions and experiences."
        
        prompt = f"""Create a comprehensive attractions guide for {city}, {region}, {country}.

REQUIREMENTS:
- Identify 4-8 must-see attractions and experiences
- Include mix of: historical sites, cultural attractions, natural features, unique experiences
- For each attraction provide: description, category, tips
- Each description should be 2-3 sentences
- Categories: History/Culture, Nature/Recreation, Architecture, Museums, Entertainment, etc.

FORMAT: Return as valid JSON with this structure:
{{
  "attraction_name": {{
    "description": "2-3 sentence description of the attraction",
    "category": "category type",
    "tips": "practical tip for visitors"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Attractions")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse attractions JSON, returning empty dict")
            return {}

    def generate_dining(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate dining section with structured data"""
        system_prompt = "You are a food and dining expert creating restaurant guides for travelers."
        
        prompt = f"""Create a comprehensive dining guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 4-8 notable restaurants/dining experiences
- Mix of: fine dining, local specialties, casual favorites, unique experiences
- For each place provide: description, cuisine_type, price_range
- Price ranges: $ (budget), $$ (moderate), $$$ (upscale), $$$$ (luxury)
- Focus on places that represent the local food culture

FORMAT: Return as valid JSON with this structure:
{{
  "restaurant_name": {{
    "description": "2-3 sentence description highlighting what makes it special",
    "cuisine_type": "type of cuisine",
    "price_range": "$, $$, $$$, or $$$$"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Dining")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse dining JSON, returning empty dict")
            return {}

    def generate_nightlife(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate nightlife section with structured data"""
        system_prompt = "You are a nightlife expert creating guides for evening entertainment."
        
        prompt = f"""Create a nightlife guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 3-6 notable nightlife venues/experiences
- Mix of: bars, clubs, live music venues, cultural evening activities
- For each venue provide: description, type, atmosphere
- Types: Bar, Nightclub, Live Music, Theater, Cultural, etc.
- Consider different preferences and age groups

FORMAT: Return as valid JSON with this structure:
{{
  "venue_name": {{
    "description": "2-3 sentence description of the venue and experience",
    "type": "venue type",
    "atmosphere": "brief description of the vibe/atmosphere"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Nightlife")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse nightlife JSON, returning empty dict")
            return {}

    def generate_shopping(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate shopping section with structured data"""
        system_prompt = "You are a shopping and retail expert creating guides for travelers."
        
        prompt = f"""Create a shopping guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 3-6 notable shopping areas/experiences
- Mix of: markets, shopping districts, specialty stores, local crafts
- For each place provide: description, specialty, price_range
- Price ranges: $ (budget), $$ (moderate), $$$ (upscale), $$$$ (luxury)
- Include both tourist shopping and authentic local experiences

FORMAT: Return as valid JSON with this structure:
{{
  "shopping_area_name": {{
    "description": "2-3 sentence description of what you can find there",
    "specialty": "what this place specializes in",
    "price_range": "$, $$, $$$, or $$$$"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Shopping")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse shopping JSON, returning empty dict")
            return {}

    def generate_transportation(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate transportation section with structured data"""
        system_prompt = "You are a transportation expert helping travelers navigate cities."
        
        prompt = f"""Create a transportation guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 3-6 transportation options for getting around
- Cover: public transport, taxis, walking, bikes, etc.
- For each option provide: description, cost, tips
- Include practical information for tourists
- Consider accessibility and convenience

FORMAT: Return as valid JSON with this structure:
{{
  "transport_type": {{
    "description": "2-3 sentence description of this transport option",
    "cost": "typical cost or cost structure",
    "tips": "practical tip for using this transport"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Transportation")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse transportation JSON, returning empty dict")
            return {}

    def generate_accommodation(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate accommodation section with structured data"""
        system_prompt = "You are a hospitality expert creating accommodation guides for travelers."
        
        prompt = f"""Create an accommodation guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 3-6 accommodation options/areas
- Mix of: luxury hotels, boutique properties, budget options, unique stays
- For each option provide: description, area, price_range
- Price ranges: $ (budget), $$ (moderate), $$$ (upscale), $$$$ (luxury)
- Consider different traveler needs and budgets

FORMAT: Return as valid JSON with this structure:
{{
  "property_name_or_area": {{
    "description": "2-3 sentence description of accommodation or area",
    "area": "neighborhood or area name",
    "price_range": "$, $$, $$$, or $$$$"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse accommodation JSON, returning empty dict")
            return {}

    def generate_seasonal_guide(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate seasonal guide section with structured data"""
        system_prompt = "You are a travel expert specializing in seasonal travel planning."
        
        prompt = f"""Create a seasonal travel guide for {city}, {region}, {country}.

REQUIREMENTS:
- Cover all seasons, months, or distinct travel periods
- For each season provide: weather, activities, events
- Include practical information about when to visit
- Consider climate, tourist seasons, local events

FORMAT: Return as valid JSON with this structure:
{{
  "season_name": {{
    "weather": "brief description of weather conditions",
    "activities": "recommended activities for this season",
    "events": "notable events or festivals during this time"
  }}
}}

Use seasons like: Spring, Summer, Fall, Winter OR Dry Season, Wet Season, etc. as appropriate.

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Seasonal Guide")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse seasonal guide JSON, returning empty dict")
            return {}

    def generate_practical_info(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate practical information section with structured data"""
        system_prompt = "You are a travel expert providing practical information for international travelers."
        
        prompt = f"""Create a practical information guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 4-8 practical categories
- Categories like: Language, Currency, Safety, Tipping, Best Time to Visit, Getting There, etc.
- For each category provide: details, tips
- Focus on information international travelers need

FORMAT: Return as valid JSON with this structure:
{{
  "category_name": {{
    "details": "factual information about this category",
    "tips": "practical tip or advice"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Practical Info")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse practical info JSON, returning empty dict")
            return {}

    def generate_golf_summary(self, city: str, region: str, country: str, language: str = 'en') -> str:
        """Generate golf summary section"""
        system_prompt = "You are a golf travel expert connecting city travel with golf experiences."
        
        prompt = f"""Write a golf summary for {city}, {region}, {country}.

REQUIREMENTS:
- 100-150 words
- Briefly describe golf opportunities in/near the city
- Mention course types, notable designers if known
- Connect golf with the city experience
- Include a call-to-action link to full golf guide
- Keep it engaging but concise

End with: <a href="#" class="golf-link">Explore {city}'s complete golf guide →</a>

Write only the golf summary text with the link."""
        
        return self.call_ollama(prompt, system_prompt, "Golf Summary")

    def generate_hidden_gems(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate hidden gems section with off-the-beaten-path discoveries"""
        system_prompt = "You are a local insider and travel expert who knows the secret spots that most tourists never discover."
        
        prompt = f"""Create a hidden gems guide for {city}, {region}, {country}.

REQUIREMENTS:
- Include 3-5 lesser-known, off-the-beaten-path places/experiences
- Focus on authentic, local spots that tourists rarely find
- Avoid major tourist attractions - these should be genuine hidden gems
- For each gem provide: description, why_special, insider_tip
- Include mix of: secret viewpoints, local hangouts, hidden restaurants, unique experiences, etc.
- These should feel like insider knowledge from a local friend

FORMAT: Return as valid JSON with this structure:
{{
  "hidden_gem_name": {{
    "description": "2-3 sentence description of this hidden gem",
    "why_special": "what makes this place special and unique",
    "insider_tip": "practical insider tip for finding or experiencing it"
  }}
}}

Return only valid JSON, no other text."""
        
        response = self.call_ollama(prompt, system_prompt, "Hidden Gems")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse hidden gems JSON, returning empty dict")
            return {}

    def generate_city_guide(self, city: str, region: str, country: str, language: str = 'en') -> Dict[str, Any]:
        """Generate complete city guide with all sections"""
        print(f"\n🏙️  Generating complete city guide for {city}, {country}")
        print("=" * 70)
        start_time = time.time()
        
        # Define all sections to generate
        sections = [
            ("overview", "📝 Overview"),
            ("neighborhoods", "🏘️  Neighborhoods"), 
            ("attractions", "🎯 Attractions"),
            ("dining", "🍽️  Dining"),
            ("nightlife", "🌙 Nightlife"),
            ("shopping", "🛍️  Shopping"),
            ("transportation", "🚌 Transportation"),
            ("accommodation", "🏨 Accommodation"),
            ("seasonal_guide", "🌡️  Seasonal Guide"),
            ("practical_info", "ℹ️  Practical Info"),
            ("hidden_gems", "💎 Hidden Gems"),
            ("golf_summary", "⛳ Golf Summary")
        ]
        
        city_guide = {}
        
        try:
            for i, (section_key, section_name) in enumerate(sections, 1):
                print(f"\n{section_name} ({i}/{len(sections)})")
                print("─" * 40)
                
                section_start = time.time()
                
                if section_key == "overview":
                    result = self.generate_overview(city, region, country, language)
                elif section_key == "neighborhoods":
                    result = self.generate_neighborhoods(city, region, country, language)
                elif section_key == "attractions":
                    result = self.generate_attractions(city, region, country, language)
                elif section_key == "dining":
                    result = self.generate_dining(city, region, country, language)
                elif section_key == "nightlife":
                    result = self.generate_nightlife(city, region, country, language)
                elif section_key == "shopping":
                    result = self.generate_shopping(city, region, country, language)
                elif section_key == "transportation":
                    result = self.generate_transportation(city, region, country, language)
                elif section_key == "accommodation":
                    result = self.generate_accommodation(city, region, country, language)
                elif section_key == "seasonal_guide":
                    result = self.generate_seasonal_guide(city, region, country, language)
                elif section_key == "practical_info":
                    result = self.generate_practical_info(city, region, country, language)
                elif section_key == "golf_summary":
                    result = self.generate_golf_summary(city, region, country, language)
                
                city_guide[section_key] = result
                
                section_time = time.time() - section_start
                
                # Show section completion stats
                if isinstance(result, dict):
                    print(f"✅ {section_name} complete: {len(result)} items ({section_time:.1f}s)")
                elif isinstance(result, str):
                    words = len(result.split())
                    print(f"✅ {section_name} complete: {words} words ({section_time:.1f}s)")
                
                # Show overall progress
                progress = (i / len(sections)) * 100
                elapsed = time.time() - start_time
                estimated_total = elapsed / (i / len(sections)) if i > 0 else 0
                remaining = estimated_total - elapsed
                
                print(f"📊 Overall progress: {progress:.1f}% ({i}/{len(sections)}) - ETA: {remaining/60:.1f} min")
            
            # Add metadata
            city_guide.update({
                'meta_description': f"Complete {city} travel guide: attractions, dining, nightlife, and travel tips for {city}, {country}.",
                'language_code': language,
                'is_published': True,
                'is_featured': False
            })
            
            generation_time = time.time() - start_time
            
            # Calculate word count
            total_words = self._calculate_word_count(city_guide)
            
            print(f"\n" + "=" * 70)
            print(f"🎉 CITY GUIDE COMPLETE FOR {city.upper()}, {country.upper()}!")
            print(f"⏱️  Total generation time: {generation_time:.1f} seconds ({generation_time/60:.1f} minutes)")
            print(f"📊 Total content: {total_words:,} words")
            print(f"📖 Estimated reading time: {max(1, round(total_words / 200))} minutes")
            print(f"🚀 Average speed: {total_words/generation_time:.0f} words/second")
            
            # Track timing
            self.generation_timings.append({
                'city': f"{city}, {country}",
                'language': language,
                'generation_time': generation_time,
                'word_count': total_words,
                'timestamp': datetime.now().isoformat()
            })
            
            return city_guide
            
        except Exception as e:
            print(f"❌ Error generating city guide for {city}: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _calculate_word_count(self, city_guide: Dict[str, Any]) -> int:
        """Calculate total word count across all content sections"""
        total_words = 0
        
        # Count text fields
        if city_guide.get('overview'):
            total_words += len(city_guide['overview'].split())
        if city_guide.get('golf_summary'):
            total_words += len(city_guide['golf_summary'].split())
            
        # Count JSON field content
        json_fields = ['neighborhoods', 'attractions', 'dining', 'nightlife', 
                      'shopping', 'transportation', 'accommodation', 
                      'seasonal_guide', 'practical_info']
        
        for field in json_fields:
            if city_guide.get(field):
                total_words += self._count_words_in_json(city_guide[field])
                
        return total_words
    
    def _count_words_in_json(self, data: Any) -> int:
        """Recursively count words in JSON data structure"""
        if isinstance(data, dict):
            return sum(self._count_words_in_json(value) for value in data.values())
        elif isinstance(data, list):
            return sum(self._count_words_in_json(item) for item in data)
        elif isinstance(data, str):
            return len(data.split())
        return 0

    def save_city_guide(self, city: str, region: str, country: str, city_guide: Dict[str, Any]):
        """Save generated city guide to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city.replace(' ', '_')}_{country.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        output_data = {
            'destination': {
                'city': city,
                'region': region,
                'country': country
            },
            'city_guide': city_guide,
            'generated_at': datetime.now().isoformat(),
            'worker_version': '1.0'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved city guide to: {filepath}")
        return filepath

    def test_generate_sample(self):
        """Generate a sample city guide for testing"""
        print("🧪 Testing city guide generation with sample data...")
        
        # Use a well-known city for testing
        test_city = "Barcelona"
        test_region = "Catalonia" 
        test_country = "Spain"
        
        city_guide = self.generate_city_guide(test_city, test_region, test_country)
        
        if city_guide:
            self.save_city_guide(test_city, test_region, test_country, city_guide)
            print(f"✅ Sample generation successful!")
            
            # Print section summary
            print("\n📋 Generated sections:")
            for section, content in city_guide.items():
                if isinstance(content, dict):
                    print(f"   {section}: {len(content)} items")
                elif isinstance(content, str):
                    words = len(content.split())
                    print(f"   {section}: {words} words")
                else:
                    print(f"   {section}: {type(content)}")
        else:
            print("❌ Sample generation failed")

    def print_timing_summary(self):
        """Print timing statistics"""
        if not self.generation_timings:
            return
            
        total_time = sum(t['generation_time'] for t in self.generation_timings)
        avg_time = total_time / len(self.generation_timings)
        total_words = sum(t['word_count'] for t in self.generation_timings)
        avg_words = total_words / len(self.generation_timings)
        
        fastest = min(self.generation_timings, key=lambda x: x['generation_time'])
        slowest = max(self.generation_timings, key=lambda x: x['generation_time'])
        
        print(f"\n📊 Generation Statistics:")
        print(f"   Total guides: {len(self.generation_timings)}")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Average time: {avg_time:.1f}s")
        print(f"   Total words: {total_words:,}")
        print(f"   Average words: {avg_words:.0f}")
        print(f"   Fastest: {fastest['generation_time']:.1f}s ({fastest['city']})")
        print(f"   Slowest: {slowest['generation_time']:.1f}s ({slowest['city']})")

def main():
    parser = argparse.ArgumentParser(description='GolfPlex CityGuide Content Generation Worker')
    parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama API URL')
    parser.add_argument('--model', default='llama3.1', help='Ollama model name')
    parser.add_argument('--output-dir', default='generated_cityguides', help='Output directory for JSON files')
    parser.add_argument('--test', action='store_true', help='Run sample generation test')
    parser.add_argument('--max-items', type=int, help='Maximum guides to generate')
    
    args = parser.parse_args()
    
    print(f"🏙️  CityGuide Worker Starting...")
    print(f"   Ollama URL: {args.ollama_url}")
    print(f"   Model: {args.model}")
    print(f"   Output dir: {args.output_dir}")
    
    worker = CityGuideWorker(
        ollama_url=args.ollama_url,
        output_dir=args.output_dir,
        model_name=args.model
    )
    
    try:
        if args.test:
            worker.test_generate_sample()
        else:
            print("💡 Use --test to run sample generation")
            print("💡 This worker generates structured city guide content using Ollama")
        
        worker.print_timing_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped by user")
    except Exception as e:
        print(f"\n❌ Worker error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
