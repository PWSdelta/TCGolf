#!/usr/bin/env python
"""
AI-Enhanced CityGuide Generator
Uses AI services to generate rich, detailed city guides
"""
import os
import django
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'golfplex.settings')
django.setup()

from destinations.models import Destination, CityGuide

class AICityGuideGenerator:
    """
    AI-enhanced city guide generator using Ollama or OpenAI
    """
    
    def __init__(self, ai_service: str = 'ollama', model: str = 'llama3.1:7b'):
        self.ai_service = ai_service
        self.model = model
        self.ollama_url = 'http://localhost:11434'
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    def test_ai_connection(self) -> bool:
        """Test connection to AI service"""
        try:
            if self.ai_service == 'ollama':
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    if self.model in model_names:
                        print(f"✅ Connected to Ollama with model {self.model}")
                        return True
                    else:
                        print(f"❌ Model {self.model} not found in Ollama")
                        print(f"Available models: {', '.join(model_names)}")
                        return False
                else:
                    print(f"❌ Failed to connect to Ollama: {response.status_code}")
                    return False
            
            elif self.ai_service == 'openai':
                if self.openai_api_key:
                    print(f"✅ OpenAI API key configured")
                    return True
                else:
                    print(f"❌ OpenAI API key not found in environment")
                    return False
            
            else:
                print(f"❌ Unsupported AI service: {self.ai_service}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to AI service: {e}")
            return False
    
    def generate_with_ai(self, prompt: str, max_tokens: int = 4000) -> Optional[str]:
        """Generate content using AI service"""
        
        try:
            if self.ai_service == 'ollama':
                return self._generate_with_ollama(prompt, max_tokens)
            elif self.ai_service == 'openai':
                return self._generate_with_openai(prompt, max_tokens)
            else:
                print(f"❌ Unsupported AI service: {self.ai_service}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating content with AI: {e}")
            return None
    
    def _generate_with_ollama(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate content using Ollama"""
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error with Ollama: {e}")
            return None
    
    def _generate_with_openai(self, prompt: str, max_tokens: int) -> Optional[str]:
        """Generate content using OpenAI"""
        
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional travel writer creating comprehensive city guides."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error with OpenAI: {e}")
            return None
    
    def generate_city_guide_with_ai(self, destination: Destination, language: str = 'en') -> Optional[CityGuide]:
        """Generate comprehensive city guide using AI"""
        
        print(f"🤖 Generating AI-powered city guide for {destination.city}, {destination.country} ({language})")
        
        # Check if guide already exists
        existing_guide = CityGuide.objects.filter(
            destination=destination,
            language_code=language
        ).first()
        
        if existing_guide:
            print(f"ℹ️  Guide already exists. Use force_regenerate=True to overwrite.")
            return existing_guide
        
        # Generate overview
        overview = self._generate_ai_overview(destination, language)
        if not overview:
            print(f"❌ Failed to generate overview for {destination.city}")
            return None
        
        # Generate structured content
        neighborhoods = self._generate_ai_neighborhoods(destination, language)
        attractions = self._generate_ai_attractions(destination, language)
        dining = self._generate_ai_dining(destination, language)
        nightlife = self._generate_ai_nightlife(destination, language)
        shopping = self._generate_ai_shopping(destination, language)
        transportation = self._generate_ai_transportation(destination, language)
        accommodation = self._generate_ai_accommodation(destination, language)
        seasonal_guide = self._generate_ai_seasonal_guide(destination, language)
        practical_info = self._generate_ai_practical_info(destination, language)
        golf_summary = self._generate_ai_golf_summary(destination, language)
        
        # Create the guide
        try:
            guide = CityGuide.objects.create(
                destination=destination,
                language_code=language,
                overview=overview,
                neighborhoods=neighborhoods,
                attractions=attractions,
                dining=dining,
                nightlife=nightlife,
                shopping=shopping,
                transportation=transportation,
                accommodation=accommodation,
                seasonal_guide=seasonal_guide,
                practical_info=practical_info,
                golf_summary=golf_summary,
                meta_description=f"Complete AI-generated travel guide for {destination.city}, {destination.country}",
                is_published=True,
                is_featured=False
            )
            
            print(f"✅ Created AI-powered guide for {destination.city}")
            return guide
            
        except Exception as e:
            print(f"❌ Error creating guide: {e}")
            return None
    
    def _generate_ai_overview(self, destination: Destination, language: str) -> str:
        """Generate city overview using AI"""
        
        prompt = f"""
        Write a compelling 2-3 paragraph overview of {destination.city} in {destination.region_or_state}, {destination.country}.
        
        Include:
        - What makes this city unique and special
        - Main attractions and experiences
        - Cultural highlights
        - Best aspects for travelers
        - Overall atmosphere and character
        
        Write in {language} language.
        Keep it engaging and informative, around 150-200 words.
        """
        
        return self.generate_with_ai(prompt, 500) or f"{destination.city} is a captivating destination in {destination.region_or_state}, {destination.country}."
    
    def _generate_ai_neighborhoods(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate neighborhood information using AI"""
        
        prompt = f"""
        Create a JSON object describing 3-5 key neighborhoods in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Neighborhood Name": {{
                "description": "Brief description of the neighborhood",
                "highlights": ["highlight1", "highlight2", "highlight3"],
                "best_for": "What this area is best for"
            }}
        }}
        
        Include diverse neighborhoods like historic areas, modern districts, entertainment zones, etc.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse neighborhoods JSON for {destination.city}")
        
        # Fallback
        return {
            "Downtown": {
                "description": f"The heart of {destination.city}",
                "highlights": ["Main attractions", "Shopping", "Dining"],
                "best_for": "First-time visitors"
            }
        }
    
    def _generate_ai_attractions(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate attraction information using AI"""
        
        prompt = f"""
        Create a JSON object describing 4-6 top attractions in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Attraction Name": {{
                "description": "Description of the attraction",
                "category": "Category like Historic, Museum, Nature, etc.",
                "tips": "Practical tips for visitors"
            }}
        }}
        
        Include a mix of must-see landmarks, cultural sites, and unique experiences.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1200)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse attractions JSON for {destination.city}")
        
        # Fallback
        return {
            "Main Landmark": {
                "description": f"The most famous landmark in {destination.city}",
                "category": "Historic",
                "tips": "Visit early to avoid crowds"
            }
        }
    
    def _generate_ai_dining(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate dining information using AI"""
        
        prompt = f"""
        Create a JSON object describing 4-6 notable restaurants and dining options in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Restaurant Name": {{
                "description": "Description of the restaurant and cuisine",
                "cuisine_type": "Type of cuisine",
                "price_range": "$ (budget), $$ (moderate), $$$ (upscale), or $$$$ (luxury)"
            }}
        }}
        
        Include a mix of local specialties, fine dining, and casual options.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1200)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse dining JSON for {destination.city}")
        
        # Fallback
        return {
            "Local Restaurant": {
                "description": f"Popular local restaurant in {destination.city}",
                "cuisine_type": "Local",
                "price_range": "$$"
            }
        }
    
    def _generate_ai_nightlife(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate nightlife information using AI"""
        
        prompt = f"""
        Create a JSON object describing 3-5 nightlife venues in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Venue Name": {{
                "description": "Description of the venue",
                "type": "Type like Bar, Club, Live Music, etc.",
                "atmosphere": "Description of the atmosphere"
            }}
        }}
        
        Include diverse nightlife options.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse nightlife JSON for {destination.city}")
        
        # Fallback
        return {
            "Local Bar": {
                "description": f"Popular bar in {destination.city}",
                "type": "Bar",
                "atmosphere": "Casual and friendly"
            }
        }
    
    def _generate_ai_shopping(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate shopping information using AI"""
        
        prompt = f"""
        Create a JSON object describing 3-5 shopping areas in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Shopping Area Name": {{
                "description": "Description of the shopping area",
                "specialty": "What they specialize in",
                "price_range": "$ (budget), $$ (moderate), $$$ (upscale), or $$$$ (luxury)"
            }}
        }}
        
        Include markets, malls, boutique areas, etc.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse shopping JSON for {destination.city}")
        
        # Fallback
        return {
            "Main Shopping Area": {
                "description": f"Primary shopping district in {destination.city}",
                "specialty": "Mixed retail",
                "price_range": "$$"
            }
        }
    
    def _generate_ai_transportation(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate transportation information using AI"""
        
        prompt = f"""
        Create a JSON object describing transportation options in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Transport Type": {{
                "description": "Description of the transportation method",
                "cost": "Cost information",
                "tips": "Practical tips for using this transport"
            }}
        }}
        
        Include public transport, taxis, walking, etc.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse transportation JSON for {destination.city}")
        
        # Fallback
        return {
            "Public Transport": {
                "description": f"Public transportation in {destination.city}",
                "cost": "Varies",
                "tips": "Purchase day passes for savings"
            }
        }
    
    def _generate_ai_accommodation(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate accommodation information using AI"""
        
        prompt = f"""
        Create a JSON object describing 3-4 accommodation types in {destination.city}, {destination.country}.
        
        Format:
        {{
            "Hotel Type": {{
                "description": "Description of the accommodation",
                "area": "Area/neighborhood where it's located",
                "price_range": "$ (budget), $$ (moderate), $$$ (upscale), or $$$$ (luxury)"
            }}
        }}
        
        Include luxury, boutique, and budget options.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse accommodation JSON for {destination.city}")
        
        # Fallback
        return {
            "City Center Hotel": {
                "description": f"Hotel in the center of {destination.city}",
                "area": "City Center",
                "price_range": "$$"
            }
        }
    
    def _generate_ai_seasonal_guide(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate seasonal guide using AI"""
        
        prompt = f"""
        Create a JSON object describing seasonal information for {destination.city}, {destination.country}.
        
        Format:
        {{
            "Season Name": {{
                "weather": "Weather description",
                "activities": "Best activities for this season",
                "events": "Notable events or festivals"
            }}
        }}
        
        Include 2-4 seasons or periods.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse seasonal guide JSON for {destination.city}")
        
        # Fallback
        return {
            "Peak Season": {
                "weather": "Pleasant weather",
                "activities": "All outdoor activities",
                "events": "Local festivals"
            }
        }
    
    def _generate_ai_practical_info(self, destination: Destination, language: str) -> Dict[str, Any]:
        """Generate practical information using AI"""
        
        prompt = f"""
        Create a JSON object with practical travel information for {destination.city}, {destination.country}.
        
        Format:
        {{
            "Category": {{
                "details": "Specific details",
                "tips": "Helpful tips"
            }}
        }}
        
        Include categories like Language, Currency, Safety, Customs, etc.
        Write in {language} language.
        Return only valid JSON.
        """
        
        ai_response = self.generate_with_ai(prompt, 1000)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                print(f"❌ Failed to parse practical info JSON for {destination.city}")
        
        # Fallback
        return {
            "Language": {
                "details": f"Local language in {destination.country}",
                "tips": "Learn basic phrases"
            }
        }
    
    def _generate_ai_golf_summary(self, destination: Destination, language: str) -> str:
        """Generate golf summary using AI"""
        
        prompt = f"""
        Write a 2-3 sentence summary about golf opportunities in {destination.city}, {destination.country}.
        
        Include:
        - Brief mention of golf courses or facilities
        - Unique aspects of golfing in this location
        - Appeal to golf enthusiasts
        
        End with: <a href="#" class="golf-link">Explore {destination.city}'s golf courses →</a>
        
        Write in {language} language.
        """
        
        ai_response = self.generate_with_ai(prompt, 300)
        if ai_response:
            return ai_response
        
        # Fallback
        return f"{destination.city} offers golf experiences that showcase the natural beauty of the region. <a href=\"#\" class=\"golf-link\">Explore {destination.city}'s golf courses →</a>"

def main():
    """Main function for AI city guide generation"""
    
    print("🤖 AI-Enhanced CityGuide Generator")
    print("=" * 40)
    
    # Check available AI services
    print("\nAvailable AI Services:")
    print("1. Ollama (Local AI)")
    print("2. OpenAI (API)")
    
    ai_choice = input("\nSelect AI service (1-2): ").strip()
    
    if ai_choice == '1':
        # Ollama setup
        model = input("Enter Ollama model (default: llama3.1:7b): ").strip() or 'llama3.1:7b'
        generator = AICityGuideGenerator(ai_service='ollama', model=model)
    elif ai_choice == '2':
        # OpenAI setup
        model = input("Enter OpenAI model (default: gpt-3.5-turbo): ").strip() or 'gpt-3.5-turbo'
        generator = AICityGuideGenerator(ai_service='openai', model=model)
    else:
        print("Invalid choice. Using Ollama as default.")
        generator = AICityGuideGenerator(ai_service='ollama', model='llama3.1:7b')
    
    # Test AI connection
    if not generator.test_ai_connection():
        print("❌ Cannot connect to AI service. Please check your setup.")
        return
    
    # Get destinations
    destinations = Destination.objects.all()
    print(f"\nFound {destinations.count()} destinations")
    
    # Language selection
    language = input("Enter language code (default: en): ").strip() or 'en'
    
    # Destination selection
    print("\nOptions:")
    print("1. Generate for first 3 destinations (demo)")
    print("2. Generate for specific destination ID")
    print("3. Generate for all destinations")
    
    dest_choice = input("\nSelect option (1-3): ").strip()
    
    if dest_choice == '1':
        # Demo with first 3 destinations
        demo_destinations = destinations[:3]
        print(f"\n🚀 Generating AI guides for {len(demo_destinations)} destinations...")
        
        for dest in demo_destinations:
            guide = generator.generate_city_guide_with_ai(dest, language)
            if guide:
                print(f"✅ Generated guide for {dest.city}")
                print(f"   URL: {guide.get_absolute_url()}")
                print(f"   Word count: {guide.word_count}")
            else:
                print(f"❌ Failed to generate guide for {dest.city}")
    
    elif dest_choice == '2':
        # Specific destination
        dest_id = input("Enter destination ID: ").strip()
        try:
            dest = Destination.objects.get(id=int(dest_id))
            print(f"\n🚀 Generating AI guide for {dest.city}...")
            
            guide = generator.generate_city_guide_with_ai(dest, language)
            if guide:
                print(f"✅ Generated guide for {dest.city}")
                print(f"   URL: {guide.get_absolute_url()}")
                print(f"   Word count: {guide.word_count}")
            else:
                print(f"❌ Failed to generate guide for {dest.city}")
                
        except (ValueError, Destination.DoesNotExist):
            print("❌ Invalid destination ID")
    
    elif dest_choice == '3':
        # All destinations
        confirm = input(f"Generate AI guides for ALL {destinations.count()} destinations? (y/N): ").strip().lower()
        if confirm == 'y':
            print(f"\n🚀 Generating AI guides for all destinations...")
            
            success_count = 0
            for dest in destinations:
                guide = generator.generate_city_guide_with_ai(dest, language)
                if guide:
                    success_count += 1
                    print(f"✅ {success_count}/{destinations.count()}: {dest.city}")
                else:
                    print(f"❌ Failed: {dest.city}")
            
            print(f"\n🎉 Complete! Generated {success_count}/{destinations.count()} guides")
        else:
            print("Operation cancelled.")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
