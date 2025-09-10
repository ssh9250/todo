from django.contrib import admin
from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'completed', 'created_at', 'updated_at']
    list_filter = ['completed']
    search_fields = ['title', 'description']
    list_editable = ['completed']
    ordering = ['-created_at']
