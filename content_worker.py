#!/usr/bin/env python
"""
GolfPlex Content Generation Worker

This script runs locally and:
1. Fetches a single (destination, language) work unit from Django API
2. Generates English guide (2500+ words) OR translates existing English content
3. Saves work to JSON for safety
4. Submits completed work back to the API immediately
5. Fetches next work unit and repeats

Each work unit is one destination + one language, preventing race conditions
between multiple workers and enabling immediate submission.

Usage:
    python content_worker.py --api-url http://localhost:8000 --model gemma3n:e4b
"""

import requests
import json
import argparse
import time
import os
from datetime import datetime
from typing import Dict, List, Optional

class GolfContentWorker:
    def __init__(self, api_url: str, ollama_url: str = "http://localhost:11434", output_dir: str = "generated_content", model_name: str = "llama3.1"):
        self.api_url = api_url.rstrip('/')
        self.ollama_url = ollama_url.rstrip('/')
        self.model_name = model_name
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Timing tracking
        self.worker_start_time = None
        self.destination_timings = []
        
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
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            print(f"📋 Available models: {model_names}")
            
            if not any(self.model_name in name for name in model_names):
                print(f"⚠️  Model '{self.model_name}' not found.")
                print(f"💡 You can pull the model with: ollama pull {self.model_name}")
                print("🔄 Attempting to continue anyway (model might be available)...")
            else:
                print(f"✅ Connected to Ollama, using model: {self.model_name}")
                
        except requests.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
            print(f"Error: {e}")
            print(f"💡 Make sure Ollama is running: ollama serve")
            raise e
    
    def call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Make a request to Ollama API with streaming output"""
        try:
            print(f"🤖 Calling Ollama with model {self.model_name}...")
            start_time = time.time()
            
            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "stream": True,  # Enable streaming
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=300,  # 5 minute timeout for long content generation
                stream=True   # Enable streaming response
            )
            response.raise_for_status()
            
            generated_text = ""
            print("📝 Generating content (streaming)...")
            print("-" * 50)
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            text_chunk = chunk['response']
                            generated_text += text_chunk
                            print(text_chunk, end='', flush=True)
                        
                        # Check if generation is done
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            print("\n" + "-" * 50)
            print(f"✅ Generation complete!")
            print(f"⏱️  Time taken: {generation_time:.1f} seconds")
            print(f"📊 Content length: {len(generated_text)} characters")
            print(f"🚀 Speed: {len(generated_text)/generation_time:.0f} chars/sec")
            
            return generated_text.strip()
            
        except requests.RequestException as e:
            print(f"❌ Ollama API error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Unexpected error calling Ollama: {e}")
            return ""

    def fetch_work(self) -> Optional[Dict]:
        """Fetch next (destination, language) work item from the API"""
        try:
            print(f"📥 Fetching work from {self.api_url}/api/fetch-work/")
            response = self.session.get(f"{self.api_url}/api/fetch-work/", timeout=30)
            response.raise_for_status()
            data = response.json()
            if data['status'] == 'no_work':
                print("🎉 No more work available - all content is complete!")
                return None
            elif data['status'] == 'work_available':
                print(f"✅ Work fetched: {data['destination'].get('city', '')}, {data['destination'].get('country', '')} [{data['target_language']}]")
                return data
            else:
                print(f"❌ Error fetching work: {data.get('message', 'Unknown error')}")
                return None
        except requests.RequestException as e:
            print(f"❌ Network error fetching work: {e}")
            return None
    
    def load_prompt_template(self) -> str:
        """Load the professional prompt template from file"""
        try:
            with open('worldwide_golf_guide_prompt.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("⚠️  worldwide_golf_guide_prompt.txt not found, using basic prompt")
            return self.get_basic_prompt_template()
    
    def get_basic_prompt_template(self) -> str:
        """Fallback prompt if template file is not found"""
        return """Write a comprehensive golf destination guide for {city}, {country}.

REQUIREMENTS:
- Minimum 2500 words
- Include seasonal information and best times to visit
- Cover multiple golf courses and facilities in the area
- Include accommodation recommendations
- Mention local attractions beyond golf
- Include practical travel information
- Use engaging, travel-guide style writing

DESTINATION INFO:
- Name: {name}
- Location: {city}, {region_or_state}, {country}
- Description: {description}
- Coordinates: {latitude}, {longitude}"""

    def generate_english_guide(self, destination: Dict) -> str:
        """Generate comprehensive English golf destination guide using Ollama"""
        system_prompt = "You are a professional golf travel writer creating destination guides for golfers worldwide. Write engaging, comprehensive guides that help golfers plan their trips."
        
        # Load the professional prompt template
        prompt_template = self.load_prompt_template()
        
        # Replace placeholders with destination data
        prompt = prompt_template.format(
            city=destination['city'],
            region=destination['region_or_state'],
            country=destination['country'],
            name=destination['name'],
            description=destination['description'],
            latitude=destination['latitude'],
            longitude=destination['longitude']
        )
        
        return self.call_ollama(prompt, system_prompt)
    
    def translate_guide(self, english_content: str, target_language: str, destination: Dict) -> str:
        """Translate guide to target language with cultural adaptation using Ollama"""
        language_name = self.language_names.get(target_language, target_language)
        
        system_prompt = f"You are a professional translator specializing in golf and travel content for {language_name}-speaking audiences. Translate naturally with cultural adaptation."
        
        prompt = f"""
Translate the following golf destination guide to {language_name}, adapting it culturally for {language_name}-speaking golf tourists.

IMPORTANT INSTRUCTIONS:
- Translate naturally, not word-for-word
- Adapt cultural references appropriately
- Keep golf terminology accurate
- Maintain the engaging travel guide tone
- Ensure minimum 2000 words in the translation
- Keep all factual information accurate
- Adapt currency mentions if relevant
- Consider travel patterns of {language_name}-speaking tourists

DESTINATION: {destination['city']}, {destination['country']}

ORIGINAL ENGLISH GUIDE:
{english_content}

Provide the complete translated guide in {language_name}:
"""
        
        return self.call_ollama(prompt, system_prompt)
    
    def process_work_item(self, work_data: Dict) -> bool:
        """Process a single (destination, language) work item"""
        process_start_time = time.time()
        destination = work_data['destination']
        language = work_data['target_language']  # Updated to match new API
        content = ""
        generation_time = 0
        
        print(f"\n🏌️ Processing: {destination['city']}, {destination['country']} [{language}]")
        
        # English generation
        if language == 'en':
            print("📖 Generating English guide...")
            english_start = time.time()
            content = self.generate_english_guide(destination)
            generation_time = time.time() - english_start
            
            if content:
                print(f"✅ Generated English guide for {destination['city']}, {destination['country']} ({len(content)} characters in {generation_time:.1f}s)")
            else:
                print(f"❌ Failed to generate English guide for {destination['city']}, {destination['country']}")
                return False
        else:
            # Translation: need English content
            existing_guides = work_data.get('existing_guides', {})
            english_content = existing_guides.get('en', {}).get('content', '')
            
            if not english_content:
                print(f"❌ No English content available for translation for {destination['city']}, {destination['country']}")
                return False
                
            print(f"🌐 Translating to {self.language_names.get(language, language)}...")
            translation_start = time.time()
            content = self.translate_guide(english_content, language, destination)
            generation_time = time.time() - translation_start
            
            if content:
                print(f"✅ Translated to {language} for {destination['city']}, {destination['country']} ({len(content)} characters in {generation_time:.1f}s)")
            else:
                print(f"❌ Failed to translate to {language} for {destination['city']}, {destination['country']}")
                return False
        
        # Save to JSON for safety
        guides = {language: {'content': content}}
        self.save_work_json(destination, guides)
        
        # Submit to API (updated format)
        submit_success = self.submit_work_single(destination['id'], language, content)
        
        # Timing summary
        total_time = time.time() - process_start_time
        destination_timing = {
            'destination': f"{destination['city']}, {destination['country']}",
            'destination_id': destination['id'],
            'language': language,
            'total_time': total_time,
            'generation_time': generation_time,
            'success': submit_success,
            'timestamp': datetime.now().isoformat()
        }
        self.destination_timings.append(destination_timing)
        
        print(f"⏱️  Work unit processing time: {total_time:.1f} seconds")
        self.print_timing_summary()
        return submit_success
    
    def print_timing_summary(self):
        """Print current timing statistics"""
        if not self.destination_timings:
            return
            
        successful_timings = [t for t in self.destination_timings if t['success']]
        
        if successful_timings:
            avg_time = sum(t['total_time'] for t in successful_timings) / len(successful_timings)
            fastest = min(successful_timings, key=lambda x: x['total_time'])
            slowest = max(successful_timings, key=lambda x: x['total_time'])
            
            print(f"📊 Timing Stats: Avg: {avg_time:.1f}s | "
                  f"Fastest: {fastest['total_time']:.1f}s ({fastest['destination']} {fastest['language']}) | "
                  f"Slowest: {slowest['total_time']:.1f}s ({slowest['destination']} {slowest['language']})")

    def get_worker_uptime(self) -> str:
        """Get formatted worker uptime"""
        if not self.worker_start_time:
            return "0s"
        
        uptime_seconds = time.time() - self.worker_start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def save_work_json(self, destination: Dict, guides: Dict):
        """Save generated content to JSON file for safety"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{destination['id']}_{destination['city'].replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        work_data = {
            'destination': destination,
            'guides': guides,
            'generated_at': datetime.now().isoformat(),
            'worker_version': '1.0'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(work_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved work to: {filepath}")
    
    def submit_work_single(self, destination_id: int, language_code: str, content: str) -> bool:
        """Submit completed work for a single (destination, language) pair to the API"""
        try:
            print(f"📤 Submitting work for destination {destination_id} ({language_code})...")
            payload = {
                'destination_id': destination_id,
                'language_code': language_code,
                'content': content,
                'worker_info': {
                    'worker_version': '1.0',
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            response = self.session.post(
                f"{self.api_url}/api/submit-work/",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if result['status'] == 'success':
                guide = result['guide']
                print(f"✅ Submitted work successfully:")
                print(f"   {guide['action'].title()}: {guide['language_name']} guide")
                print(f"   Content length: {guide['content_length']} characters")
                return True
            else:
                print(f"❌ Submission failed: {result.get('message', 'Unknown error')}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Network error submitting work: {e}")
            return False

    def submit_work(self, destination_id: int, guides: Dict) -> bool:
        """Submit completed work to the API"""
        try:
            print(f"📤 Submitting work for destination {destination_id}...")
            payload = {
                'destination_id': destination_id,
                'guides': guides,
                'worker_info': {
                    'worker_version': '1.0',
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            response = self.session.post(
                f"{self.api_url}/api/submit-work/",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if result['status'] == 'success':
                results = result['results']
                print(f"✅ Submitted work successfully:")
                print(f"   Created: {len(results['created_guides'])} guides")
                print(f"   Updated: {len(results['updated_guides'])} guides")
                if results['errors']:
                    print(f"   Errors: {results['errors']}")
                return True
            else:
                print(f"❌ Submission failed: {result.get('message', 'Unknown error')}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Network error submitting work: {e}")
            return False
    
    def get_work_status(self):
        """Get overall work status from API"""
        try:
            print(f"📊 Getting work status from {self.api_url}/api/work-status/")
            response = self.session.get(f"{self.api_url}/api/work-status/", timeout=30)
            response.raise_for_status()
            status = response.json()
            
            print("\n📊 WORK STATUS:")
            print("=" * 50)
            overview = status['overview']
            print(f"Total destinations: {overview['total_destinations']}")
            print(f"Destinations with guides: {overview['destinations_with_guides']}")
            print(f"Destinations without guides: {overview['destinations_without_guides']}")
            print(f"Total guides: {overview['total_guides']}")
            print(f"Overall completion: {overview['completion_percentage']}%")
            
            print("\n🌐 Language Progress:")
            for lang, stats in status['language_stats'].items():
                print(f"  {stats['name']}: {stats['count']} guides ({stats['percentage']}%)")
            
        except requests.RequestException as e:
            print(f"❌ Error getting work status: {e}")
    
    def run(self, max_items: int = None):
        """Main worker loop: fetch and process one (destination, language) at a time"""
        self.worker_start_time = time.time()
        print("🚀 Starting GolfPlex Content Generation Worker (Ollama)")
        print(f"🔗 API URL: {self.api_url}")
        print(f"🤖 Ollama URL: {self.ollama_url}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"🧠 Model: {self.model_name}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.get_work_status()
        processed = 0
        while max_items is None or processed < max_items:
            uptime = self.get_worker_uptime()
            print(f"\n🔄 Fetching work item {processed + 1}... (Uptime: {uptime})")
            work_data = self.fetch_work()
            if not work_data:
                break
            success = self.process_work_item(work_data)
            if success:
                processed += 1
                print(f"✅ Completed work item {processed}")
            else:
                print(f"❌ Failed work item {processed + 1}")
                print("🔄 Continuing to next item...")
            time.sleep(2)
        final_uptime = self.get_worker_uptime()
        print(f"\n🎯 Worker completed. Processed {processed} items.")
        print(f"⏰ Total uptime: {final_uptime}")
        if self.destination_timings:
            successful = len([t for t in self.destination_timings if t['success']])
            failed = len(self.destination_timings) - successful
            print(f"📊 Final Stats: {successful} successful, {failed} failed")
            if successful > 0:
                total_generation_time = sum(t['total_time'] for t in self.destination_timings if t['success'])
                avg_time = total_generation_time / successful
                print(f"⚡ Average time per work unit: {avg_time:.1f}s")
                print(f"🏭 Total generation time: {total_generation_time:.1f}s")
        self.get_work_status()


def main():
    parser = argparse.ArgumentParser(description='GolfPlex Content Generation Worker (Ollama)')
    parser.add_argument('--api-url', required=True, help='Django API base URL (e.g., http://localhost:8000)')
    parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama API URL (default: http://localhost:11434)')
    parser.add_argument('--model', default='llama3.1', help='Ollama model name (default: llama3.1)')
    parser.add_argument('--output-dir', default='generated_content', help='Output directory for JSON files')
    parser.add_argument('--max-items', type=int, help='Maximum items to process (default: unlimited)')
    parser.add_argument('--english-only', action='store_true', help='Generate only English guides (skip translations)')
    
    args = parser.parse_args()
    
    print(f"🎯 Starting worker with arguments:")
    print(f"   API URL: {args.api_url}")
    print(f"   Ollama URL: {args.ollama_url}")
    print(f"   Model: {args.model}")
    print(f"   Output dir: {args.output_dir}")
    print(f"   Max items: {args.max_items or 'unlimited'}")
    print(f"   English only: {args.english_only}")
    
    worker = GolfContentWorker(
        api_url=args.api_url,
        ollama_url=args.ollama_url,
        output_dir=args.output_dir,
        model_name=args.model
    )
    try:
        worker.run(max_items=args.max_items)
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped by user")
    except Exception as e:
        print(f"\n❌ Worker error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()