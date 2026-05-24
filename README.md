# 🧪 WhatSinIt — Know What You're Actually Eating

**Live demo → [whatsinit-e4rh.onrender.com](https://whatsinit-e4rh.onrender.com)**

WhatSinIt decodes the ingredients list on any Indian packaged food product and tells you — in plain language — what you're actually eating, who should be careful, and why.

---

## What it does

Paste an ingredients list or upload a photo of a food label and instantly get:

- **🫙 Jar visualization** — ingredient proportions shown as layers inside a jar, scaled by weight
- **🥄 Spoon translation** — converts gram weights into teaspoons so you can visualize quantities ("2 tsp of sugar per serving")
- **👥 Consumer profile verdicts** — tailored safety verdicts for 7 profiles: healthy adults, diabetics, infants, pregnant women, high blood pressure, elderly, and fitness/gym
- **💡 Plain English summary** — one paragraph that tells you exactly what this product is and whether to avoid it

---

## Features

- **Two input modes** — type/paste an ingredients list, or upload a label photo (Gemini Vision reads it for you)
- **107+ ingredients tracked** — covers the most common additives, preservatives, sweeteners, oils, emulsifiers, colours, and nutrients found in Indian packaged foods
- **FSSAI-aligned classifications** — safety ratings reference Indian and international food safety standards (FSSAI, EFSA, FDA)
- **Zero signup required** — open and use, no account needed
- **Fully free** — no paywalls, no ads

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| AI / Vision | Google Gemini 2.0 Flash (free tier) |
| Ingredient DB | Curated JSON — 107+ entries |
| Frontend | Plain HTML + CSS + Vanilla JS |
| Deployment | Render (free tier) |

No heavy frameworks. No database server. The entire backend is a single `app.py` file.

---

## How it works

1. User inputs an ingredients list (text or image)
2. If image → Gemini Vision extracts the ingredients text
3. Parser normalises separators (`&`, `AND`, bracket groups) and fuzzy-matches each ingredient against the local database
4. Matched ingredients are ranked by label order (FSSAI/FDA rule: listed in descending weight order)
5. Safety verdicts are looked up per consumer profile from the database
6. Results rendered as jar SVG, spoon breakdown, verdict cards, and summary

---

## Run locally

**1. Clone the repo**
```bash
git clone https://github.com/trishab004/whatsinit.git
cd whatsinit
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Get a free Gemini API key**

Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → sign in with Google → Create API key

Free tier: 1500 requests/day, no credit card needed.

**4. Set the API key**
```bash
# Mac / Linux
export GEMINI_API_KEY="your-key-here"

# Windows
set GEMINI_API_KEY=your-key-here
```

**5. Run**
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## Project structure

```
whatsinit/
├── app.py                  # Flask backend — all logic in one file
├── requirements.txt
├── data/
│   └── ingredients.json    # Ingredient database — add new entries here
└── templates/
    └── index.html          # Frontend — HTML + CSS + plain JS, no frameworks
```

---

## Adding ingredients to the database

Open `data/ingredients.json` and add a new entry:

```json
"ingredient_key": {
  "name": "Display name",
  "aliases": ["common name", "e-code", "ins number", "other names"],
  "safety": "good | okay | caution | avoid",
  "color": "#hexcolor",
  "spoon_label": "Short label for spoon breakdown",
  "note": "One-line plain English explanation",
  "profiles": {
    "adults": "good | okay | caution | avoid",
    "diabetics": "...",
    "infants": "...",
    "pregnant": "...",
    "hypertension": "...",
    "elderly": "...",
    "fitness": "..."
  },
  "profile_notes": {
    "infants": "Reason shown in verdict card"
  }
}
```

---

## Consumer profiles

| Profile | What it checks |
|---|---|
| 🧑 Healthy adults | General safety and cumulative additive load |
| 🩸 Diabetics | Glycemic index, sugar alcohols, hidden sugars |
| 👶 Infants (<2 yrs) | Allergens, additives, salt, sweeteners |
| 🤰 Pregnant women | Artificial additives, trans fats, high-risk preservatives |
| ❤️ High blood pressure | Sodium, saturated fat, phosphates |
| 🧓 Elderly | Digestive additives, high sodium, phosphates |
| 💪 Gym / fitness | Empty calories, trans fat, high GI fillers |

---

## Deployment

Deployed on [Render](https://render.com) free tier.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python app.py`
- **Environment variable:** `GEMINI_API_KEY`

---

## License

MIT — free to use, modify, and build on.
