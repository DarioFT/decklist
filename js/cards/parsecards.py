#!/usr/bin/env python3

import json
import unicodedata

# Just FYI!
# b (banned) = [sml] (standard, modern, legacy)
# c (color) = White = A, Blue = B, Black = C, Red = D, Green = E, Gold = F, Artifact = G , Split = S, Unknown = X, Land = Z
# m (CMC) = N  (Split = 98, Land = 99)
# n (actual name) = 'true name nemesis' to 'True Name Nemesis'
# t (type) = 1 = land, 2 = creature, 3 = sorcery, 4 = instant, 5 = other

FORMATS = ('standard', 'modern', 'legacy')

def getLegalities(face):
    # Let's figure out legalities
    banned = 'sml'

    for format in FORMATS:
        if face.get('legalities', {}).get(format) == 'Legal':
            banned = banned.replace(format[0].lower(), '')

    return(banned)

def remove_accents(input_str):
    """Removes accents from a given string."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def getColorCode(colors):
    color_map = {'W': 'A', 'U': 'B', 'B': 'C', 'R': 'D', 'G': 'E'}
    if len(colors) == 0:
        return 'X'  # X for unknown or no color
    if len(colors) > 1:
        return 'F'  # Gold for multiple colors
    return color_map.get(colors[0], 'X')

# Open the JSON file
jsonfh = open("AtomicCards.json", "r")

# Load all the cards into a giant dictionary
cards = json.load(jsonfh)

# Gotta store these cards in a dictionary
ocards = {}

# Okay, we need the colors but in a much shorter format
for card in cards["data"].values():
    # We only care about the first face
    if 'side' not in card[0] or len(card) == 1:
        face = card[0]
    else:
        face = card[0] if card[0]['side'] == 'a' else card[1]

    is_flip = face["layout"] in ("transform", "modal_dfc", "adventure")

    # We're going to store them in lowercase
    ocard = face["faceName" if is_flip else "name"].lower()

    # Remove accents from the card name
    ocard = remove_accents(ocard)

    # Python's Unicode support sucks, as does everybodies.  Manually
    # replace the Ae to lower case
    ocard = ocard.replace(u'\xc6', u'\xe6')

    # Skip tokens
    if face['layout'] == 'token':
        continue

    # Create an entry in the output dictionary
    ocards[ocard] = {}

    if 'Land' in face['types']:
        ocards[ocard]['c'] = 'Z'
    elif 'Artifact' in face['types'] and 'colors' not in face:
        ocards[ocard]['c'] = 'G'
    elif face.get("layout") == "split":
        ocards[ocard]['c'] = getColorCode(face.get("colorIdentity", []))
    else:
        ocards[ocard]['c'] = getColorCode(face.get("colors", []))

    if   'Land'     in face['types']:  ocards[ocard]['t'] = '1'
    elif 'Creature' in face['types']:  ocards[ocard]['t'] = '2'
    elif 'Sorcery'  in face['types']:  ocards[ocard]['t'] = '3'
    elif 'Instant'  in face['types']:  ocards[ocard]['t'] = '4'
    else:                              ocards[ocard]['t'] = '5'

    # Now try to deal with CMC
    if 'convertedManaCost' not in face: ocards[ocard]['m'] = 99
    else: ocards[ocard]['m'] = face['convertedManaCost']

    # Add it into the file if the banned list isn't empty
    legality = getLegalities(face)
    if legality != "": ocards[ocard]['b'] = legality

    # And put the true name in there as well
    ocards[ocard]['n'] = face["faceName" if is_flip else "name"]

# Print out the full list of cards
ojsonfh = open("decklist-cards.js", "w")
ojsonfh.write('cards=')
json.dump(ocards, ojsonfh)
ojsonfh.close()
