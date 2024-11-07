from django.contrib import admin
from .models import MovieReport


class MovieReportAdmin(admin.ModelAdmin):
    # Customize the columns to display in the list view
    list_display = ('movie', 'get_reported_by_username', 'reason', 'status', 'reported_at')

    # Optional: You can add this method to display the username of the 'user' field in the 'MovieReport' model
    def get_reported_by_username(self, obj):
        return obj.user.username  # Access the username of the related 'User' model

    get_reported_by_username.short_description = 'Reported By'  # Set a custom column header

    # You can also customize the filtering options if needed
    list_filter = ('status', 'reported_at')

    # Optional: Make fields editable in the list view
    list_editable = ('status',)


admin.site.register(MovieReport, MovieReportAdmin)
