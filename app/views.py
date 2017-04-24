import json

from flask import render_template

from app import app
from app.models import Player


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # react-router is used on the client to take care of routing.
    # This is a catch-all url to say - whatever url we put in,
    # render base.jade with app js and the client takes care of the rest.
    return render_template('base.html')


@app.route('/api/players', methods=['POST'])
def team():
    players = Player.query.all()
    resp = [p.to_api_dict() for p in players]

    return json.dumps(resp)
