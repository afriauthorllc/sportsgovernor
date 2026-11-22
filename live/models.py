from django.db import models

# Create your models here.
from django.db import models
from matches.models import Match, League
from teams.models import Team

class LiveEvent(models.Model):
    EVENT_TYPES = [
        ('GOAL', 'Goal'),
        ('CARD_YELLOW', 'Yellow Card'),
        ('CARD_RED', 'Red Card'),
        ('SUB', 'Substitution'),
        ('PENALTY', 'Penalty'),
        ('FULLTIME', 'Full Time'),
    ]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="events")
    minute = models.IntegerField(default=0)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    team_name = models.CharField(max_length=100, blank=True)
    player = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200, blank=True)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-minute']

    def __str__(self):
        return f"{self.minute}' {self.event_type} - {self.match}"

class Standing(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="standings")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="standings")
    position = models.IntegerField()
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    form = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ['league', 'position']
        unique_together = ['league', 'team']

    def __str__(self):
        return f"{self.league.name} #{self.position} {self.team.name}"
        
        