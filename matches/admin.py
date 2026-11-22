from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import League, Match, MatchOdds

class MatchOddsInline(admin.TabularInline):
    model = MatchOdds
    extra = 0

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['name', 'sport', 'country']
    search_fields = ['name']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'league', 'commence_time', 'status']
    list_filter = ['status', 'league', 'commence_time']
    search_fields = ['home_team', 'away_team']
    inlines = [MatchOddsInline]

@admin.register(MatchOdds)
class MatchOddsAdmin(admin.ModelAdmin):
    list_display = ['match', 'home_win', 'draw', 'away_win', 'bookmaker', 'last_updated']
    list_filter = ['bookmaker']
    
    