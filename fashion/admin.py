from django.contrib import admin
from .models import CustomUser, Feedback

admin.site.register(CustomUser)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rating', 'created_at', 'is_featured')
    list_filter = ('rating', 'category', 'is_featured', 'created_at')
    search_fields = ('name', 'email', 'comment')
    list_editable = ('is_featured',)
