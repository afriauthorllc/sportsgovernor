from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from matches.models import Match
from .models import BetSlip, BetSlipSelection, GeneratedCombination
from .utils import generate_all_combinations
from decimal import Decimal

def match_list(request):
    matches = Match.objects.filter(status='SCHEDULED', odds__isnull=False).select_related('odds', 'league').order_by('commence_time')
    return render(request, 'calculator/match_list.html', {'matches': matches})

@require_POST
def create_slip(request):
    match_ids = request.POST.getlist('match_ids')
    stake = Decimal(request.POST.get('stake', '1000'))

    if len(match_ids) < 2:
        return redirect('match_list')

    matches = Match.objects.filter(id__in=match_ids, odds__isnull=False).select_related('odds')

    if len(matches) < 2:
        return redirect('match_list')

    matches_with_odds = []
    for m in matches:
        matches_with_odds.append({
            'match': str(m),
            'match_id': m.id,
            'odds': {'1': m.odds.home_win, 'X': m.odds.draw, '2': m.odds.away_win}
        })

    combinations = generate_all_combinations(matches_with_odds)

    slip = BetSlip.objects.create(stake=stake, total_combinations=len(combinations))

    for m in matches:
        BetSlipSelection.objects.create(betslip=slip, match=m)

    for combo in combinations:
        GeneratedCombination.objects.create(
            betslip=slip,
            combination_number=combo['combination_number'],
            picks=combo['picks'],
            combined_odds=combo['combined_odds'],
            potential_win=stake * combo['combined_odds']
        )

    return redirect('slip_detail', slip_id=slip.id)

def slip_detail(request, slip_id):
    slip = get_object_or_404(BetSlip, id=slip_id)
    combinations = slip.combinations.all()
    return render(request, 'calculator/slip_detail.html', {'slip': slip, 'combinations': combinations})
        
from django.utils import timezone
from datetime import timedelta
from matches.models import Match, League
from live.models import Standing
from teams.models import Team

def home(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # LIVE NOW
    live_matches = Match.objects.filter(status__icontains='live').order_by('commence_time')[:3]

    # NEXT KICKOFF if no live
    next_match = Match.objects.filter(commence_time__gte=now).order_by('commence_time').first()

    # TODAY - 6 only
    today_matches = Match.objects.filter(
        commence_time__gte=today_start,
        commence_time__lt=today_end
    ).select_related('league').order_by('commence_time')[:6]
    today_count = Match.objects.filter(
        commence_time__gte=today_start,
        commence_time__lt=today_end
    ).count()

    # PREMIER LEAGUE TOP 5
    try:
        pl = League.objects.filter(name__icontains='Premier League').first()
        top5 = Standing.objects.filter(league=pl).select_related('team').order_by('position')[:5] if pl else []
    except Exception:
        top5 = []

    # TEAMS TO WATCH - 6 with form
    teams_watch = Team.objects.all()[:6]

    q = request.GET.get('q', '')
    if q:
        teams_watch = Team.objects.filter(name__icontains=q)[:6]
        today_matches = Match.objects.filter(home_team__icontains=q) | Match.objects.filter(away_team__icontains=q)
        today_matches = today_matches.order_by('commence_time')[:6]

    return render(request, 'calculator/home.html', {
        'live_matches': live_matches,
        'next_match': next_match,
        'today_matches': today_matches,
        'today_count': today_count,
        'top5': top5,
        'teams_watch': teams_watch,
        'q': q,
    })
    
        
        