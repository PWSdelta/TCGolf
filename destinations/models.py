from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json

# Create your models here.

class Destination(models.Model):
    # ...existing fields...

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
            models.Index(fields=['region_or_state']),
            models.Index(fields=['country']),
            models.Index(fields=['id']),
            models.Index(fields=['description']),
            models.Index(fields=['latitude']),
            models.Index(fields=['longitude']),
            models.Index(fields=['article_content']),
            models.Index(fields=['article_content_multilang']),
            models.Index(fields=['created_at']),
            models.Index(fields=['image_url']),
            models.Index(fields=['article_content']),
            models.Index(fields=['article_content_multilang']),
            models.Index(fields=['created_at']),
            models.Index(fields=['image_url']),
        ]
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
            models.Index(fields=['destination']),
            models.Index(fields=['language_code']),
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


class CityGuide(models.Model):
    """
    Comprehensive city guides - broader lifestyle/travel content beyond golf.
    Each guide is a specific language version of content for a city/destination.
    Follows the same multi-language pattern as DestinationGuide for maximum flexibility.
    """
    
    # Link to destination and language
    destination = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='city_guides'
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
    
    # SEO and title fields
    title = models.CharField(
        max_length=300, 
        blank=True,
        help_text="SEO-optimized title for this language version"
    )
    slug = models.SlugField(
        max_length=300,
        blank=True,
        help_text="Auto-generated from destination and language"
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True,
        help_text="Meta description for search engines"
    )
    
    # Main content sections
    overview = models.TextField(help_text="City overview and introduction")
    
    # Structured content as JSON for flexibility
    neighborhoods = models.JSONField(
        default=dict, 
        help_text="Neighborhoods: {name: {description, highlights, best_for}}"
    )
    attractions = models.JSONField(
        default=dict,
        help_text="Must-see attractions: {name: {description, category, tips}}"
    )
    dining = models.JSONField(
        default=dict,
        help_text="Restaurants & cuisine: {name: {description, cuisine_type, price_range}}"
    )
    nightlife = models.JSONField(
        default=dict,
        help_text="Bars, clubs, entertainment: {name: {description, type, atmosphere}}"
    )
    shopping = models.JSONField(
        default=dict,
        help_text="Shopping areas & markets: {name: {description, specialty, price_range}}"
    )
    transportation = models.JSONField(
        default=dict,
        help_text="Getting around: {type: {description, cost, tips}}"
    )
    accommodation = models.JSONField(
        default=dict,
        help_text="Where to stay: {name: {description, area, price_range}}"
    )
    seasonal_guide = models.JSONField(
        default=dict,
        help_text="Seasonal recommendations: {season: {weather, activities, events}}"
    )
    practical_info = models.JSONField(
        default=dict,
        help_text="Practical travel info: {category: {details, tips}}"
    )
    
    # Golf integration (brief mention, links to full golf guide)
    golf_summary = models.TextField(
        blank=True, 
        help_text="Brief golf overview with link to full golf guide"
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
    content_quality_score = models.FloatField(
        default=0.0,
        help_text="Content quality score (0-100)"
    )
    
    # Generation tracking
    generated_by = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('template', 'Template Generator'),
            ('ollama', 'Ollama LLM'),
            ('openai', 'OpenAI API'),
            ('imported', 'Data Import'),
        ],
        default='template',
        help_text="Method used to generate this content"
    )
    generation_model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specific model used for generation (e.g., 'llama3.1:70b')"
    )
    
    # Publishing and feature flags
    is_published = models.BooleanField(
        default=True,
        help_text="Whether this guide is published and visible"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this guide is featured on the homepage"
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
            models.Index(fields=['destination']),
            models.Index(fields=['language_code']),
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['updated_at']),
        ]
        
    def save(self, *args, **kwargs):
        """Auto-generate slug and update counts on save"""
        if not self.slug:
            self.slug = self.generate_slug()
        
        # Update word/character counts
        self.word_count = self._calculate_word_count()
        self.character_count = self._calculate_character_count()
        
        super().save(*args, **kwargs)
    
    def generate_slug(self):
        """Generate SEO-friendly slug"""
        city = self.destination.city.replace(" ", "-").lower()
        region = self.destination.region_or_state.replace(" ", "-").lower()
        country = self.destination.country.replace(" ", "-").lower()
        
        if self.language_code == 'en':
            return slugify(f"city-guide-{city}-{region}-{country}")
        else:
            return slugify(f"{self.language_code}-city-guide-{city}-{region}-{country}")
    
    def _calculate_character_count(self):
        """Calculate total character count across all content sections"""
        total_chars = 0
        
        # Count text fields
        for field in ['overview', 'golf_summary']:
            content = getattr(self, field, '')
            if content:
                total_chars += len(content)
        
        # Count JSON field content
        for field_data in [self.neighborhoods, self.attractions, self.dining, 
                          self.nightlife, self.shopping, self.transportation,
                          self.accommodation, self.seasonal_guide, self.practical_info]:
            total_chars += self._count_characters_in_json(field_data)
            
        return total_chars
    
    def _count_characters_in_json(self, data):
        """Recursively count characters in JSON data structure"""
        if isinstance(data, dict):
            return sum(self._count_characters_in_json(value) for value in data.values())
        elif isinstance(data, list):
            return sum(self._count_characters_in_json(item) for item in data)
        elif isinstance(data, str):
            return len(data)
        return 0
    
    def _calculate_word_count(self):
        """Calculate total word count across all content sections"""
        total_words = 0
        
        # Count overview
        if self.overview:
            total_words += len(self.overview.split())
        
        # Count golf summary
        if self.golf_summary:
            total_words += len(self.golf_summary.split())
            
        # Count JSON field content
        for field_data in [self.neighborhoods, self.attractions, self.dining, 
                          self.nightlife, self.shopping, self.transportation,
                          self.accommodation, self.seasonal_guide, self.practical_info]:
            total_words += self._count_words_in_json(field_data)
            
        return total_words
    
    def _count_words_in_json(self, data):
        """Recursively count words in JSON data structure"""
        if isinstance(data, dict):
            return sum(self._count_words_in_json(value) for value in data.values())
        elif isinstance(data, list):
            return sum(self._count_words_in_json(item) for item in data)
        elif isinstance(data, str):
            return len(data.split())
        return 0
    
    def get_absolute_url(self):
        """Get URL for this specific language guide"""
        if self.language_code == 'en':
            return reverse('destinations:city_guide_detail', kwargs={'slug': self.slug})
        else:
            return reverse('destinations:city_guide_detail_lang', kwargs={
                'language': self.language_code, 
                'slug': self.slug
            })
    
    def get_reading_time(self):
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        if self.word_count:
            return max(1, round(self.word_count / 200))
        return 0
    
    def get_sections_summary(self):
        """Get summary of available content sections"""
        sections = []
        if self.neighborhoods:
            sections.append(f"{len(self.neighborhoods)} neighborhoods")
        if self.attractions:
            sections.append(f"{len(self.attractions)} attractions")
        if self.dining:
            sections.append(f"{len(self.dining)} dining spots")
        if self.nightlife:
            sections.append(f"{len(self.nightlife)} nightlife venues")
        if self.shopping:
            sections.append(f"{len(self.shopping)} shopping areas")
        return sections
    
    def get_content_sections(self):
        """Get all content sections as a dictionary for easy iteration"""
        return {
            'neighborhoods': self.neighborhoods,
            'attractions': self.attractions,
            'dining': self.dining,
            'nightlife': self.nightlife,
            'shopping': self.shopping,
            'transportation': self.transportation,
            'accommodation': self.accommodation,
            'seasonal_guide': self.seasonal_guide,
            'practical_info': self.practical_info,
        }
    
    def has_substantial_content(self):
        """Check if the guide has substantial content across multiple sections"""
        content_sections = self.get_content_sections()
        populated_sections = sum(1 for section in content_sections.values() if section)
        return populated_sections >= 3 and self.word_count > 500
    
    def get_available_languages_for_destination(self):
        """Get all available languages for this destination's city guides"""
        return list(
            CityGuide.objects.filter(destination=self.destination)
            .values_list('language_code', flat=True)
            .distinct()
        )
    
    def __str__(self):
        return f"{self.destination.city} City Guide ({self.get_language_code_display()})"


# Cache invalidation for city guides
@receiver([post_save, post_delete], sender=CityGuide)
def invalidate_city_guide_cache(sender, **kwargs):
    """Invalidate city guide cache when guides change"""
    if hasattr(kwargs.get('instance'), 'destination'):
        dest = kwargs['instance'].destination
        # Clear city guide detail page cache
        cache.delete(f'city_guide_detail_{dest.generate_slug()}')
        # Clear city guide listing cache
        cache.delete('city_guides_grid')
