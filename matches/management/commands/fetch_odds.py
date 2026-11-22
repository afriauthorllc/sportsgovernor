import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from matches.models import League, Match, MatchOdds
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        api_key = settings.ODDS_API_KEY
        sports = [
            'soccer_epl',
            'soccer_spain_la_liga',
            'soccer_italy_serie_a',
            'soccer_germany_bundesliga',
            'soccer_france_ligue_one',
            'soccer_uefa_champs_league',
            'soccer_uefa_europa_league',
        ]
        total = 0
        for sport in sports:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            r = requests.get(url, params={'apiKey': api_key, 'regions': 'eu,uk', 'markets': 'h2h', 'oddsFormat': 'decimal'})
            if r.status_code != 200:
                self.stdout.write(f"{sport}: Error {r.status_code}")
                continue
            games = r.json()
            self.stdout.write(f"{sport}: Got {len(games)} games")
            for game in games:
                league, _ = League.objects.get_or_create(name=game.get('sport_title', sport))
                commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                match, _ = Match.objects.update_or_create(
                    external_id=game['id'],
                    defaults={'league': league, 'home_team': game['home_team'], 'away_team': game['away_team'], 'commence_time': commence_time, 'status': 'SCHEDULED'}
                )
                bookmakers = game.get('bookmakers', [])
                if not bookmakers:
                    continue
                # Soccer always has 3 outcomes, so this will now work
                home_list, draw_list, away_list = [], [], []
                for b in bookmakers:
                    try:
                        m = {o['name']: o['price'] for o in b['markets'][0]['outcomes']}
                        home_list.append(m.get(game['home_team']))
                        draw_list.append(m.get('Draw'))
                        away_list.append(m.get(game['away_team']))
                    except:
                        continue
                home_list = [x for x in home_list if x]
                draw_list = [x for x in draw_list if x]
                away_list = [x for x in away_list if x]
                if home_list and draw_list and away_list:
                    MatchOdds.objects.update_or_create(
                        match=match,
                        defaults={
                            'bookmaker': 'Average',
                            'home_win': sum(home_list)/len(home_list),
                            'draw': sum(draw_list)/len(draw_list),
                            'away_win': sum(away_list)/len(away_list),
                        }
                    )
                    total += 1
        self.stdout.write(self.style.SUCCESS(f"Done! Saved/Updated {total} matches"))
        
        