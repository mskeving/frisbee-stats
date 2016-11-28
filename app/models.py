from collections import defaultdict
from sqlalchemy import and_

from app import app, db
from app.lib.helpers import percentage


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(56))
    gender = db.Column(db.String(25))
    position = db.Column(db.String(25))
    od = db.Column(db.String(25))

    def __repr__(self):
        # This will be included in cache_key to make sure
        # keys are unique per player.
        return "%s(%s)" % (self.__class__.__name__, self.id)

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

        return "{}%".format(percentage(count, len(events)))

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
    passer = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
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
    def points(cls):
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
    def lines_split(cls):
        """
        Calculate how many lines we have as 4-3, 3-4, or other
        """
        events = cls.full_line_events()
        male_players = Player.male_ids()

        four_three_events = []
        three_four_events = []
        other = []

        for event in events:
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
            '4-3': four_three_events,
            '3-4': three_four_events,
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
    def offense_line_split(cls):
        """
        On offense we get to choose 3-4 or 4-3. Calculate what
        we're choosing.
        """
        lines_split = cls.lines_split()

        return {
            '4-3': [e for e in lines_split['4-3'] if e.line == "O"],
            '3-4': [e for e in lines_split['3-4'] if e.line == "O"],
            'other': [e for e in lines_split['other'] if e.line == "O"],
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
    def receives_by_gender(cls, breakdown=None):
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
            - breakdown: '3-4' or '4-3' for line composition

        returns:
            - Total number of receives
            - Percentage Female
            - Percentage Male
        """
        if breakdown is None:
            receive_events = cls.query.filter(Event.receiver.isnot(None)).all()
        elif breakdown in ['3-4', '4-3']:
            events_by_line = cls.lines_split()
            all_events = events_by_line[breakdown]
            receive_events = [e for e in all_events if e.receiver is not None]
        else:
            return "breakdown {} unknown".format(breakdown)

        male_ids = Player.male_ids()
        male = [e for e in receive_events if e.receiver in male_ids]

        female_ids = Player.female_ids()
        female = [e for e in receive_events if e.receiver in female_ids]

        return {
            'total': len(receive_events),
            'female': "{}%".format(percentage(len(female), len(receive_events))),
            'male': "{}%".format(percentage(len(male), len(receive_events))),
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
