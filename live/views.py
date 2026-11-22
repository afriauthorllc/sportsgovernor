from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from matches.models import Match, League
from .models import Standing

from django.shortcuts import render
from django.utils import timezone
from matches.models import Match
from live.models import Standing
from matches.models import League

def live_list(request):
    status = request.GET.get('status', 'today')
    matches = Match.objects.select_related('league').all().order_by('commence_time')
    now = timezone.now()

    if status == 'live':
        matches = matches.filter(status__icontains='live')
    elif status == 'upcoming':
        matches = matches.filter(commence_time__gte=now)
    elif status == 'finished':
        matches = matches.filter(status__icontains='finished') | matches.filter(commence_time__lt=now, status__icontains='scheduled')
        # fallback: if no finished status, just show past matches
        if not matches.exists():
            matches = Match.objects.select_related('league').filter(commence_time__lt=now).order_by('-commence_time')
    # today = all, sorted by time

    return render(request, 'live/live_list.html', {'matches': matches, 'active': status})
        
def standings_list(request):
    # ONLY leagues that have standings - hides WNCAAB, AHL, etc.
    leagues = League.objects.filter(standings__isnull=False).distinct().order_by('name')
    league_id = request.GET.get('league')
    if league_id:
        standings = Standing.objects.filter(league_id=league_id).select_related('team')
        selected = League.objects.get(id=league_id)
    else:
        selected = leagues.first()
        standings = Standing.objects.filter(league=selected).select_related('team') if selected else []
    return render(request, 'live/standings.html', {'leagues': leagues, 'standings': standings, 'selected': selected})
        
        