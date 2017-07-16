from __future__ import print_function

import requests
from bs4 import BeautifulSoup
import datetime
import os

today = datetime.date.today()
base_url = 'http://gd2.mlb.com/components/game/mlb/year_{}/month_{:02d}/day_{:02d}'.format(today.year, today.month,
                                                                                           today.day)
player_name = 'Tzu-Wei Lin'


def get_game_link():
    r = requests.get(base_url)

    soup = BeautifulSoup(r.text)

    links = [a['href'] for a in soup.find_all('a')]
    links = [l for l in links if 'bosmlb' in l]

    if not links:
        return None

    return links[0]


def get_player_events(game_link, player_id=624407):
    r = requests.get(os.path.join(base_url, game_link, 'batters/{}.xml'.format(player_id)))
    if not r.ok:
        return None

    soup = BeautifulSoup(r.text)

    at_bats = soup.find('atbats')

    if not at_bats:
        return None

    return [ab['event'] for ab in at_bats.find_all('ab')]


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_alexa_output():
    game_link = get_game_link()
    if not game_link:
        return 'There is no Red Sox game today.'

    events = get_player_events(game_link)
    if events is None:
        return '{} has not played yet.'.format(player_name)
    else:
        return '{} has {} today.'.format(player_name, ', '.join(events))


def lambda_handler(event, context):
    output = get_alexa_output()

    return build_response({}, build_speechlet_response(
        "today", output, None, True))
