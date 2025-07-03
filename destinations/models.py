from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import json

# Create your models here.

class Destination(models.Model):
    # Core location data (language-neutral)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    region_or_state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Multi-language article content stored as JSON
    # Format: {"en": "English content...", "de": "German content...", "es": "Spanish content..."}
    article_content_multilang = models.JSONField(default=dict, blank=True)
    
    # Keep the original field for backward compatibility
    article_content = models.TextField(blank=True)

    # Language support constants
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'de': 'German', 
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
    }
    
    def get_article_content(self, language='en'):
        """Get article content for a specific language, fallback to English"""
        if self.article_content_multilang and language in self.article_content_multilang:
            return self.article_content_multilang[language]
        elif self.article_content_multilang and 'en' in self.article_content_multilang:
            return self.article_content_multilang['en']
        else:
            # Fallback to the original field for backward compatibility
            return self.article_content
    
    def set_article_content(self, content, language='en'):
        """Set article content for a specific language"""
        if not self.article_content_multilang:
            self.article_content_multilang = {}
        self.article_content_multilang[language] = content
        
        # Keep the main field updated with English content for backward compatibility
        if language == 'en':
            self.article_content = content
    
    def get_available_languages(self):
        """Get list of languages for which content is available"""
        if not self.article_content_multilang:
            return ['en'] if self.article_content else []
        return list(self.article_content_multilang.keys())
    
    def has_content_in_language(self, language):
        """Check if content exists for a specific language"""
        return (self.article_content_multilang and 
                language in self.article_content_multilang and 
                self.article_content_multilang[language].strip())

    def generate_slug(self, language='en'):
        """Generate SEO-friendly slug with optional language prefix"""
        # Create a more golf-focused slug format that includes country for uniqueness
        # Clean and format location components
        city = self.city.replace(" ", "-").lower()
        region = self.region_or_state.replace(" ", "-").lower()
        country = self.country.replace(" ", "-").lower()
        
        # Create the final slug with "golf-course" prefix for better SEO
        if language == 'en':
            slug_text = f"golf-course-{city}-{region}-{country}"
        else:
            slug_text = f"{language}-golf-course-{city}-{region}-{country}"
        return slugify(slug_text)

    def get_absolute_url(self, language='en'):
        if language == 'en':
            return reverse('destination_detail', kwargs={'slug': self.generate_slug()})
        else:
            return reverse('destination_detail_lang', kwargs={
                'language': language, 
                'slug': self.generate_slug(language)
            })

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"

    class Meta:
        ordering = ['name']
