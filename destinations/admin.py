from django.contrib import admin
from .models import Destination, DestinationGuide

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
