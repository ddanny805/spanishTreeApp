from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
import spacy
from spacy import displacy
import os
import time

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
def add_global_headers(response):
    """
    Apply headers to all responses globally.
    """
    response.headers["Content-Type"] = response.headers.get("Content-Type", "application/json; charset=utf-8")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route("/")
def index():
    """
    Serve the main index page with appropriate headers.
    """
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route("/generate", methods=["POST"])
def generate():
    """
    Process the sentence and return breakdown and tree as JSON.
    """
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

    response = jsonify({"breakdown": "\n".join(breakdown), "tree": svg})
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route("/static/<path:filename>")
def send_static(filename):
    """
    Serve static files with explicit headers and cache-busting query parameter.
    """
    static_folder = os.path.join(app.root_path, 'static')
    response = make_response(send_from_directory(static_folder, filename))
    
    # Append cache-busting query parameter
    cache_buster = int(time.time())
    response.headers["Content-Type"] = "application/octet-stream; charset=utf-8"
    if filename.endswith(".css"):
        response.headers["Content-Type"] = "text/css; charset=utf-8"
    elif filename.endswith(".js"):
        response.headers["Content-Type"] = "application/javascript; charset=utf-8"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        response.headers["Content-Type"] = "image/jpeg"
    elif filename.endswith(".png"):
        response.headers["Content-Type"] = "image/png"
    
    response.headers["Cache-Control"] = "public, max-age=180"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Busting"] = f"?v={cache_buster}"
    return response

if __name__ == "__main__":
    app.run(debug=True)
