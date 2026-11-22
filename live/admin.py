from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LiveEvent, Standing
@admin.register(LiveEvent)
class LiveEventAdmin(admin.ModelAdmin):
    list_display = ['match', 'minute', 'event_type', 'player', 'home_score', 'away_score']
    list_filter = ['event_type']
@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ['league', 'position', 'team', 'played', 'points', 'form']
    list_filter = ['league']
    