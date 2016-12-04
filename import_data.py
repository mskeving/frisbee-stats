import csv

from app import db
from app.models import Player, Event


def create_player(player_info):
    name = player_info['Name']
    team_name = player_info['Team']

    existing = Player.query.filter_by(name=name).first()
    if existing:
        print "Already found player {}. skipping.".format(name)
        return

    team = Team.query.filter_by(name=team_name).first()
    team_id = team.id if team else None

    print "Adding new player {}.".format(name)
    db.session.add(
        Player(
            name=name,
            gender=player_info['Gender'],
            position=player_info['Position'],
            od=player_info['OD'],
            team_id=team_id,
        )
    )


def update_roster():
    with open('data/classy_roster.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        reader.next()
        roster_data = [row for row in reader]

    for player_info_list in roster_data:
        create_player(player_info_list)

    db.session.commit()
    print "Finished updating roster."


def generate_play(event_info):
    action = event_info['Action']
    passer = event_info['Passer']
    receiver = event_info['Receiver']
    defender = event_info['Defender']

    if action == "Catch":
        play = "{} to {}".format(passer, receiver)
    elif action == "Drop":
        play = "Drop by {}".format(receiver)
    elif action == "D":
        play = "Block by {}".format(defender)
    elif action == "Goal":
        play = "Goal from {} to {}".format(passer, receiver)
    elif action == "Pull":
        play = "Pull by {}".format(defender)
    elif action == "PullOb":
        play = "OB pull by {}".format(defender)
    elif action == "Throwaway":
        play = "Throwaway by {}".format(passer)
    else:
        play = "Unknown play"

    return play


def create_event(event_info, name_to_id):
    title = "{tourny} > {opp} > {our_score}-{their_score} > {play}".format(
        tourny=event_info['Tournamemnt'],
        opp=event_info['Opponent'],
        our_score=event_info['Our Score - End of Point'],
        their_score=event_info['Their Score - End of Point'],
        play=generate_play(event_info)
    )

    # Note: Finding existing title is not perfect. You could have
    # same people throwing to each other in same point.
    existing = Event.query.filter_by(title=title).first()
    if existing:
        print "Already found event {}".format(title)
        return

    print "Adding event {}".format(title)
    db.session.add(
        Event(
            date=event_info['Date/Time'],
            title=title,
            tournament=event_info['Tournamemnt'],  # their typo.
            opponent=event_info['Opponent'],
            seconds_elapsed=int(event_info['Point Elapsed Seconds']),
            line=event_info['Line'],
            our_score=event_info['Our Score - End of Point'],
            their_score=event_info['Their Score - End of Point'],
            event_type=event_info['Event Type'],
            action=event_info['Action'],
            passer=name_to_id.get(event_info['Passer']),
            receiver=name_to_id.get(event_info['Receiver']),
            defender=name_to_id.get(event_info['Defender']),
            player_1=name_to_id.get(event_info['Player 0']),
            player_2=name_to_id.get(event_info['Player 1']),
            player_3=name_to_id.get(event_info['Player 2']),
            player_4=name_to_id.get(event_info['Player 3']),
            player_5=name_to_id.get(event_info['Player 4']),
            player_6=name_to_id.get(event_info['Player 5']),
            player_7=name_to_id.get(event_info['Player 6']),
        )
    )


def import_events(players_name_to_id):
    # hey, get this from the API instead of downloading a csv.
    # http://www.ultianalytics.com/rest/view/team/5699535384870912/gamesdata
    with open('data/classy_data_2k16.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        reader.next()
        event_data = [row for row in reader]

    for event_info_list in event_data:
        create_event(event_info_list, players_name_to_id)

    db.session.commit()


def get_names_to_ids():
    players = Player.query.all()

    players_name_to_id = {}
    for player in players:
        players_name_to_id[player.name] = int(player.id)

    return players_name_to_id


def main():
    update_roster()

    players_name_to_id = get_names_to_ids()

    import_events(players_name_to_id)


if __name__ == "__main__":
    main()
