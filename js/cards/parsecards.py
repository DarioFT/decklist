#!/usr/bin/env python3

import json

# Just FYI!
# b (banned) = [sml] (standard, modern, legacy)
# c (color) = White = A, Blue = B, Black = C, Red = D, Green = E, Gold = F, Artifact = G , Split = S, Unknown = X, Land = Z
# m (CMC) = N  (Split = 98, Land = 99)
# n (actual name) = 'true name nemesis' to 'True Name Nemesis'
# t (type) = 1 = land, 2 = creature, 3 = instant or sorcery 4 = other

FORMATS = ('standard', 'modern', 'legacy')

def getLegalities(face):
    # Let's figure out legalities
    banned = 'sml'

    for format in FORMATS:
        if face.get('legalities', {}).get(format) == 'Legal':
            banned = banned.replace(format[0].lower(), '')

    return(banned)

def processAdventureCard(card):
    # Adventure cards typically have two sides; creature and Adventure
    creature_side, adventure_side = card

    # Use the creature side's name as the primary identifier
    ocard = creature_side["name"].lower()
    ocard = ocard.replace(u'\xc6', u'\xe6')  # Handle special characters

    # Skip further processing if layout is token
    if creature_side['layout'] == 'token':
        return

    # Initialize dictionary for this card
    ocards[ocard] = {}

    # Process color identity
    if 'colorIdentity' in creature_side:
        ocards[ocard]['colorIdentity'] = ''.join(creature_side['colorIdentity'])

    # Process colors
    if 'colors' in creature_side:
        colors = creature_side['colors']
        if len(colors) > 1:
            ocards[ocard]['c'] = 'F'  # Gold for multicolored
        else:
            color_map = {'W': 'A', 'U': 'B', 'B': 'C', 'R': 'D', 'G': 'E'}
            ocards[ocard]['c'] = color_map.get(colors[0], 'X')  # Default to 'X' if color not found

    # Process type
    if 'types' in creature_side:
        type_map = {'Land': '1', 'Creature': '2', 'Sorcery': '3', 'Instant': '3'}
        ocards[ocard]['t'] = type_map.get(creature_side['types'][0], '4')  # Default to '4' for other types

    # Process mana cost and converted mana cost (CMC)
    ocards[ocard]['manaCost'] = creature_side.get('manaCost', 'Unknown')
    ocards[ocard]['cmc'] = creature_side.get('convertedManaCost', 99)

    # Add legalities
    legality = getLegalities(creature_side)
    if legality != "":
        ocards[ocard]['b'] = legality

    # Add true name
    ocards[ocard]['n'] = creature_side["name"]

    # Indicate that this card has an Adventure aspect
    ocards[ocard]['hasAdventure'] = True

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

    # Check if the card is an Adventure card
    if 'layout' in face and face['layout'] == 'adventure':
        processAdventureCard(card)
        continue

    is_flip = face["layout"] in ("transform", "modal_dfc")

    # We're going to store them in lowercase
    ocard = face["faceName" if is_flip else "name"].lower()

    # Python's Unicode support sucks, as does everybodies.  Manually
    # replace the Ae to lower case
    ocard = ocard.replace(u'\xc6', u'\xe6')

    # Skip tokens
    if face['layout'] == 'token':
        continue

    # Create an entry in the output dictionary
    ocards[ocard] = {}

    # Lands and (noncolored) artifacts are special
    if 'Land' in face['types']:
        ocards[ocard]['c'] = 'Z' # Sort lands last
    elif (('Artifact' in face['types']) and ('colors' not in face)):
        ocards[ocard]['c'] = 'G'

    # Make the colors shorter
    if ('colors' not in face): pass
    elif len(face['colors']) > 1:  ocards[ocard]['c'] = 'F'    # gold
    elif face['colors'] == ['W']:  ocards[ocard]['c'] = 'A'
    elif face['colors'] == ['U']:  ocards[ocard]['c'] = 'B'
    elif face['colors'] == ['B']:  ocards[ocard]['c'] = 'C'
    elif face['colors'] == ['R']:  ocards[ocard]['c'] = 'D'
    elif face['colors'] == ['G']:  ocards[ocard]['c'] = 'E'

    if   'Land'     in face['types']:  ocards[ocard]['t'] = '1'
    elif 'Creature' in face['types']:  ocards[ocard]['t'] = '2'
    elif 'Sorcery'  in face['types']:  ocards[ocard]['t'] = '3'
    elif 'Instant'  in face['types']:  ocards[ocard]['t'] = '3'
    else:                              ocards[ocard]['t'] = '4'

    # Now try to deal with CMC
    if 'convertedManaCost' not in face: ocards[ocard]['m'] = 99
    else: ocards[ocard]['m'] = face['convertedManaCost']

    # Add it into the file if the banned list isn't empty
    legality = getLegalities(face)
    if legality != "": ocards[ocard]['b'] = legality

    # And put the true name in there as well
    ocards[ocard]['n'] = face["faceName" if is_flip else "name"]

    # Now to handle split cards (ugh)
    if ' // ' in ocard:
        ocards[ocard]['c'] = 'S'
        ocards[ocard]['m'] = 98

    # if 'names' in face:
    #     name = " // ".join(face['names'])
    #     ocard = name.lower().replace(u'\xc6', u'\xe6')   # Just like a real card
    #
    #     ocards[ocard] = {}
    #     ocards[ocard]['c'] = 'S'
    #     ocards[ocard]['m'] = 98
    #     ocards[ocard]['n'] = name
    #
    #     legality = getLegalities(face)
    #     if legality != "": ocards[ocard]['b'] = legality


# Print out the full list of cards
ojsonfh = open("decklist-cards.js", "w")
ojsonfh.write('cards=')
json.dump(ocards, ojsonfh)
ojsonfh.close()
