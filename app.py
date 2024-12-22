from flask import Flask, request, jsonify, render_template, make_response, send_from_directory
import spacy
from spacy import displacy
import os

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

# Mapping of dependency labels from English to Spanish
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
    """Add necessary headers to all responses."""
    response.headers["Content-Type"] = response.headers.get("Content-Type", "text/html; charset=utf-8")
    response.headers["Cache-Control"] = "max-age=180, must-revalidate"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    """Generate the linguistic breakdown and syntax tree."""
    data = request.get_json()
    sentence = data.get("sentence", "")

    if not sentence:
        return jsonify({"error": "No sentence provided."}), 400

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

    response = make_response(jsonify({"breakdown": "\n".join(breakdown), "tree": svg}))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Cache-Control"] = "max-age=180, must-revalidate"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files with proper headers."""
    static_folder = os.path.join(app.root_path, "static")
    response = make_response(send_from_directory(static_folder, filename))
    response.headers["Cache-Control"] = "max-age=180, must-revalidate"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

if __name__ == "__main__":
    app.run(debug=True)
