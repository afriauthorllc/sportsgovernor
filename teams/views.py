from django.shortcuts import render, get_object_or_404
from teams.models import Team
from live.models import Standing
from matches.models import League, Match

def team_list(request):
    league_id = request.GET.get('league')
    standings = Standing.objects.select_related('team', 'league').order_by('league__name', 'position')
    if league_id:
        standings = standings.filter(league_id=league_id)
    leagues = League.objects.filter(standings__isnull=False).distinct().order_by('name')
    return render(request, 'teams/team_list.html', {'standings': standings, 'leagues': leagues})

def team_detail(request, pk=None, team_id=None):
    from django.utils import timezone
    import requests
    from django.conf import settings
    team_id = team_id or pk
    team = get_object_or_404(Team, pk=team_id)
    standing = Standing.objects.filter(team=team).select_related('league').first()
    now = timezone.now()

    # --- LAST 5 PLAYED - REAL SCORES from Football-Data ---
    show_all = request.GET.get('show') == 'all'
    limit = 15 if show_all else 5
    last_results = []

    # Safe external_id - if blank, skip API call, don't crash
    try:
        ext_id = int(team.external_id) if team.external_id else None
    except (ValueError, TypeError):
        ext_id = None

    if ext_id:
        try:
            headers = {'X-Auth-Token': settings.FOOTBALL_DATA_KEY}
            r = requests.get(
                f"https://api.football-data.org/v4/teams/{ext_id}/matches?status=FINISHED&limit={limit}",
                headers=headers, timeout=10
            )
            if r.status_code == 200:
                for m in r.json().get('matches', []):
                    score = m.get('score', {}).get('fullTime', {})
                    home, away = score.get('home'), score.get('away')
                    if home is None or away is None:
                        continue
                    is_home = m['homeTeam']['id'] == ext_id
                    my = home if is_home else away
                    opp = away if is_home else home
                    result = 'W' if my > opp else 'D' if my == opp else 'L'
                    last_results.append({
                        'date': m['utcDate'][:10],
                        'competition': m['competition']['name'],
                        'home_name': m['homeTeam']['name'],
                        'away_name': m['awayTeam']['name'],
                        'home_score': home,
                        'away_score': away,
                        'is_home': is_home,
                        'venue_label': 'Home' if is_home else 'Away',
                        'result': result,
                        'my_score': my,
                        'opp_score': opp,
                    })
                last_results = list(reversed(last_results))
        except Exception as e:
            print(f"Results fetch error for {team.name}: {e}")

    # --- UPCOMING - from your Odds DB ---
    all_matches = Match.objects.filter(home_team__icontains=team.name) | Match.objects.filter(away_team__icontains=team.name)
    upcoming = all_matches.filter(commence_time__gte=now).order_by('commence_time')[:5]

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'standing': standing,
        'last_matches': last_results,
        'upcoming': upcoming,
        'show_all': show_all,
    })
