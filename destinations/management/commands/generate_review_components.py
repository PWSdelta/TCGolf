import os
import google.generativeai as genai
from django.core.management.base import BaseCommand
from destinations.models import Destination
from dotenv import load_dotenv
import json  # Import json module for dumping modular_reviews
from django.db import models
import concurrent.futures  # Import for concurrency

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = 'Generate modular review components for destinations using Gemini Flash'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=1, help='Limit the number of destinations to process')
        parser.add_argument('--dry-run', action='store_true', help='Run without saving results to the database')

    def handle(self, *args, **options):
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            self.stderr.write("Error: GOOGLE_API_KEY is not set in the environment.")
            return

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Fetch destinations
        limit = options['limit']
        dry_run = options['dry_run']
# Remove modular_guides usage (legacy)

        if not destinations.exists():
            self.stdout.write("No destinations found.")
            return

        def process_destination(destination):
            self.stdout.write(f"Generating modular review for: {destination.name}")

            # Ensure modular_guides is initialized as a dictionary
            if not isinstance(destination.modular_guides, dict):
                destination.modular_guides = {}

            # Skip generation if modular review for the language already exists
            if not dry_run and "en" in destination.modular_guides:
                self.stdout.write(f"Skipping {destination.name}: Modular review for 'en' already exists.")
                return

            # Define sections and prompts using the refined prompt template
            sections = {
                "introduction": "Provide an overview of the city as a golf destination, highlighting its unique appeal and key features.",
                "renowned_golf_courses": "Describe the most notable golf courses, including their unique characteristics, signature holes, and what makes them stand out. Use links to course websites where appropriate, ensuring they open in a new tab (target=\"_blank\").",
                "off_the_beaten_path": "Highlight lesser-known courses or hidden gems that offer a unique or unexpected golfing experience.",
                "golf_on_the_cheap": "Recommend budget-friendly courses or deals for golfers looking to save money without compromising on quality.",
                "seasonal_insights": "Offer advice on the best times to visit for golfing, considering weather, peak seasons, and off-season opportunities.",
                "travel_and_lodging": "Include practical advice for international golfers, such as flights, transportation, and accommodation options. Highlight resorts with stay-and-play packages or hotels near top courses.",
                "cultural_highlights": "Briefly touch on local culture, dining, and other activities that complement a golf trip. Use bullet points sparingly for recommendations like restaurants, attractions, or must-try experiences. Include links to official websites or resources where relevant, ensuring they open in a new tab (target=\"_blank\").",
                "dining": "Explore the cultural food traditions and practices of the destination. Highlight unique culinary customs, traditional dishes, and the role of food in local culture. Provide insights into how meals are prepared, served, and enjoyed in the region. Include any notable food festivals or cultural events related to cuisine."
            }



# Golf-Focused (~6):
# Introduction
# Renowned Golf Courses
# Off the Beaten Path Courses
# Golf on the Cheap
# Seasonal Insights
# 2-Day Golf Itinerary ✅

# Destination-Focused (~5):
# Travel and Lodging
# Cultural Highlights
# Dining
# Things to Do Beyond Golf
# Safety & Practical Tips

# Closing (~1):
# Call to Action and Resources ✅

            modular_review = {}

            for section, prompt_template in sections.items():
                # Format the prompt for the current section
                prompt = (
                    f"Write a detailed and engaging section for the following destination.\n\n"
                    f"{prompt_template}\n\n"
                    f"Destination: {destination.name}\n"
                    f"City: {destination.city}\n"
                    f"Region/State: {destination.region_or_state}\n"
                    f"Country: {destination.country}\n"
                )

                # Generate content for the section
                self.stdout.write(f"Generating content for section: {section}")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,  # Increased token limit for detailed sections
                        top_p=0.8,
                        top_k=40
                    )
                )

                # Store the generated content in the modular review
                modular_review[section] = response.text.strip()

            # Display the output
            self.stdout.write(f"\nGenerated Modular Review for {destination.name}:")
            for section, content in modular_review.items():
                if content.strip():  # Only display sections with content
                    self.stdout.write(f"\n{section.replace('_', ' ').capitalize()}:")
                    self.stdout.write(content)

            # Save to the database if not a dry run
            if not dry_run:
                destination.modular_guides["en"] = modular_review
                destination.save()
                self.stdout.write(f"Saved modular review for: {destination.name}")

        # Process destinations in parallel using threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(process_destination, destinations)

        # Dump the modular_reviews field to the terminal for the first destination
        if not dry_run and destinations.exists():
            self.stdout.write("\nDumping modular_reviews for the first destination:")
            self.stdout.write(json.dumps(destinations[0].modular_reviews, indent=4, ensure_ascii=False))
