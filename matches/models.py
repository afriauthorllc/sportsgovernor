from django.db import models

# Create your models here.
from django.db import models

class League(models.Model):
    name = models.CharField(max_length=100)  # e.g. Premier League
    sport = models.CharField(max_length=50, default="Soccer")
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('FINISHED', 'Finished'),
        ('CANCELLED', 'Cancelled'),
    ]

    # This is the ID from The Odds API / API-Football.
    # This stops duplicates when your cron job runs every 15 mins
    external_id = models.CharField(max_length=100, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="matches")
    home_team = models.CharField(max_length=100)  # Team A
    away_team = models.CharField(max_length=100)  # Team B
    commence_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['commence_time']

    def __str__(self):
        return f"{self.home_team} v {self.away_team}"

class MatchOdds(models.Model):
    # OneToOne = One match has one set of odds at a time
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name="odds")
    bookmaker = models.CharField(max_length=100, default="Average")
    
    # This is your 1, X, 2
    home_win = models.DecimalField(max_digits=5, decimal_places=2)  # 1.5
    draw = models.DecimalField(max_digits=5, decimal_places=2)      # 2.0
    away_win = models.DecimalField(max_digits=5, decimal_places=2)   # 2.4
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.match} - 1:{self.home_win} X:{self.draw} 2:{self.away_win}"
        
        