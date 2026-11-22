from django.db import models

# Create your models here.
from django.db import models
from matches.models import Match

class BetSlip(models.Model):
    """
    A user picks 2, 3, 4 matches. This is that pick.
    Example: User picks A v B + C v D
    """
    created_at = models.DateTimeField(auto_now_add=True)
    stake = models.DecimalField(max_digits=10, decimal_places=2, default=1000)  # e.g. 1000 UGX
    total_combinations = models.IntegerField(default=0)  # e.g. 9

    def __str__(self):
        return f"Slip #{self.id} - {self.total_combinations} combos"

class BetSlipSelection(models.Model):
    """
    The matches the user selected for this slip.
    """
    betslip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="selections")
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.betslip} - {self.match}"

class GeneratedCombination(models.Model):
    """
    ONE row = ONE of the 9 possible outcomes.
    Example: A wins + Draw
    """
    betslip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="combinations")
    combination_number = models.IntegerField()  # 1 to 9, 1 to 27, etc.
    
    # We store it as JSON so it works for 2 matches or 10 matches
    # Example: [{"match": "A v B", "pick": "1", "odd": 1.5}, {"match": "C v D", "pick": "X", "odd": 1.6}]
    picks = models.JSONField()
    
    combined_odds = models.DecimalField(max_digits=10, decimal_places=2)  # 1.5 x 1.6 = 2.40
    potential_win = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['combination_number']

    def __str__(self):
        return f"Combo {self.combination_number} - Odds {self.combined_odds}"
        
        