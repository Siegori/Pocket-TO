from django.db import models
from django.utils import timezone
import datetime

class Medal(models.Model):
    name = models.CharField(default='', max_length=100)
    tournament = models.ForeignKey(
        'Tournament',
        null=True,
        on_delete=models.CASCADE,
        related_name="tournament"
    )
    player = models.ForeignKey(
        'Player',
        null=True,
        on_delete=models.CASCADE,
        related_name="player"
    )

class Player(models.Model):
    name = models.CharField(default='', max_length=100, unique=True)
    score = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    def __str__(self):
        return self.name


class Match(models.Model):
    name = models.CharField(default='', max_length=100)
    round_num = models.IntegerField(default=1)
    player1 = models.ForeignKey(
        "Player",
        null=True,
        on_delete=models.CASCADE,
        related_name="player1"
    )
    player2 = models.ForeignKey(
        "Player",
        null=True,
        on_delete=models.CASCADE,
        related_name="player2"
    )
    winner = models.ForeignKey(
        "Player",
        null=True,
        default=None,
        blank=True,
        on_delete=models.CASCADE,
        related_name="winner"
    )


class Tournament(models.Model):
    running = models.BooleanField(default=True)
    name = models.CharField(default='', max_length=100)
    round_num = models.IntegerField(default=1)
    participants = models.ManyToManyField(
        'Player',
        related_name="+"
    )
    matches = models.ManyToManyField(
        'Match',
        related_name="+"
    )
    date_start = models.DateTimeField(
        default=timezone.now,
        editable=True,
        blank=True
    )
    date_end = models.DateTimeField(
        default=timezone.now,
        editable=True,
        blank=True)
    url = models.CharField(default='', max_length=100)

class Season(models.Model):
    name = models.CharField(default='', max_length=100, unique=True)
    date_start = models.DateTimeField(
        default=timezone.now,
        editable=True,
        blank=True
    )
    date_end = models.DateTimeField(
        default=timezone.now,
        editable=True,
        blank=True
    )
    events = models.ManyToManyField(
        'Tournament',
        related_name="+"
    )
    circut = models.BooleanField(default=False)
    url = models.CharField(default='', max_length=100)
