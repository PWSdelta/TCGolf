import google.generativeai as genai
import os
import json
from datetime import datetime
import time  # Add this import for timing

# Configuration
GEMINI_API_KEY = "AIzaSyBVCYcGrVKNSDF-Si8tynLaEhFkqyHWI90"  # Replace with your actual API key
PROMPT_FILE = "prompt-simplified.txt"  # Your prompt file
OUTPUT_DIR = "golf_guides"

# Test city data
TEST_CITY = "Kansas City"
TEST_REGION = "Missouri"
TEST_COUNTRY = "United States"

def setup_gemini():
    """Initialize Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    return {
        'flash': genai.GenerativeModel('gemini-1.5-flash'),
        'pro': genai.GenerativeModel('gemini-1.5-pro')
    }

def load_prompt(file_path):
    """Load prompt from text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None

def format_prompt(prompt_template, city, region, country):
    """Replace placeholders in prompt and encourage narrative-style writing."""
    narrative_instructions = "\n\nIMPORTANT: Write in a detailed, narrative style. Avoid excessive use of bullet points. Use paragraphs to provide a fluid and engaging reading experience."
    return (prompt_template.replace('{city}', city)
                          .replace('{region}', region)
                          .replace('{country}', country) + narrative_instructions)

def generate_content(model, prompt, model_name):
    """Generate content using specified model"""
    print(f"\n🚀 Generating content with {model_name}...")
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,  # Adjust based on your needs
                top_p=0.8,
                top_k=40
            )
        )
        
        return {
            'content': response.text,
            'usage': {
                'prompt_tokens': response.usage_metadata.prompt_token_count,
                'completion_tokens': response.usage_metadata.candidates_token_count,
                'total_tokens': response.usage_metadata.total_token_count
            }
        }
    except Exception as e:
        print(f"Error with {model_name}: {str(e)}")
        return None

def calculate_cost(usage, model_name):
    """Calculate cost based on token usage"""
    costs = {
        'flash': {'input': 0.075, 'output': 0.30},  # per 1M tokens
        'pro': {'input': 1.25, 'output': 5.00}     # per 1M tokens
    }
    
    if model_name.lower() not in costs:
        return 0
    
    rates = costs[model_name.lower()]
    input_cost = (usage['prompt_tokens'] / 1_000_000) * rates['input']
    output_cost = (usage['completion_tokens'] / 1_000_000) * rates['output']
    
    return input_cost + output_cost

def save_results(results, city, region, country):
    """Save results to files, including Markdown format."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{city}_{region}_{country}_{timestamp}"

    # Save individual results
    for model_name, result in results.items():
        if result:
            # Save as plain text
            filename = f"{OUTPUT_DIR}/{base_filename}_{model_name}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== {model_name.upper()} RESULTS ===\n")
                f.write(f"City: {city}, {region}, {country}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tokens: {result['usage']['total_tokens']}\n")
                f.write(f"Cost: ${calculate_cost(result['usage'], model_name):.4f}\n")
                f.write("=" * 50 + "\n\n")
                f.write(result['content'])

            # Save as Markdown
            markdown_filename = f"{OUTPUT_DIR}/{base_filename}_{model_name}.md"
            with open(markdown_filename, 'w', encoding='utf-8') as f:
                f.write(f"# {city}, {region}, {country}: {model_name.upper()} Results\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Tokens:** {result['usage']['total_tokens']}\n\n")
                f.write(f"**Cost:** ${calculate_cost(result['usage'], model_name):.4f}\n\n")
                f.write(result['content'].replace('\n', '\n\n'))  # Enhance spacing in Markdown

    # Save comparison summary
    summary_filename = f"{OUTPUT_DIR}/{base_filename}_comparison.json"
    comparison_data = {
        'city': city,
        'region': region,
        'country': country,
        'timestamp': timestamp,
        'models': {}
    }

    for model_name, result in results.items():
        if result:
            comparison_data['models'][model_name] = {
                'usage': result['usage'],
                'cost': calculate_cost(result['usage'], model_name),
                'word_count': len(result['content'].split()),
                'char_count': len(result['content'])
            }

    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2)

    return base_filename

def main():
    """Main execution function"""
    print("🏌️ Gemini Golf Guide Comparison Tool")
    print("=" * 40)
    
    # Load prompt
    prompt_template = load_prompt(PROMPT_FILE)
    if not prompt_template:
        return
    
    # Setup models
    print("Setting up Gemini models...")
    models = setup_gemini()
    
    # Format prompt with test city
    formatted_prompt = format_prompt(prompt_template, TEST_CITY, TEST_REGION, TEST_COUNTRY)
    print(f"Prompt length: {len(formatted_prompt)} characters")
    
    # Generate content with both models
    results = {}

    # Test with Flash first (cheaper)
    print("\n⏱ Timing Gemini 1.5 Flash...")
    start_time = time.time()
    results['flash'] = generate_content(models['flash'], formatted_prompt, 'Gemini 1.5 Flash')
    flash_time = time.time() - start_time
    print(f"Gemini 1.5 Flash took {flash_time:.2f} seconds.")

    # Test with Pro
    print("\n⏱ Timing Gemini 1.5 Pro...")
    start_time = time.time()
    results['pro'] = generate_content(models['pro'], formatted_prompt, 'Gemini 1.5 Pro')
    pro_time = time.time() - start_time
    print(f"Gemini 1.5 Pro took {pro_time:.2f} seconds.")

    # Save results
    base_filename = save_results(results, TEST_CITY, TEST_REGION, TEST_COUNTRY)

    # Print comparison
    print("\n📊 COMPARISON RESULTS")
    print("=" * 40)
    print(f"\nTiming Summary:")
    print(f"  Gemini 1.5 Flash: {flash_time:.2f} seconds")
    print(f"  Gemini 1.5 Pro: {pro_time:.2f} seconds")
    
    for model_name, result in results.items():
        if result:
            cost = calculate_cost(result['usage'], model_name)
            word_count = len(result['content'].split())
            print(f"\n{model_name.upper()}:")
            print(f"  Words: {word_count:,}")
            print(f"  Tokens: {result['usage']['total_tokens']:,}")
            print(f"  Cost: ${cost:.4f}")
            print(f"  Cost per word: ${cost/word_count:.6f}")
    
    print(f"\n💾 Results saved to {OUTPUT_DIR}/ with prefix: {base_filename}")
    print("\n✅ Comparison complete!")

if __name__ == "__main__":
    # Check if API key is set
    if GEMINI_API_KEY == "your_api_key_here":
        print("⚠️  Please set your GEMINI_API_KEY in the script")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
    else:
        main()
