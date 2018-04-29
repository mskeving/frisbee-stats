from collections import defaultdict
from sqlalchemy import and_

from app import app, db
from app.lib.helpers import percentage


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(56))
    region = db.Column(db.String(56))
    players = db.relationship('Player', backref='team')


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    name = db.Column(db.String(56))
    gender = db.Column(db.String(25))
    position = db.Column(db.String(25))
    od = db.Column(db.String(25))
    year = db.Column(db.String(25))

    def __repr__(self):
        # This will be included in cache_key to make sure
        # keys are unique per player.
        return "%s(%s)" % (self.__class__.__name__, self.id)

    def to_api_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'position': self.position,
            'od': self.od,
            'team_name': self.team.name,
        }

    def female_passing_percentage(self):
        """ Out of total passes this player does, what percentage
        of those are going to a female player?

        Take into account lineup? For example, if there's only 1
        female cutter out there, should that handler be considered
        more female friendly if they throw it to them?
        """
        female_ids = self.female_ids()

        events = Event.query.filter_by(passer=self.id).all()
        count = 0
        for event in events:
            if event.receiver in female_ids:
                count += 1

        return "{}: {}% of {} throws".format(self.name, percentage(count, len(events)), len(events))

    @classmethod
    @app.cache.memoize(timeout=30)
    def female_ids(cls):
        players = cls.query.filter_by(gender="F").all()
        return [player.id for player in players]

    @classmethod
    @app.cache.memoize(timeout=30)
    def male_ids(cls):
        players = cls.query.filter_by(gender="M").all()
        return [player.id for player in players]

    @classmethod
    @app.cache.memoize(timeout=30)
    def handler_ids(cls):
        players = cls.query.filter_by(position="Handler").all()
        return [player.id for player in players]

    @classmethod
    @app.cache.memoize(timeout=30)
    def cutter_ids(cls):
        players = cls.query.filter_by(position="Cutter").all()
        return [player.id for player in players]


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    # unique string to identify event. Same as plasticdisco.
    # "{tourny} > {opp} > {our_score}-{their_score} > {play}"
    title = db.Column(db.String(255))

    date = db.Column(db.String(55))
    tournament = db.Column(db.String(55))
    opponent = db.Column(db.String(55))
    seconds_elapsed = db.Column(db.Integer)
    line = db.Column(db.String(25))
    our_score = db.Column(db.Integer)
    their_score = db.Column(db.Integer)
    event_type = db.Column(db.String(25))
    action = db.Column(db.String(25))
    passer = db.Column(db.Integer)  # user id
    receiver = db.Column(db.Integer)  # user id
    defender = db.Column(db.Integer)

    # players on the line
    player_1 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_2 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_3 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_4 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_5 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_6 = db.Column(db.Integer, db.ForeignKey('players.id'))
    player_7 = db.Column(db.Integer, db.ForeignKey('players.id'))

    def point_title(self):
        """
        Helpful for sorting events into same points. self.title
        is too specific, because it takes "play" into account.

        Could probably add this to the import script and have it
        as a property instead.
        """
        return "{date}{opponent}{our_score}{their_score}".format(
            date=self.date,
            opponent=self.opponent.encode('utf-8'),
            our_score=self.our_score,
            their_score=self.their_score
        )

    @classmethod
    def off_gender_passes(cls):
        """
        Count how many times a pass happens between same gendered players

        returns
            - counts (ints) of same vs off gendered passes
        """
        off_gender_passes = 0
        same_gender_passes = 0

        male_ids = Player.male_ids()
        female_ids = Player.female_ids()
        events = cls.query.all()

        for event in events:
            if event.passer == None or event.receiver == None:
                continue
            same_gender = (
                event.passer in male_ids and event.receiver in male_ids or
                event.passer in female_ids and event.receiver in female_ids
            )
            if same_gender:
                same_gender_passes += 1
            else:
                off_gender_passes += 1

        return {
            'off_gender': off_gender_passes,
            'same_gender': same_gender_passes
        }

    @classmethod
    def points_played_by_players(cls):
        num_points_by_player = {}
        players = Player.query.all()
        for player in players:
            num_points_by_player[player.name] = cls.points_played_by_player(player.id)

        return num_points_by_player

    @classmethod
    def points_played_by_player(cls, user_id):
        points_played = 0
        points_to_events = cls.points_to_events()

        for point, events in points_to_events.iteritems():
            # we only care about the first event because that'll have
            # the lineup for the entire point.
            event = events[0]
            if user_id in [
                event.player_1,
                event.player_2,
                event.player_3,
                event.player_4,
                event.player_5,
                event.player_6,
                event.player_7,
            ]:
                points_played += 1

        return points_played

    @classmethod
    @app.cache.memoize(timeout=30)
    def points_to_events(cls):
        """
        Distinguish points by unique title and put them in a dict.
        Keys are points, values are list of events for that point.
        """
        points_to_events = defaultdict(list)
        all_events = cls.query.all()
        for event in all_events:
            points_to_events[event.point_title()].append(event)

        return points_to_events

    @classmethod
    def goals_by_gender(cls):
        female_ids = Player.female_ids()
        male_ids = Player.male_ids()
        male_count = 0
        female_count = 0

        # Goals for opponent will have None receiver
        goals = cls.query.filter(
            cls.action == "Goal",
            cls.receiver.isnot(None)
        ).all()

        for goal in goals:
            if goal.receiver in female_ids:
                female_count += 1
            elif goal.receiver in male_ids:
                male_count += 1

        return {
            'female': "{}%".format(percentage(female_count, len(goals))),
            'male': "{}%".format(percentage(male_count, len(goals))),
        }

    @classmethod
    def full_line_events(cls):
        """
        return all events that we have a full line of players for.
        many lines don't have all 7 players listed. drat.
        """
        return cls.query.filter(
            and_(
                Event.player_1.isnot(None),
                Event.player_2.isnot(None),
                Event.player_3.isnot(None),
                Event.player_4.isnot(None),
                Event.player_5.isnot(None),
                Event.player_6.isnot(None),
                Event.player_7.isnot(None)
            )).all()

    @classmethod
    def num_points_by_line_split(cls):
        """
        Calculate how many lines we have as 4-3, 3-4,
        or other per POINT, not event
        """
        points_to_events = cls.points_to_events()
        male_players = Player.male_ids()

        four_three_points = []
        three_four_points = []
        other = []

        for point, events in points_to_events.iteritems():
            event = events[0]
            male_count = 0
            players = [
                event.player_1,
                event.player_2,
                event.player_3,
                event.player_4,
                event.player_5,
                event.player_6,
                event.player_7
            ]
            for player in players:
                if player in male_players:
                    male_count += 1

            if male_count == 4:
                four_three_events.append(event)
            elif male_count == 3:
                three_four_events.append(event)
            else:
                other.append(event)

        return {
            '4-3': four_three_points,
            '3-4': three_four_points,
            'other': other,
        }

    @classmethod
    def handler_gender_split(cls):
        """
        This takes all events and counts how many "handlers" we have on the
        line. It's not great because lots of people go back and forth between
        handler and cutter.

        It's also not great because it goes by events. Probably we should be
        going by points.
        """
        handler_ids = Player.handler_ids()
        female_handlers = [f for f in Player.female_ids() if f in handler_ids]
        male_handlers = [f for f in Player.male_ids() if f in handler_ids]

        all_events = cls.query.all()
        ret = {}

        for event in all_events:
            male_count = 0
            female_count = 0
            players = [
                event.player_1,
                event.player_2,
                event.player_3,
                event.player_4,
                event.player_5,
                event.player_6,
                event.player_7
            ]
            for player in players:
                if player in male_handlers:
                    male_count += 1
                elif player in female_handlers:
                    female_count += 1
            breakdown = "{}-{}".format(male_count, female_count)
            ret['total'] = ret.get('total', 0) + 1
            ret[breakdown] = ret.get(breakdown, 0) + 1

        return ret

    @classmethod
    def line_split_count(cls, line="O"):
        """
        On offense we get to choose 3-4 or 4-3. Calculate what
        lines are chosen based on offense or defense.
        """
        if line not in ["O", "D"]:
            return "line has to be 'O' or 'D'"

        num_points_by_line_split = cls.num_points_by_line_split()

        return {
            '4-3': len([e for e in num_points_by_line_split['4-3'] if e.line == line]),
            '3-4': len([e for e in num_points_by_line_split['3-4'] if e.line == line]),
            'other': len([e for e in num_points_by_line_split['other'] if e.line == line]),
        }

    @classmethod
    def dees_by_gender(cls):
        female_ids = Player.female_ids()
        male_ids = Player.male_ids()
        dee_events = cls.query.filter(cls.defender.isnot(None)).all()

        male_count = 0
        female_count = 0

        for d in dee_events:
            if d.defender in female_ids:
                female_count += 1
            elif d.defender in male_ids:
                male_count += 1

        return {
            'female': "{}%".format(percentage(female_count, len(dee_events))),
            'male': "{}%".format(percentage(male_count, len(dee_events))),
            'total': len(dee_events)
        }

    @classmethod
    def receives_by_gender(cls, receive_events=None, breakdown=None):
        """
        For the sake of this analysis, we're going to include all
        actions where there is a receiver. This includes:
        Catch, Goal, or Drop.

        This seems more accurate than touches, because it means
        a play was intended for someone. Touches, defined by ultianalytics,
        would include Callahans and not drops.

        Pick up after pull is not included here, but can be
        calculated by the passer of first play of O point.
        Need to calculate manually.

        args:
            - events: list. can pass in your own events to analyze
                otherwise, will search entire set of events.
            - breakdown: '3-4' or '4-3' for line composition

        returns:
            - Total number of receives
            - Percentage Female
            - Percentage Male
        """
        if receive_events is None:
            if breakdown is None:
                receive_events = (
                    cls.query.filter(Event.receiver.isnot(None)).all()
                )
            elif breakdown in ['3-4', '4-3']:
                events_by_line = cls.num_points_by_line_split()
                all_events = events_by_line[breakdown]
                receive_events = [
                    e for e in all_events if e.receiver is not None
                ]
            else:
                return "breakdown {} unknown".format(breakdown)

        male_ids = Player.male_ids()
        male = [e for e in receive_events if e.receiver in male_ids]

        female_ids = Player.female_ids()
        fem = [e for e in receive_events if e.receiver in female_ids]

        return {
            'total': len(receive_events),
            'female': "{}%".format(percentage(len(fem), len(receive_events))),
            'male': "{}%".format(percentage(len(male), len(receive_events))),
        }

    @classmethod
    def gender_contribution_to_score(cls):
        """
        Find out percentage of touches on winning vs losing points. For
        example, on winning points, are we using our women more? Or are
        we losing those points?

        Returns: {
            'winning': {'male': 50%, 'female': 50%, 'total': 250}
            'losing': {'male': 50%, 'female': 50%, 'total': 250}
        }
        """
        winning_events = []
        losing_events = []

        for point, events in cls.points_to_events().iteritems():
            for event in events:
                if event.action == "Goal":
                    if event.receiver is None:
                        losing_events.extend(
                            [e for e in events if e.receiver is not None]
                        )
                    else:
                        winning_events.extend(
                            [e for e in events if e.receiver is not None]
                        )

        return {
            'winning': cls.receives_by_gender(receive_events=winning_events),
            'losing': cls.receives_by_gender(receive_events=losing_events)
        }

    @classmethod
    def receives_for_position(cls, position="handlers"):
        """
        Returns breakdown of receives by gender for position - handler, cutter
        """
        if position == "handlers":
            position_ids = Player.handler_ids()
        elif position == "cutters":
            position_ids = Player.cutter_ids()
        else:
            return "Position {} unknown".format(position)

        events = cls.query.filter(Event.receiver.isnot(None)).all()
        position_receives = [e for e in events if e.receiver in position_ids]

        female_players = Player.female_ids()
        female_position = [p for p in female_players if p in position_ids]
        female_receives = [e for e in events if e.receiver in female_position]

        male_players = Player.male_ids()
        male_position = [p for p in male_players if p in position_ids]
        male_receives = [e for e in events if e.receiver in male_position]

        return {
            'position': position,
            'female': "{}%".format(
                percentage(len(female_receives), len(position_receives))
            ),
            'male': "{}%".format(
                percentage(len(male_receives), len(position_receives))
            )
        }

    @classmethod
    def conversion_rate(cls):
        """
        Take each point, figure out what line we start off on, and then count
        how many times it switches.

        If O, count number of drops, throwaways in one point to get number of posessions.

        all posessions that end in score/all possessions
        """
        points_to_events = cls.points_to_events()

        line_to_possessions = {
            'O': None,
            'D': None,
        }
        line_to_goals = {
            'O': None,
            'D': None,
        }

        for point, events in points_to_events:
            posessions = 0
            goals = 0
            line = events[0].line # determine if this is an O or D line
            line_to_points[line] = line_to_points.get(line, 0) + 1

            for event in events:
                if event.line == 'O' and event.action in ['Drop', 'Throwaway']:
                    posessions += 1
                if event.line == 'O' and event.action in ['Goal']:
                    goals += 1

            line_to_possessions[line] = line_to_possessions.get(line, 0) + posessions

        return {
            'O': percentage(line_to_points['O']/line_to_possessions['O']),
            'D': percentage(line_to_points['D']/line_to_possessions['D'])
        }

