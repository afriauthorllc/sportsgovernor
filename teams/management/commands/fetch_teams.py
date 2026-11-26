# teams/management/commands/fetch_teams.py
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from matches.models import League
from teams.models import Team, TeamStat
from live.models import Standing

class Command(BaseCommand):
    help = 'Fetches Teams + Standings from Football-Data.org (free, current season)'

    def handle(self, *args, **options):
        token = settings.FOOTBALL_DATA_KEY
        headers = {'X-Auth-Token': token}
        base = "https://api.football-data.org/v4"

        # Football-Data codes: PL, PD, SA, BL1, FL1, CL, EL
        competitions = [
    ('PL', 'Premier League'),
    ('PD', 'La Liga'),
    ('SA', 'Serie A'),
    ('BL1', 'Bundesliga'),
    ('FL1', 'Ligue 1'),
    ('CL', 'Champions League'),
]

        total = 0
        for code, league_name in competitions:
            r = requests.get(f"{base}/competitions/{code}/standings", headers=headers)
            if r.status_code != 200:
                self.stdout.write(f"{league_name}: Error {r.status_code} - {r.text[:200]}")
                continue
            data = r.json()
            # For CL / EL there are multiple groups, we take total table if available else first group
            tables = data.get('standings', [])
            if not tables:
                continue
            # Use TOTAL table if exists, else first
            table = next((t for t in tables if t['type'] == 'TOTAL'), tables[0])
            rows = table['table']

            league, _ = League.objects.get_or_create(name=league_name)

            for row in rows:
                t = row['team']
                team, _ = Team.objects.update_or_create(
                    external_id=str(t['id']),
                    defaults={
                        'league': league,
                        'name': t['name'],
                        'short_name': t.get('shortName', '') or t['name'][:3].upper(),
                        'crest_url': t.get('crest', ''),
                        'position': row['position'],
                        'points': row['points'],
                        'form': row.get('form', '') or '',
                    }
                )
                TeamStat.objects.update_or_create(
                    team=team,
                    defaults={
                        'played': row['playedGames'],
                        'won': row['won'],
                        'drawn': row.get('draw', 0),
                        'lost': row['lost'],
                        'goals_for': row['goalsFor'],
                        'goals_against': row['goalsAgainst'],
                    }
                )
                Standing.objects.update_or_create(
                    league=league, team=team,
                    defaults={
                        'position': row['position'],
                        'played': row['playedGames'],
                        'won': row['won'],
                        'drawn': row.get('draw', 0),
                        'lost': row['lost'],
                        'goals_for': row['goalsFor'],
                        'goals_against': row['goalsAgainst'],
                        'points': row['points'],
                        'form': row.get('form', '') or '',
                    }
                )
                total += 1
            self.stdout.write(f"{league_name}: Saved {len(rows)} teams")

        self.stdout.write(self.style.SUCCESS(f"Done! Total Teams/Standings: {total}"))
