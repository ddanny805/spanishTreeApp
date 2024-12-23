from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
import spacy
from spacy import displacy

app = Flask(__name__)

# Load spaCy Spanish model
nlp = spacy.load("es_core_news_sm")

# Mapping of POS tags from English to Spanish
POS_MAPPING = {
    "PROPN": "Nombre propio",
    "AUX": "Verbo auxiliar",
    "ADV": "Adverbio",
    "ADJ": "Adjetivo",
    "CCONJ": "Conjunción de coordinación",
    "VERB": "Verbo",
    "NOUN": "Sustantivo",
    "PRON": "Pronombre",
    "DET": "Determinante",
    "ADP": "Adposición",
    "NUM": "Numeral",
    "PUNCT": "Signo de puntuación",
    "SYM": "Símbolo",
    "X": "Otro",
}

DEP_LABELS_MAPPING = {
    "nsubj": "sujeto nominal",
    "cop": "verbo copulativo",
    "advmod": "modificador adverbial",
    "obj": "objeto",
    "amod": "modificador adjetival",
    "det": "determinante",
    "root": "raíz",
    "cc": "conjunción coordinada",
    "conj": "conjunción",
    "punct": "puntuación",
    "case": "caso",
    "obl": "complemento oblicuo",
    "mark": "marcador",
    "xcomp": "complemento abierto",
    "aux": "auxiliar",
    "fixed": "fijo",
    "nmod": "modificador nominal",
    "appos": "aposición",
    "nummod": "modificador numérico",
    "dep": "dependencia",
}


@app.after_request
def add_headers(response):
    """Add headers globally."""
    response.headers["Content-Type"] = response.headers.get("Content-Type", "text/html; charset=utf-8")
    response.headers["Cache-Control"] = response.headers.get("Cache-Control", "no-store")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def index():
    html_response = make_response(render_template("index.html"))
    html_response.headers["Cache-Control"] = "no-store"
    return html_response


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files with proper cache and content-type."""
    response = make_response(send_from_directory("static", filename))
    if filename.endswith(".css"):
        response.headers["Content-Type"] = "text/css; charset=utf-8"
    elif filename.endswith(".js"):
        response.headers["Content-Type"] = "application/javascript; charset=utf-8"
    elif filename.endswith(".jpg") or filename.endswith(".png"):
        response.headers["Content-Type"] = "image/jpeg" if filename.endswith(".jpg") else "image/png"
    response.headers["Cache-Control"] = "max-age=180, public"
    return response


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    sentence = data.get("sentence", "")

    if not sentence:
        response = jsonify({"error": "No sentence provided."})
        response.headers["Cache-Control"] = "no-store"
        return response, 400

    # Process the sentence
    doc = nlp(sentence)

    # Text-based breakdown with Spanish POS labels
    breakdown = []
    for token in doc:
        pos_spanish = POS_MAPPING.get(token.pos_, token.pos_)
        breakdown.append(f"({pos_spanish}: {token.text})")

    # Generate the SVG for dependency visualization
    svg = displacy.render(doc, style="dep", options={"compact": True, "bg": "#ffffff"})

    # Replace both POS tags and dependency labels with Spanish equivalents
    for eng_label, spa_label in DEP_LABELS_MAPPING.items():
        svg = svg.replace(f">{eng_label}<", f">{spa_label}<")
    for eng_pos, spa_pos in POS_MAPPING.items():
        svg = svg.replace(f">{eng_pos}<", f">{spa_pos}<")

    response = jsonify({"breakdown": "\n".join(breakdown), "tree": svg})
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(debug=True)
