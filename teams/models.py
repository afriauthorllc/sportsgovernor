from django.db import models

# Create your models here.
from django.db import models
from matches.models import League

class Team(models.Model):
    external_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20, blank=True)
    logo_url = models.URLField(blank=True)
    # Form: W W D W W - stored as string, updated by API
    form = models.CharField(max_length=20, default="", blank=True)
    # e.g. "1st • 28 pts" - cached for list page
    position = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def form_list(self):
        # "WWDLW" -> ['W','W','D','L','W']
        return list(self.form) if self.form else []

class TeamStat(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="stats")
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    top_scorer = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.team.name} Stats"
        
        