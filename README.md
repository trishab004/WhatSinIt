# WhatSinIt — Know what you eat

Scan a food label or paste an ingredients list and instantly see:
- A jar visualization showing ingredient proportions
- Spoon-count translation ("2 tsp of sugar")
- Verdict cards for 7 consumer profiles
- Plain English summary

## Setup (5 minutes)

### 1. Get a free Gemini API key
- Go to https://aistudio.google.com/app/apikey
- Sign in with Google → Create API key → Copy it
- Free tier: 15 requests/min, 1500/day — more than enough

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
# Mac/Linux
export GEMINI_API_KEY="your-key-here"

# Windows
set GEMINI_API_KEY=your-key-here
```

### 4. Run
```bash
python app.py
```
Open http://localhost:5000

## Deploy to Render (free)
1. Push to GitHub
2. New Web Service on Render → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variable: GEMINI_API_KEY

## Project structure
```
whatsinit/
  app.py              # Flask backend — all logic here
  requirements.txt
  data/
    ingredients.json  # Ingredient database — add more here
  templates/
    index.html        # Frontend — HTML + plain JS, no frameworks
  static/             # For any images/icons you add later
```

## How to add more ingredients
Open `data/ingredients.json` and add a new entry following the same pattern.
Each ingredient has: name, aliases, safety level, color, spoon label, and
profile verdicts for all 7 consumer groups.

## Interview talking points
- "I chose rule-based over ML because safety classification is a fact, not a prediction"
- "Gemini free tier handles image OCR — Tesseract was the fallback but vision API is more accurate"
- "The percentage estimation uses descending weight order (FSSAI/FDA regulation) — not made up"
- "The spoon translation is a UX decision: divide gram weight by 5g per teaspoon"
- "I tested on 15 real products from my kitchen to validate"
