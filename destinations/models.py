from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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

    # Modular guides for destinations, stored as JSON
    # Format: {"en": {"introduction": "...", "dining": "..."}, "es": {...}}
    modular_guides = models.JSONField(default=dict, blank=True)

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
            return reverse('destinations:destination_detail', kwargs={'slug': self.generate_slug()})
        else:
            return reverse('destinations:destination_detail_lang', kwargs={
                'language': language, 
                'slug': self.generate_slug(language)
            })

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"

    class Meta:
        ordering = ['name']

class DestinationGuide(models.Model):
    """
    Separate model for multi-language golf destination guides.
    Each guide is a specific language version of content for a destination.
    """
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='guides'
    )
    language_code = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('es', 'Spanish'),
            ('de', 'German'),
            ('fr', 'French'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('zh', 'Chinese'),
        ],
        help_text="Language code (ISO 639-1)"
    )
    
    # Main content
    title = models.CharField(
        max_length=300, 
        blank=True,
        help_text="SEO-optimized title for this language version"
    )
    content = models.TextField(
        help_text="Full golf guide content in Markdown format"
    )
    
    # SEO fields
    meta_description = models.CharField(
        max_length=160, 
        blank=True,
        help_text="Meta description for search engines"
    )
    slug = models.SlugField(
        max_length=300,
        blank=True,
        help_text="Auto-generated from destination and language"
    )
    
    # Content metadata
    word_count = models.PositiveIntegerField(
        default=0,
        help_text="Approximate word count for content management"
    )
    character_count = models.PositiveIntegerField(
        default=0,
        help_text="Character count for content management"
    )
    
    # Generation tracking
    generated_by = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('ollama', 'Ollama LLM'),
            ('openai', 'OpenAI API'),
            ('imported', 'Data Import'),
        ],
        default='ollama'
    )
    generation_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific model used for generation (e.g., 'llama3.1:70b')"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_generated_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this content was last regenerated"
    )
    
    class Meta:
        unique_together = ('destination', 'language_code')
        ordering = ['destination__name', 'language_code']
        indexes = [
            models.Index(fields=['language_code', 'destination']),
            models.Index(fields=['destination', 'language_code']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and update counts on save"""
        if not self.slug:
            self.slug = self.generate_slug()
        
        # Update word/character counts
        if self.content:
            self.character_count = len(self.content)
            # Simple word count (split by whitespace)
            self.word_count = len(self.content.split())
        
        super().save(*args, **kwargs)
    
    def generate_slug(self):
        """Generate SEO-friendly slug"""
        city = self.destination.city.replace(" ", "-").lower()
        region = self.destination.region_or_state.replace(" ", "-").lower()
        country = self.destination.country.replace(" ", "-").lower()
        
        if self.language_code == 'en':
            return slugify(f"golf-guide-{city}-{region}-{country}")
        else:
            return slugify(f"{self.language_code}-golf-guide-{city}-{region}-{country}")
    
    def get_absolute_url(self):
        """Get URL for this specific language guide"""
        if self.language_code == 'en':
            return reverse('destinations:destination_detail', kwargs={'slug': self.slug})
        else:
            return reverse('destinations:destination_detail_lang', kwargs={
                'language': self.language_code, 
                'slug': self.slug
            })
    
    def get_reading_time(self):
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        if self.word_count:
            return max(1, round(self.word_count / 200))
        return 0
    
    def __str__(self):
        return f"{self.destination.name} ({self.get_language_code_display()})"

# Cache invalidation signals
@receiver([post_save, post_delete], sender=Destination)
def invalidate_destination_cache(sender, **kwargs):
    """Invalidate home page cache when destinations change"""
    cache.delete('destinations_grid')
    # Clear view-level cache for home page
    cache.delete_many([
        'views.decorators.cache.cache_page.home',
        'views.decorators.cache.cache_page.home.en',
    ])

@receiver([post_save, post_delete], sender=DestinationGuide)
def invalidate_guide_cache(sender, **kwargs):
    """Invalidate destination detail cache when guides change"""
    if hasattr(kwargs.get('instance'), 'destination'):
        dest = kwargs['instance'].destination
        # Clear destination detail page cache
        cache.delete(f'destination_detail_{dest.generate_slug()}')
        # Also clear home page cache as new content might affect featured status
        cache.delete('destinations_grid')
