from django.db.models.query_utils import Q
from app.models import *
from app.utils import *

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
    history = Tournament.objects.filter(participants=player)
    return history

def _loser(matches, player):
    return matches.filter(
        ~Q(winner=player),
        Q(player1=player) | Q(player2=player))

def undefeated(tournament):
    matches = tournament.matches
    players = tournament.participants.all()

    alist = []
    for player in players:
        if not _loser(matches, player).exists():
            alist.append(player)
    return alist

def underdog(tournament):
    # get all players that lost their first match
    # and also won atleast 2 matches afterwards
    matches = tournament.matches
    players = tournament.participants.all()

    alist = []
    for player in players:
        if _loser(matches.filter(round_num=1), player).exists():
            # then this player lost r1
            cnt = matches.filter(round_num__gt=1, winner=player).count()
            if cnt >= 2:
                alist.append(player)
    return alist

def woodenspoon(tournament):
    alist = []
    for player in tournament.participants.all():
        if not tournament.matches.filter(winner=player).exists():
            alist.append(player)
    return alist

def winstreak(tournament):
    alist = []
    playernames = tournament.participants.all()
    playername2score = {playername: tournament.matches.filter
    (winner=playername).count() for playername in playernames}
    sorted_players = sorted(playername2score, key=playername2score.get,
    reverse=True)
    for player in tournament.participants.all():
        if sorted_players[0] == player:
            if tournament.matches.filter(winner=player).count() == 0:
                pass
            tournamenthistory = get_player_history(player)
            tdict = {tournament.name: tournament.date_end for tournament in tournamenthistory}
            if len(tdict) == 1:
                break
            sorted_tdict = sorted(tdict, key=tdict.get)
            prev_tour = sorted_tdict[-2]
            prev_tour_obj = Tournament.objects.get(name=prev_tour)
            playernames2 = prev_tour_obj.participants.all()
            playername2score2 = {playername2: prev_tour_obj.matches.filter
            (winner=playername2).count() for playername2 in playernames2}
            sorted_players2 = sorted(playername2score2, key=playername2score2.get,
            reverse=True)
            if sorted_players2[0] == player:
                alist.append(player)
    return alist


medals2func = {
    "Undefeated": undefeated,
    "Underdog": underdog,
    "Winstreak": winstreak,
    "Wooden Spoon": woodenspoon,
}


def calc_tournament_medals(tournament: Tournament):
    """gets all the medals a given player has received in a given tournament.

    Args:
    tournament: str
        tournament str to get all medals in a particular tournament
        example:
        "Tournament 1"

    Returns:
        dictionary containing a list of player names associated with
        a medal string(the key) that has been achieved
        in a particular tournament.
        example:

        TODO: finish example
        {
            'woodenspoon': ['Heinrich', 'Josephine'],
            'underdog': [],
        }

    """
    return {
        medal_name: players_who_got_medal(tournament)
        for medal_name, players_who_got_medal in medals2func.items()
    }

def get_player_medals(player: Player):
    return Medal.objects.filter(player=player).order_by('tournament')

def get_tournament_medals(tournament: Tournament):
    return Medal.objects.filter(
        Q(tournament=tournament)
        & ~Q(player__name='Bye')
        & ~Q(player__name='Draw')
    )


def get_medals_description():
    descriptions = {
        "Undefeated": "Play through an entire tournament or event without a single loss, scoring first place by a landslide.",
        'Underdog': "Came back from a round 1 loss and managed to pick up multiple wins inspite of a bad start, might even have reached topcut and gotten a chance to redeem themselves.",
        'Winstreak': "Didn't just win one tournament, won two in a row! Big props for managing that.",
        'Wooden Spoon': "They had a bad day, didn't manage to pick up any wins. Hopefully they can look back and laugh at this one, yeah?",
    }
    return descriptions
