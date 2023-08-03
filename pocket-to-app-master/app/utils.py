import random
from app.models import *
from . mydebugger import debug
from app.medals import *
from django.utils import timezone
import datetime
from datetime import datetime
import pytz
import re
from django.core.paginator import Paginator

def get_random_pairings(playernames, tournament: Tournament):
    """ Given list of playernames shuffles it and then pairs the players in sets
        of two

    Args:
        playernames: list
            list of player names
            example:
            ['Kealin', 'Heinrich', 'Joesph', 'Hermann']
        tournamentname: string
            name of a tournament
            exmaple:
            ['Tournament 1']

    Returns:
        A list that denotes player pairings as lists.
        example:
        [['Keailn', 'Heinrich'], ['Joseph', 'Hermann']]
    """
    random.shuffle(playernames)
    pairings = list(zip(playernames[0::2], playernames[1::2]))
    num = 1
    for p1_name, p2_name in pairings:
        match = Match()
        firstRound = '1'
        match.name = 'match' + str(num) + '-' + firstRound
        match.player1 = get_player_from_name(p1_name)
        match.player2 = get_player_from_name(p2_name)
        if match.player1.name == "Bye":
            match.winner = match.player2
        elif match.player2.name == "Bye":
            match.winner = match.player1
        match.save()
        tournament.matches.add(match)
        tournament.save()
        num += 1

def get_pairings(tournament_name: str, round_num: int):
    """sorts players into two people pairs based on their score, assigns a Bye
    to the lowest scoring player if there are an odd number of players

    Args:
        tournament_name: str
            name of a tournament
            example:
            "Tournament 2"

    Returns:
        Tuple containing the pairings of players
        example:
            ([['Keailn', 'Heinrich'], ['Joseph', 'Hermann']])
            ([['Keailn', 'Heinrich'], ['Joseph', 'Bye']])

    """
    tournament = Tournament.objects.get(name=tournament_name)
    playernames = tournament.participants.all()
    playername2score = {playername:
     tournament.matches.filter(winner=playername).count() for playername
      in playernames}
    sorted_players = sorted(playername2score,
        key=playername2score.get, reverse=True)
    num = 1
    for p1_name, p2_name in zip(sorted_players[0::2], sorted_players[1::2]):
        match = Match()
        match.player1 = get_player_from_name(p1_name)
        match.player2 = get_player_from_name(p2_name)
        match.round_num = round_num
        match.name = 'match' + str(num) + '-' + str(round_num)
        if match.player1.name == "Bye":
            match.winner = match.player2
        elif match.player2.name == "Bye":
            match.winner = match.player1
        match.save()
        tournament.round_num = round_num
        tournament.matches.add(match)
        tournament.save()
        num += 1

def get_recent_players():
    # p2date = {}
    # for p in Player.objects.all():
    #     p2date[p] = p.tournament_set.order_by('date_end').first().date_end
    # return list(sorted(p2date, key=p2date.get))
    players = list(Player.objects.filter(~Q(name='Draw') & ~Q(name='Bye')))
    if (Tournament.objects.exists()):
        tournament = Tournament.objects.last()
        recent = list(tournament.participants.filter(
            ~Q(name='Draw') & ~Q(name='Bye')))
        for recentplayer in recent:
            players.remove(recentplayer)
        playerlist = [recplayer for recplayer in recent]
        for player in players:
            playerlist.append(player)
        return playerlist
    else:
        return players

def get_player_history(playername: str):
    """gets a list containing all the Tournaments a player has participated in.

    Args: playername: str
        name of the player you want to search
        example:
        "Kealin"

    Returns:
        tuple containing a list of tournament objects that this player was in.
        example:
        [Tournament object 1, Tournament object 2]

    """
    player = Player.objects.get(name=playername)
    history = Tournament.objects.filter(participants=player, running=False)
    return history

def get_player_match_history(playername: str, tournamentname:str):
    """gets all the matches a given player had played in the given tournament.

    Args:
     playername: str
        name of the player you want to search
        example:
        "Heinrich"
    tournamentname: str
        name of the tournament you wish to get matches from.
        example:
        "Tournament 1"

    Returns:
        tuple containing a list of match objects that this player was in.
        example:
        [Match object 1, Match object 2]

    """
    tournament = Tournament.objects.get(name=tournamentname)
    player = Player.objects.get(name=playername)
    matches = (tournament.matches.filter(player1=player) |
        tournament.matches.filter(player2 = player))

    history = [tournament]
    medals = []
    for match in matches:
        hist = []
        hist.append(match.winner)
        if playername == match.player1.name:
            hist.append(match.player1)
            hist.append(match.player2)
        else:
            hist.append(match.player2)
            hist.append(match.player1)
        hist.append(match.round_num)
        history.append(hist)

    return history

def get_player_tops(name: str):
    """creates a dictionary that displays the percantage of times a player had
    placed in a certain top amount.
    Args:
        name
        name of the player you wish to create the dictionary for.
        example:
        "Joseph"


    """
    playername = Player.objects.get(name=name)
    history = get_player_history(name)
    topdict = {"top50" :0,
    "top8": 0,
    "top4": 0,
    "tops": 0}
    total = history.count()
    for tournament in history:
        players = tournament.participants.all()
        playername2score = {player:
        tournament.matches.filter(winner=player).count() for player in players}
        sorted_players = sorted(playername2score, key=playername2score.get, reverse=True)
        if playername in sorted_players[:len(sorted_players)]:
            topdict["top50"] += float(1)
            if playername in sorted_players[:8]:
                topdict["top8"] += float(1)
            if playername in sorted_players[:4]:
                topdict["top4"] += float(1)
            if playername in sorted_players[:1]:
                topdict["tops"] += float(1)
    for dict in topdict:
        topdict[dict]//total
    return topdict

def tournament_scores(tournamentname: str):
    tournament = Tournament.objects.get(name=tournamentname)
    players = tournament.participants.filter(~Q(name='Draw') & ~Q(name='Bye'))
    playername2score = {
        player: tournament.matches.filter(
            winner=player,
        ).count() for player in players
    }
    sorted_players = sorted(playername2score.items(), key=lambda item: item[1],
     reverse=True)
    return sorted_players


def get_draw():
    if Player.objects.get(name="Draw"):
        draw = Player.objects.get(name="Draw")
    else:
        draw = Player()
        draw.name = "Draw"
    return draw

def undo_select(match_name, urlname):
    tournament = Tournament.objects.get(url=urlname)
    match = tournament.matches.filter(name=match_name)[0]
    match.winner=None
    match.save()
    tournament.save()

def get_player_from_name(name: str):
    """ fetches player from datatbase with given name """
    if (Player.objects.filter(name=name).exists()):
        return Player.objects.get(name=name)

def calculate_tournamentwl(playername:str, tournamentname:str):
    player = Player.objects.get(name=playername)
    tournament = Tournament.objects.get(name=tournamentname)
    matches = (tournament.matches.filter(player1=player)|
    tournament.matches.filter(player2=player))
    total = matches.count()
    wins = matches.filter(winner=player).count()
    wl_ratio = float(wins//total)
    losses = total - wins
    return wins, losses, wl_ratio

def seasonal_winlost(playername:str, seasonname:str):
    player = Player.objects.get(name=playername)
    season = Season.objects.get(name=seasonname)
    tournaments = season.events.all()
    matches = (tournament.matches.filter(player1=player)|
    tournament.matches.filter(player2=player))
    total = matches.count()
    wins = matches.filter(winner=player).count()
    wl_ratio = float(wins//total)
    losses = total - wins
    return wins, losses, wl_ratio

def calculate_globalwl(playername:str):
    player = Player.objects.get(name=playername)
    tournaments = Tournament.objects.filter(participants=player)
    matches = (tournament.matches.filter(player1=player)|
    tournament.matches.filter(player2=player))
    total = matches.count()
    wins = matches.filter(winner=player).count()
    wl_ratio = float(wins//total)
    losses = total - wins
    return wins, losses, wl_ratio

# def display_true_rankings(tournament: Tournament):
#     participants = tournament.participants.all()
#     player_rankings = {player.name :
#     calculate_tournamentwl(player, tournament.name)[2] for player in participants}
#     sorted_rankings = sorted(player_rankings, key=player_rankings.get, reverse=True)
    
#     return sorted_rankings
    


def get_time():
    today = datetime.today()
    month = today.month
    year = today.year
    return month, year, today

def manage_seasons(season_name: str, tournament: Tournament):
    if not Season.objects.filter(name=season_name).exists():
        default_name = get_default_season_name()
        if default_name == season_name:
            circuit = False
            register_season(default_name, circuit)
        else:
            circuit = True
            register_season(season_name, circuit)
    season = get_season(season_name)
    append_to_season(season, tournament)

# def set_season_time(season_name: str, start: datetime, end: datetime):
#     season = Season.objects.get(name=season_name)
#     season.date_start = start
#     season.date_end = end
#     season.save()

'''def search_for_seasons():
    seasons = Season.objects.all()
    for season2 in seasons:
        if tournament.date_start <= season2.date_end >= season2.date_start:
            season2.events.add(tournament)
            season2.save()
            break
'''

def get_default_season_name():
    """Create's a season that assigns all tournaments within the timeframe into
    a season object"""
    month = get_time()[0]
    year = get_time()[1]
    if  1 <= month <= 3:
        name = "Q1"
    elif 4 <= month <= 6:
        name = "Q2"
    elif 7 <= month <= 9:
        name = "Q3"
    else:
        name = "Q4"
    season_name = f"{year} {name}"
    return season_name

def register_season(season_name: str, circut: bool):
    #  start: datetime, end:datetime
    """Plain season creation"""
    utc=pytz.UTC
    season = Season()
    season.name = season_name
    season.circut = circut
    season.url = (re.sub("[^0-9a-zA-Z]+", "", season_name))
    season.date_start = timezone.now()
    season.save()

def append_to_season(season: Season, tournament: Tournament):
    season.events.add(tournament)
    season.save()

def get_season(season_name: str):
    if (Season.objects.filter(name=season_name).exists()):
        return Season.objects.get(name=season_name)

def get_tournament_stats(tournaments: Tournament):
    listoftournaments = []
    for tournament in tournaments:
        adict = {
            'name': tournament.name,
            'end_date': tournament.date_end.strftime("%d/%m/%Y"),
            'url': tournament.url, 
            "isRunning": tournament.running,
        }
        listoftournaments.append(adict)

    return listoftournaments

def get_season_stats(seasons: Season):
    listofseasons = []
    for season in seasons:
        adict = {
            'name': season.name,
            'start_date': season.date_start.strftime("%d/%m/%Y"),
            'url': season.url, 
        }
        listofseasons.append(adict)

    return listofseasons

def get_tournament_pagination (request, listoftournaments: list): 
    paginator = Paginator(listoftournaments, 10)
    page_number = request.GET.get('page')
    tournamentspages = paginator.get_page(page_number)
    page_number = int(page_number)
    lastpage = int(tournamentspages.paginator.num_pages)
    page_list = range(lastpage , 0, -1)

    context = {
        'tournaments': listoftournaments,
        'tournamentspages': tournamentspages, 
        'page_number': page_number,
        'page_list': page_list,
        'lastpage': lastpage
    }

    return context