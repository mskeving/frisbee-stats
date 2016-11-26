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

    @classmethod
    @app.cache.memoize(timeout=30)
    def female_player_ids(cls):
        players = cls.query.filter_by(gender="F").all()
        return [player.id for player in players]

    @classmethod
    @app.cache.memoize(timeout=30)
    def male_player_ids(cls):
        players = cls.query.filter_by(gender="M").all()
        return [player.id for player in players]


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    # unique string to identify event
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

    @classmethod
    def receives_by_gender(cls):
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

        returns:
            - Total number of receives
            - Percentage Female
            - Percentage Male
        """
        total = len(cls.query.filter(Event.receiver.isnot(None)).all())

        male_ids = Player.male_player_ids()
        male = len(cls.query.filter(Event.receiver.in_(male_ids)).all())

        female_ids = Player.female_player_ids()
        female = len(cls.query.filter(Event.receiver.in_(female_ids)).all())

        return {
            'total': total,
            'female': "{}%".format(percentage(female, total)),
            'male': "{}%".format(percentage(male, total)),
        }
