from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import BetSlip, BetSlipSelection, GeneratedCombination

class BetSlipSelectionInline(admin.TabularInline):
    model = BetSlipSelection
    extra = 0

class GeneratedCombinationInline(admin.TabularInline):
    model = GeneratedCombination
    extra = 0
    readonly_fields = ['picks', 'combined_odds', 'potential_win']

@admin.register(BetSlip)
class BetSlipAdmin(admin.ModelAdmin):
    list_display = ['id', 'stake', 'total_combinations', 'created_at']
    inlines = [BetSlipSelectionInline, GeneratedCombinationInline]

@admin.register(GeneratedCombination)
class GeneratedCombinationAdmin(admin.ModelAdmin):
    list_display = ['betslip', 'combination_number', 'combined_odds', 'potential_win']
    list_filter = ['betslip']
    