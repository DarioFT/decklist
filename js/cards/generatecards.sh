#!/bin/sh

# Clean up a bit
rm -f *.js *.zip

curl https://mtgjson.com/api/v5/AtomicCards.json.zip > AtomicCards.json.zip
unzip AtomicCards.json.zip

# Parse out the giant JSON and make a much smaller one
./parsecards.py

# Minify
terser decklist-cards.js --source-map "url='decklist-cards-min.js.map'" -o decklist-cards-min.js

# Clean up a bit
rm AtomicCards*
rm decklist-cards.js
