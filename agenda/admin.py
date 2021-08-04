from django.contrib import admin
from agendalilio.models import Event, token_google_user

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'patients_name', 'description', 'email', 'whatsapp',
                    'start_datetime', 'finish_datetime', 'location', 'google_event_id', 'user_id']

@admin.register(token_google_user)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'token', 'user_id']
