from app import db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(56))
    gender = db.Column(db.String(25))
    position = db.Column(db.String(25))
    od = db.Column(db.String(25))


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
