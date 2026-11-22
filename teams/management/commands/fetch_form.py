import requests, time
from django.core.management.base import BaseCommand
from django.conf import settings
from teams.models import Team
from live.models import Standing

class Command(BaseCommand):
    help = 'Fills form for teams that still have empty form'

    def handle(self, *args, **options):
        token = settings.FOOTBALL_DATA_KEY
        headers = {'X-Auth-Token': token}
        base = "https://api.football-data.org/v4"

        # ONLY teams with empty form - don't re-do the ones that already have badges
        missing = Standing.objects.filter(form__isnull=True) | Standing.objects.filter(form='')
        team_ids = list(missing.values_list('team_id', flat=True).distinct())
        teams = Team.objects.filter(id__in=team_ids)
        print(f"Missing form: {teams.count()} teams")

        for team in teams:
            try:
                r = requests.get(f"{base}/teams/{team.external_id}/matches?status=FINISHED&limit=5", headers=headers)
                if r.status_code != 200:
                    print(f"{team.name}: Error {r.status_code} - skipping, will retry next run")
                    continue
                matches = r.json().get('matches', [])
                forms = []
                for m in reversed(matches):
                    score = m.get('score', {}).get('fullTime', {})
                    home, away = score.get('home'), score.get('away')
                    if home is None or away is None:
                        continue
                    is_home = m['homeTeam']['id'] == int(team.external_id)
                    my = home if is_home else away
                    opp = away if is_home else home
                    forms.append('W' if my > opp else 'D' if my == opp else 'L')
                form_str = ','.join(forms)
                print(f"{team.name}: {form_str}")
                team.form = form_str
                team.save(update_fields=['form'])
                Standing.objects.filter(team=team).update(form=form_str)
                time.sleep(7)  # 10/min limit
            except Exception as e:
                print(f"{team.name}: {e}")
        self.stdout.write(self.style.SUCCESS("Done!"))
