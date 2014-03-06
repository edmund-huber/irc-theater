#!/usr/bin/env python

import inspect
import json
import re
import sys


# In order of appearance.
character_to_actor = {
    'LIBRARIAN': 1,
    'VENKMAN': 1,
    'SOPHOMORE': 1,
    'COED': 1,
    'STANTZ': 1,
    'SPENGLER': 1,
    'HEAD LIBRARIAN': 1,
    'THE GHOST': 1,
    'DEAN YAEGER': 1,
    'R/E WOMAN': 1,
    'LOUIS': 1,
    'DANA': 1,
    'FATHER': 1,
    'THE KIDS': 1,
    'MOTHER': 1,
    'JANINE': 1,
    'THE FAMILY': 1,
    'GHOSTBUSTERS': 1,
    'THE PRESENCE': 1,
    'BRIDE': 1,
    'GROOM': 1,
    'MANAGER': 1,
    'GUEST': 1,
    'WOMAN': 1,
    'HOTEL MANAGER': 1,
    'REPORTER #1': 1,
    'REPORTER #2': 1,
    'REPORTER #3': 1,
    'REPORTER #4': 1,
    'STREET PUNK': 1,
    'MINICAM REPORTER': 1,
    'ALL TOGETHER': 1,
    'ANNOUNCER': 1,
    'ROGER GRIMSBY': 1,
    'ROY BRADY': 1,
    'JOE FRANKLIN': 1,
    'LARRY KING': 1,
    'FEMALE CALLER': 1,
    'VIOLINIST': 1,
    'WINSTON': 1,
    'PECK': 1,
    'TALL WOMAN': 1,
    'WOMAN #2': 1,
    'DOORMAN': 1,
    'FIRST BUM': 1,
    'SECOND BUM': 1,
    'COACHMAN': 1,
    'THE COP': 1,
    'PARK RANGER': 1,
    'SERGEANT': 1,
    'CON-ED MAN': 1,
    'CAPTAIN': 1,
    'GUY IN SUIT': 1,
    'FIRE CAPTAIN': 1,
    'POLICE CAPTAIN': 1,
    'BUSINESSMAN': 1,
    'MUGGER': 1,
    'VINZ': 1,
    'MUGGER #2': 1,
    'POLICE OFFICIAL': 1,
    'REPORTERS': 1,
    'THE AIDE': 1,
    'MAYOR': 1,
    'FIRE COMMISSIONER': 1,
    'POLICE COMMISSIONER': 1,
    'ARCHBISHOP': 1,
    'MRS. BLUM': 1,
    'AIDE': 1,
    'VOICE IN CROWD (MAN)': 1,
    'VOICE IN CROWD (GIRL)': 1,
    'GOZER': 1,
    'COP': 1
}

for character in character_to_actor:
    if character_to_actor[character] == 1:
        character_to_actor[character] = re.sub(r'\W', '_', character.lower())
        print character_to_actor[character]

things = []
def emit(j):
    things.append(j)
    print >> sys.stderr, '!!!! %s' % j

lines = open('GHOSTBUSTERS').readlines()[::-1]

def get_line():
    if not lines:
        raise StopIteration()
    line = lines.pop().rstrip()
    print >> sys.stderr, '>>>> (L%i) %s' % (inspect.getouterframes(inspect.currentframe())[1][2], line)
    return line

def unget_line(line):
    lines.append(line)
    print >> sys.stderr, '** ungot line'

try:
    while True:
        line = get_line().rstrip()
        action_match = re.match(r'\s+(.+?)$', line)
        #                                LIBRARIAN
        #                        (puzzled)
        #                Hello?  Is anybody there?
        if action_match:
            m = action_match.group(1)
            while True:
                strip_match = re.match("(.*)( \(CONT'D\)| \(V.O.\)| \(O.S.\))$", m)
                if not strip_match:
                    break
                m = strip_match.group(1)
            characters = m.split(' & ')
            print >> sys.stderr, '** action match (characters=%s)' % characters
            try:
                while True:
                    print >> sys.stderr, 'parsing action'
                    line = get_line()
                    complete_movement_match = re.match(r'\s+\((.*?)\)', line)
                    beginning_movement_match = re.match(r'\s+\((.+)', line)
                    dialogue_match = re.match(r'\s+(.+)', line)
                    if complete_movement_match:
                        print >> sys.stderr, '** complete movement match'
                        for c in characters:
                            emit({'character': c, 'action': {'movement': complete_movement_match.group(1)}})
                    elif beginning_movement_match:
                        print >> sys.stderr, '** beginning movement match'
                        movement = beginning_movement_match.group(1)
                        while True:
                            line = get_line()
                            ending_movement_match = re.match(r'\s+(.+)\)$', line)
                            if ending_movement_match:
                                print >> sys.stderr, '** ending movement match'
                                movement += ' %s' % ending_movement_match.group(1)
                                for c in characters:
                                    emit({'character': c, 'action': {'movement': movement}})
                                break
                            else:
                                print >> sys.stderr, '** continuing movement'
                                movement += ' %s' % line.lstrip()

                    elif dialogue_match:
                        print >> sys.stderr, '** dialogue match'
                        dialogue = dialogue_match.group(1)
                        while True:
                            line = get_line()
                            dialogue_match = re.match(r'[^(].*', line.lstrip())
                            if dialogue_match:
                                dialogue += ' %s' % dialogue_match.group(0)
                            else:
                                unget_line(line)
                                for c in characters:
                                    emit({'character': c, 'action': {'dialogue': dialogue}})
                                break
                    else:
                        break
            except StopIteration:
                pass
        # EXT. NEW YORK PUBLIC LIBRARY -- DAY
        elif re.match(r'[A-Z\W]+$', line):
            print >> sys.stderr, '** topic match'
            emit({'topic': line})
        # The sun shines brightly on the classic facade of the main library at Fifth
        # Avenue and 42nd Street.  In the adjacent park area, pretty hustlers and
        # drug peddlers go about their business.
        else:
            narration = ''
            while re.match(r'\w', line):
                print >> sys.stderr, '** narration match'
                if narration:
                    narration += ' '
                narration += line
                line = get_line()
            if narration:
                emit({'narration': narration})
except StopIteration:
    pass


# IRC magic!

import irc.client
import ssl
import time

def on_connect(connection, event):
    connection.join('#ghostbusters')
    # Say things!
    for t in things:
        if 'action' in t and 'dialogue' in t['action']:
            connection.privmsg('#ghostbusters', '%s: %s' % (t['character'], t['action']['dialogue']))
        elif 'action' in t and 'movement' in t['action']:
            connection.action('#ghostbusters', '%s: %s' % (t['character'], t['action']['movement']))
        elif 'topic' in t:
            connection.topic('#ghostbusters', t['topic'])
        elif 'narration' in t:
            connection.privmsg('#ghostbusters', t['narration'])
        time.sleep(5)


ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
client = irc.client.IRC()
connection = client.server().connect('irc.xelpers.org', 6697, 'venkman', password='smellyoulater', connect_factory=ssl_factory)
connection.add_global_handler('welcome', on_connect)
client.process_forever()
