# StenoMD - Romanian Parliament Knowledge Brain

**Status:** OPERATIONAL with REAL DATA from cdep.ro

## Quick Start

```bash
# Open Obsidian
/opt/Obsidian/obsidian /home/adrian/Desktop/NEDAILAB/StenoMD/vault

# Run daily update
cd /home/adrian/Desktop/NEDAILAB/StenoMD
python3 scripts/run_daily.py
```

## Project Structure

```
StenoMD/
├── data/                    # Raw stenogram HTML files
├── knowledge_graph/        # entities.json
├── vault/                 # Obsidian vault
│   ├── politicians/       # Real MP notes
│   ├── sessions/        # Session notes
│   └── laws/           # Law notes
└── scripts/             # Automation scripts
```

## Current Real Data

- **11 MPs**: Vasile Citea, Alexandra Hu, Boris Volosatii, etc.
- **6 Sessions**: Nov 2024 - Feb 2025
- **1 Law**: 448/2006

## How Scraper Works

1. Calendar page → session dates
2. Iterate session IDs → find content
3. Use prn=1 for full printable version
4. Extract MPs: Domnul/Doamna + names
5. Extract laws: Legea + numbers
6. Save HTML → update entities → sync vault

## Sample Debate

> Bogdan-Alexandru Bola: "Forta Dreptei si Ludovic Orban sunt singurii aliati ai mediului de afaceri romanesc!"

> Boris Volosatii: "Republica Moldova trebuie sa mearga inainte!"

## License

CC BY 4.0 | Data from cdep.ro