from django.core.management.base import BaseCommand
from app.models import Tournament, Match, Player
from itertools import islice
from app.utils import *
import math

class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **kwargs):
        Player.objects.all().delete()
        batch_size = 32
        objs = (Player(name="Player %s" % i) for i in range(32))
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            Player.objects.bulk_create(batch, batch_size)
        Tournament.objects.all().delete()
        t = Tournament()
        t.name = "masspopulate tournament"
        t.save()
        players = Player.objects.all()
        for player in players:
            t.participants.add(player)
        t.save()
        self.simulate_tournament(t)

    def simulate_tournament(self, tournament: Tournament):
        # create random pairings at first
        playernames = [ player.name for player in tournament.participants.all() ]
        playername2score = { playername: 0 for playername in playernames }

        max_wins = math.log2(len(playernames))
        # simulate tournament
        round_num = 0
        while max(playername2score.values()) < max_wins:
            round_num += 1
            # get pairings
            pairings, bye = get_pairings(playername2score)
            # face each off
            for winner_name, loser_name in pairings:
                winner = get_player_from_name(winner_name)
                loser = get_player_from_name(loser_name)
                m = Match()
                m.player1 = winner
                m.player2 = loser
                m.winner = winner
                m.round_num = round_num
                m.save()
                #add to tournament
                # add win to winenr
                tournament.matches.add(m)
                playername2score[winner_name] += 1
