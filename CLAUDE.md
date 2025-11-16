# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

decklist.xyz is a static website that generates Magic: The Gathering tournament registration sheets and decklists. It's a fork of the original [decklist.org](https://github.com/april/decklist) project by April King, enhanced with additional features and improvements.

The application runs entirely client-side using vanilla JavaScript, jQuery, and jsPDF. No build process is required for the main application.

## Architecture

### Core JavaScript Modules

The application is split into three main JavaScript modules in `js/decklist/`:

1. **decklist.js** - Core decklist parsing and manipulation
   - `Decklist.parse(deckmain, deckside)` - Parses various deck formats (MTGO, MWS, MTG Goldfish, Tappedout, etc.) into structured card objects
   - `Decklist.sort(deck, sortorder)` - Sorts decks by alphabetical, CMC, color, numeric, or type
   - `Decklist.section(deck, sectionType)` - Adds visual spacers between card groups
   - `Decklist.filter(deck, field, values, mode)` - Filters cards by properties
   - `Decklist.count(deck)` - Counts total cards in a deck
   - Returns objects with structure: `{main: [], side: [], unrecognized: [], unparseable: []}`
   - Each card object has properties: `n` (name), `c` (color), `t` (type), `m` (CMC), `q` (quantity), `b` (banned status)

2. **main.js** - Main application logic
   - Event handling for form inputs
   - PDF generation using jsPDF
   - URL parameter parsing for direct linking
   - History state management for permalinks
   - Input validation with debounced updates (400ms for validation, 1500ms for PDF generation)

3. **dci.js** - DCI number validation utilities
   - `DCI.isValid(number)` - Validates DCI numbers using checksum algorithm
   - `DCI.getTenDigit(number)` - Converts to 10-digit format
   - Uses prime number checksums for validation

### Card Data System

Card data is stored in `js/cards/decklist-cards-min.js` as a minified JavaScript object. The card database structure:
- Key: lowercase card name (with accents removed)
- Value: object with properties:
  - `c`: color code (A=White, B=Blue, C=Black, D=Red, E=Green, F=Gold, G=Artifact, Z=Land)
  - `t`: type code (1=Land, 2=Creature, 3=Sorcery, 4=Instant, 5=Other)
  - `m`: converted mana cost (99 for lands)
  - `b`: banned status in formats (combination of s/m/l for Standard/Modern/Legacy)
  - `n`: actual card name with proper capitalization

### URL Parameters for Direct Linking

The application supports extensive URL parameter support for pre-filling forms:
- Personal: `firstname`, `lastname`, `dcinumber`
- Event: `event`, `eventdate`, `eventlocation`
- Deck: `deckname`, `deckdesigner`, `deckmain`, `deckside`, `decksort`
- Display: `decksheet` (wotc/scg), `logo`, `disableediting`

Use `%0A` for newlines in deck data, `%20` for spaces.

## Card Data Regeneration

The card database is automatically updated daily via GitHub Actions workflow (`.github/workflows/generate-cards.yml`).

### Manual Card Data Update

To manually regenerate the card database:

```bash
cd js/cards
./generatecards.sh
```

This script:
1. Downloads latest `AtomicCards.json.zip` from mtgjson.com
2. Runs `parsecards.py` to extract and compress card data
3. Minifies output using terser
4. Cleans up temporary files

**Requirements:**
- Python 3
- terser (install globally: `npm i terser -g`)
- curl and unzip

The workflow auto-commits changes with message "💬 Update card list".

## Development Workflow

### Testing Changes

Since this is a static site:
1. Open `index.html` in a browser
2. Make changes to JavaScript/CSS files
3. Refresh the browser (hard refresh: Ctrl+F5 / Cmd+Shift+R)

For iframe preview testing, the app uses `srcdoc` attribute to render the decklist preview inline.

### Common Modifications

**Adding a new deck format parser:**
- Edit `decklist.js`, add regex to `cardRE.main` or `cardRE.side` arrays
- Test with various inputs to ensure proper parsing

**Adding a new sort order:**
- Add sort function in `Decklist.sort()`
- Add corresponding UI radio button in `index.html`
- Add case to sort switch statement

**Adding a new logo:**
- Place logo as base64-encoded JavaScript in `images/logos/`
- Add logo name to `logos` array in `main.js`
- Logo JavaScript files should define the logo as a global variable

## Deployment

The site is hosted on GitHub Pages from the `gh-pages` branch. Any commits to this branch automatically deploy.

## Important Notes

- All card name matching is case-insensitive with accent normalization
- The app HTML-encodes all user input to prevent XSS attacks
- PDF generation happens client-side using jsPDF library
- The iframe preview regenerates with debounced updates to avoid performance issues
- DCI number validation supports both 8-digit and 10-digit formats
