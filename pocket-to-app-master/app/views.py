from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from app.models import *
import random
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from app.utils import *
from . mydebugger import debug
from app.medals import *
from django.contrib.auth.decorators import login_required
import re

@login_required(login_url="/user_auth/login/")
def home(request):
    """ home page """
    return render(request, 'app/home.html', {'title': 'Home'})

def playerspage(request):
    """ this page handles the listing of players as well as the creation of new
        players.

    Args:
        request
            if this is a POST request, then it is a request to make a new player
            else it is a request to get all of the existing players.
    """
    if request.method == 'POST':
        username = request.POST['username'].strip()

        player = Player.objects.filter(name=username)

        if player:
            messages.error(request, f'Username already exists')
            return redirect('/playerspage')

        player = Player.objects.create(name=username, score=0)
        messages.success(request, f'New player created')
        return redirect('/playerspage')
    else:
        players = Player.objects.filter(~Q(name='Draw') & ~Q(name='Bye'))
        playerscores = {player: player.score for player in players}
        sorted_players = sorted(playerscores, key=playerscores.get, reverse=True)
        ranking_num = list(range(1, len(sorted_players) + 1))
        stats = {
            'title': 'New Tournament',
            'ranking_stats': list(zip(sorted_players, ranking_num)),
        }
        return render(request, 'app/playerspage.html', stats)

def playerstats(request, name: str):
    """ Fetches the stats of the given player

    Args:
        name: str
            name of the player
            example:

            'Kealin'

    Returns:
        dictionary containing the stats of that player
    """
    past_tournaments = get_player_history(name)
    if not past_tournaments:
        messages.error(request, f"Player has yet to participate in a tournament")
        return redirect('/playerspage/')
    history = []
    for tournament in past_tournaments:
        if not tournament.running:
            hist = get_player_match_history(name, tournament.name)
            history.append(hist)

    player = get_player_from_name(name)
    medals = get_player_medals(player)
    ranking_stats = get_player_tops(name)
    all_medals = Medal.objects.values('name').distinct()
    stats = {
        'history': history,
        'medals': medals,
        'name': name,
        'ranking_stats': ranking_stats.items(),
        'all_medals': all_medals,
        'medals_description': get_medals_description(),
    }
    return render(request, 'app/playerstats.html', stats)

def seasonspage(request):
    """ seasons page """
    seasons = Season.objects.all()
    listofseasons = get_season_stats(seasons)
    context = {
        'seasons': listofseasons,
    }
    return render(request, 'app/seasonspage.html', context)

def seasonstats(request, urlname: str):
    """ seasons page """
    season = Season.objects.get(url=urlname)
    tournaments = season.events.all()
    listoftournaments = get_tournament_stats(tournaments)
    context = get_tournament_pagination(request, listoftournaments)
    context['season_name'] = season.name
    return render(request, 'app/seasonstats.html', context)

def tournamentspage(request):
    """ this page handles the listing of tournaments as well as the creation 
        of new tournaments.

    Args:
        request
            if this is a POST request, then it is a request to make a 
            new tournament else it is a request to get 
            all of the existing tournament.
    """
    tournaments = Tournament.objects.all()
    listoftournaments = get_tournament_stats(tournaments)
    context = get_tournament_pagination(request, listoftournaments)
    return render(request, 'app/tournamentspage.html', context)

def createtournamentpage(request):
    if request.method == 'POST':
        names = request.POST.getlist('playernames[]')
        tournament_name = request.POST.get('tournament_name')
        season_name = request.POST.get('season_name')
        tournament_type = request.POST.get('tournament_type')
        tournament_name = tournament_name.strip()
        season_name = season_name.strip()
        tournament = Tournament()
        
        if Tournament.objects.filter(name=tournament_name):
            messages.error(request, f'Tournament name already exists')

            return JsonResponse({
                'success': False,
                })

        tournament.name = tournament_name
        tournament.url = (re.sub("[^0-9a-zA-Z]+", "", tournament_name))
        tournament.date_start = timezone.now()
        tournament.save()
        for name in names:
            player = get_player_from_name(name)
            tournament.participants.add(player)
        if tournament.participants.count() % 2 == 1:
            if Player.objects.filter(name="Bye"):
                bye = Player.objects.get(name="Bye")
                tournament.participants.add(bye)
            else:
                bye=Player()
                bye.name = "Bye"
                bye.save()
                tournament.participants.add(bye)

        tournament.save()
        get_random_pairings(names, tournament)
        manage_seasons(season_name, tournament)
        messages.success(request, f'Tournament Started')

        return JsonResponse({
                'success': True,
                'url': tournament.url,
        })
    else:
        tournament_num = Tournament.objects.count() + 1
        default_season_name = get_default_season_name()
        seasons = Season.objects.filter(~Q(name=default_season_name))
        players = get_recent_players()
        context = {
            'players': players,
            'tournament_num': tournament_num,
            'default_season_name': default_season_name,
            'seasons': seasons,
        }
        return render(request, 'app/createtournamentpage.html', context)

def end_match(request, urlname):
    tournament = Tournament.objects.get(url=urlname)
    allMatches = tournament.matches.all()
    for match in allMatches:
        matchDraw = match.name + 'drawInput'
        if request.POST.get(match.name) or request.POST.get(matchDraw):
            if request.POST.get(matchDraw) == 'drawInput':
                winner = get_draw()
            else:
                winner = request.POST.get(match.name)

            round_num = match.round_num
            match.winner = get_player_from_name(winner)
            match.winner.save()
            match.save()

            round_num = match.round_num
            matches = tournament.matches.filter(round_num=round_num)

            if matches.filter(winner=None).count() == 0:
                # then tournament is over
                for match in allMatches:
                    match.winner.score += 1
                if round_num == len(tournament.participants.all()) // 2:
                    tournament.running = False

                    medals_from_tournament = calc_tournament_medals(tournament)
                    for medal_name, players in medals_from_tournament.items():
                        for player in players:
                            Medal.objects.create(
                                name=medal_name,
                                tournament=tournament,
                                player=player
                            )
                    tournament.date_end = timezone.now()
                    tournament.save()
                else:
                    start_next_round(tournament.name, round_num)


    messages.success(request, f'Winner Added')

def start_next_round(tournament_name: str, prev_round_num: int):
    """
    Args:
        tournament_name: str
            name of the tournamnet
            example:
                "Sample Tournament"
        prev_round_num: int
            the integer value of the previous round
            example:
                2
    Returns:
        dict mapping containing pairings and round_num
        example:
            {'pairings': [['Keailn', 'Heinrich'], ['Joseph', 'Hermann']],
             'round_num': 4}

    """
    round_num = prev_round_num + 1
    get_pairings(tournament_name, round_num)


def tournamentstats(request, urlname: str):
    """ Fetches the stats of the given tournament

    Args:
        urlname: str
            url of the tournament
            example:

            'RegionalChampionshipAugust',
            'Tournament0'
            '2019-05-23'

    Returns:
        dictionary containing the stats of that tournament
    """
    if request.method == 'POST':
        if request.POST.get('undoButton'):
            match_name = request.POST.get('undoButton')
            undo_select(match_name, urlname)
        else:
            end_match(request, urlname)
        return redirect('/tournamentspage/tournamentstats/' + urlname)
    else:
        stats = get_match_details(urlname)
        return render(request, 'app/tournamentstats.html', stats)


def get_match_details(urlname):
    tournament = Tournament.objects.get(url=urlname)
    top = list(tournament.participants.order_by('-score'
        )[:4].values("name", "score"))
    currentRound = tournament.round_num
    numRounds = []
    for x in range(currentRound):
        numRounds.append(x + 1)

    top = tournament_scores(tournament.name)
    participants = list(tournament.participants.filter(~Q(name='Draw') & ~Q(name='Bye')))
    pairings = tournament.matches.filter(
        (~Q(player1__name__contains='Bye') & ~Q(player2__name__contains='Bye'))
        & ~Q(player1__name__contains='Draw') & ~Q(player2__name__contains='Draw')
    )
    all_medals = Medal.objects.values('name').distinct()
    stats = {
        'Name': tournament.name,
        'isRunning': tournament.running,
        'rounds': numRounds,
        'pairings': pairings,
        'participants': participants,
        'top': top,
        'currentRound': currentRound,
        'medals' : get_tournament_medals(tournament),
        'all_medals': all_medals,
        'medals_description': get_medals_description(),
    }
    return stats

def medalspage(request):
    """ medals page """
    medals_context = {
        'medals_description': get_medals_description(),
    }
    return render(request, 'app/medalspage.html', medals_context)