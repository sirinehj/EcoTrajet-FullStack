from django.contrib import admin
from .models import UserProfile  # Correct import using the actual model name

@admin.register(UserProfile)  # Replace 'Profile' with 'UserProfile'
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    """
    list_display = ('user', 'phone_number', 'music_preference', 'created_at', 'updated_at')
    list_filter = ('music_preference', 'animal_preference', 'smoking_preference', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Preferences', {
            'fields': ('phone_number', 'profile_picture', 'music_preference', 'animal_preference', 'smoking_preference')
        }),
        ('Rating Information', {
            'fields': ('total_rating', 'rating_count', 'average_rating')
        }),
        ('Communities', {
            'fields': ('communities',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # Make average_rating readable in the admin (it's a property)
    def average_rating(self, obj):
        return obj.average_rating
    average_rating.short_description = 'Average Rating'