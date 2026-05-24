import os
import json
import base64
import re
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Load ingredient database
with open("data/ingredients.json") as f:
    INGREDIENT_DB = json.load(f)

# Configure Gemini (free tier)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-2.5-flash")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    resp = send_from_directory("templates", "index.html")
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.route("/analyze", methods=["POST"])
def analyze():
    ingredients_text = ""

    if "image" in request.files:
        image_file = request.files["image"]
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = image_file.mimetype or "image/jpeg"

        prompt = (
            "This is a food product label. "
            "Find the INGREDIENTS section and extract every single ingredient listed, including additives, E-codes, and numbers in brackets. "
            "Return them as a plain comma-separated string. "
            "Include everything — sweeteners, emulsifiers, raising agents, preservatives, antioxidants, flavourings. "
            "Keep INS/E numbers as-is (e.g. 471, 322, 955). "
            "Do NOT skip any ingredient. Do NOT include percentages or any other text."
        )

        response = model.generate_content([
            {"mime_type": mime, "data": image_b64},
            prompt
        ])
        ingredients_text = response.text.strip()

    else:
        data = request.get_json()
        ingredients_text = data.get("text", "").strip()

    if not ingredients_text:
        return jsonify({"error": "No ingredients provided"}), 400

    result = parse_and_analyze(ingredients_text)
    return jsonify(result)


# ── Core logic ──────────────────────────────────────────────────────────────────

def parse_and_analyze(raw_text):
    # Step 1: normalise separators
    # Replace & and AND (word boundary) with commas
    text = re.sub(r'\bAND\b', ',', raw_text, flags=re.IGNORECASE)
    text = re.sub(r'&', ',', text)
    # Remove roman numeral sub-qualifiers like (i), (ii), (iii), (iv)
    text = re.sub(r'\(\s*i{1,3}v?\s*\)', '', text, flags=re.IGNORECASE)
    # Remove square brackets but keep their contents
    text = re.sub(r'[\[\]]', '', text)

    raw_items = [i.strip().lower() for i in re.split(r'[,;]', text) if i.strip()]

    matched = []
    unmatched = []
    seen_ids = set()  # prevent duplicates

    for item in raw_items:
        found = match_ingredient(item)
        if found:
            if found["id"] not in seen_ids:
                matched.append(found)
                seen_ids.add(found["id"])
        else:
            # only keep non-trivial unmatched
            clean = item.strip()
            if len(clean) > 2 and not re.match(r'^\d+(\.\d+)?%?$', clean):
                unmatched.append(clean)

    ingredients = estimate_percentages(matched)
    verdicts = build_verdicts(matched)
    summary = build_summary(ingredients, verdicts)

    return {
        "ingredients": ingredients,
        "verdicts": verdicts,
        "summary": summary,
        "unmatched": unmatched
    }


def match_ingredient(item):
    """
    Fuzzy match — checks if alias is contained in item or item in alias.
    Shorter aliases (len < 4) must match exactly to avoid false positives.
    """
    best = None
    best_score = 0

    for key, data in INGREDIENT_DB.items():
        aliases = [key.lower()] + [a.lower() for a in data.get("aliases", [])]
        for alias in aliases:
            if len(alias) < 4:
                # short alias (like "322") — must be exact or bounded by non-digit
                if re.search(r'(?<!\d)' + re.escape(alias) + r'(?!\d)', item):
                    score = len(alias)
                    if score > best_score:
                        best_score = score
                        best = {"id": key, **data}
            else:
                if alias in item or item in alias:
                    score = len(alias)
                    if score > best_score:
                        best_score = score
                        best = {"id": key, **data}

    return best


def estimate_percentages(matched):
    if not matched:
        return []

    n = len(matched)
    weights = [1 / (i + 1) for i in range(n)]
    total = sum(weights)

    result = []
    for i, ing in enumerate(matched):
        pct = round((weights[i] / total) * 100)
        spoons = max(1, round(pct / 5))
        result.append({
            "name": ing["name"],
            "id": ing["id"],
            "percent": pct,
            "spoons": spoons,
            "spoon_label": ing.get("spoon_label", ing["name"]),
            "safety": ing.get("safety", "unknown"),
            "color": ing.get("color", "#B4B2A9"),
            "note": ing.get("note", "")
        })

    return result


def build_verdicts(matched):
    profiles = ["adults", "diabetics", "infants", "pregnant", "hypertension", "elderly", "fitness"]
    priority = {"avoid": 3, "caution": 2, "okay": 1, "good": 0}
    labels = {"avoid": "Not recommended", "caution": "Use caution", "okay": "Okay in moderation", "good": "Good choice"}

    verdicts = {}
    for profile in profiles:
        worst = "okay"
        reasons = []
        for ing in matched:
            flag = ing.get("profiles", {}).get(profile, "okay")
            if priority.get(flag, 1) > priority.get(worst, 1):
                worst = flag
            if flag in ("avoid", "caution"):
                note = ing.get("profile_notes", {}).get(profile, "")
                if note and note not in reasons:
                    reasons.append(note)

        verdicts[profile] = {
            "verdict": worst,
            "label": labels[worst],
            "reasons": reasons[:2]
        }

    return verdicts


def build_summary(ingredients, verdicts):
    if not ingredients:
        return {"overall": "Could not parse", "main_ingredient": "", "main_percent": 0, "concern_count": 0, "caution_count": 0}

    top = ingredients[0]
    concerns = [v for v in verdicts.values() if v["verdict"] == "avoid"]
    cautions = [v for v in verdicts.values() if v["verdict"] == "caution"]

    if len(concerns) >= 3:
        overall = "High concern"
    elif len(cautions) >= 2:
        overall = "Moderate concern"
    else:
        overall = "Generally okay"

    return {
        "overall": overall,
        "main_ingredient": top["name"],
        "main_percent": top["percent"],
        "concern_count": len(concerns),
        "caution_count": len(cautions)
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

