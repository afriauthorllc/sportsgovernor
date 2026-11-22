from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Team, TeamStat
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'position', 'points', 'form']
    list_filter = ['league']
    search_fields = ['name']
@admin.register(TeamStat)
class TeamStatAdmin(admin.ModelAdmin):
    list_display = ['team', 'played', 'won', 'drawn', 'lost', 'goals_for']
    
    