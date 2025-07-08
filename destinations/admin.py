from django.contrib import admin
from .models import Destination, DestinationGuide, CityGuide

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'city', 'country']
    readonly_fields = ['created_at']

@admin.register(DestinationGuide)
class DestinationGuideAdmin(admin.ModelAdmin):
    list_display = ['destination', 'language_code', 'word_count', 'generated_by', 'created_at']
    list_filter = ['language_code', 'generated_by', 'created_at']
    search_fields = ['destination__name', 'destination__city', 'title']
    readonly_fields = ['slug', 'word_count', 'character_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('destination', 'language_code', 'title', 'content')
        }),
        ('SEO', {
            'fields': ('slug', 'meta_description')
        }),
        ('Metadata', {
            'fields': ('word_count', 'character_count', 'generated_by', 'generation_model'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destination')


@admin.register(CityGuide)
class CityGuideAdmin(admin.ModelAdmin):
    list_display = [
        'destination', 'language_code', 'word_count', 'character_count', 
        'generated_by', 'is_published', 'is_featured', 'updated_at'
    ]
    list_filter = [
        'language_code', 'generated_by', 'is_published', 'is_featured',
        'destination__country', 'created_at', 'updated_at'
    ]
    search_fields = [
        'destination__name', 'destination__city', 'destination__country',
        'title', 'overview'
    ]
    readonly_fields = [
        'slug', 'word_count', 'character_count', 'created_at', 
        'updated_at', 'last_generated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('destination', 'language_code', 'title', 'overview')
        }),
        ('Content Sections', {
            'fields': (
                'neighborhoods', 'attractions', 'dining', 'nightlife', 
                'shopping', 'transportation', 'accommodation', 
                'seasonal_guide', 'practical_info'
            ),
            'classes': ('collapse',)
        }),
        ('Golf Integration', {
            'fields': ('golf_summary',)
        }),
        ('SEO & Publishing', {
            'fields': ('slug', 'meta_description', 'is_published', 'is_featured')
        }),
        ('Content Metadata', {
            'fields': (
                'word_count', 'character_count', 'content_quality_score',
                'generated_by', 'generation_model'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destination')
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form to show helpful information"""
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text for JSON fields
        json_fields = [
            'neighborhoods', 'attractions', 'dining', 'nightlife', 
            'shopping', 'transportation', 'accommodation', 
            'seasonal_guide', 'practical_info'
        ]
        
        for field_name in json_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget.attrs['rows'] = 10
                form.base_fields[field_name].widget.attrs['cols'] = 80
        
        return form
