from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'usn', 'section', 'food_type', 'is_used', 'email_sent']
    list_filter   = ['food_type', 'is_used', 'email_sent', 'section']
    search_fields = ['name', 'usn']
    readonly_fields = ['qr_id', 'created_at']