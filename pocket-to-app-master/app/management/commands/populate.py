from django.core.management.base import BaseCommand
from app.models import *
from itertools import islice

'''
Populate the database with example data
'''
class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **kwargs):
        # TODO: google django bulk creation
        Player.objects.all().delete() # clears database
        kealin = Player.objects.create(name='Kealin')
        heinrich = Player.objects.create(name='Heinrich')
        joseph = Player.objects.create(name='Joseph')
        hermann = Player.objects.create(name='Hermann')
        Tournament.objects.all().delete() 
        Match.objects.all().delete()
        t = Tournament()
        t.name = "example tournament"
        t.save()
        t.participants.add(kealin, heinrich, joseph, hermann)
        # setup matches
        r1m1 = Match(winner=kealin, loser=heinrich, roundcount=1)
        r1m1.save()
        r1m2 = Match(winner=joseph, loser=hermann, roundcount=1)
        r1m2.save()
        r2m1 = Match(winner=kealin, loser=joseph, roundcount=2)
        r2m1.save()
        t.matches.add(r1m1)
        t.matches.add(r1m2)
        t.matches.add(r2m1)
        t.save()

