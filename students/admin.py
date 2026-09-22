from django.contrib import admin, messages
from django.urls import reverse
from django.core.management import call_command
import threading
from .models import Student

@admin.action(description='Send QR Emails to selected students')
def send_emails_action(modeladmin, request, queryset):
    queryset.update(email_sent=False)
    
    def send():
        try:
            call_command('send_qr_emails')
        except Exception as e:
            print(f"Action email error: {e}")
            
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()
    
    modeladmin.message_user(request, "Emails are now sending to selected students in the background.", messages.SUCCESS)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'usn', 'section', 'food_type', 'is_used', 'email_sent']
    list_filter   = ['food_type', 'is_used', 'email_sent', 'section']
    search_fields = ['name', 'usn']
    readonly_fields = ['qr_id', 'created_at']
    actions = [send_emails_action]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['upload_csv_url'] = reverse('upload_csv')
        extra_context['trigger_send_emails_url'] = reverse('trigger_send_emails')
        return super().changelist_view(request, extra_context=extra_context)