from flask import Flask, request, jsonify, render_template, send_from_directory
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
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

    # Create a response with proper headers
    response = jsonify({"breakdown": "\n".join(breakdown), "tree": svg})

    # Set headers
    response.headers["Content-Type"] = "application/json"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Prevent caching
    response.headers["X-Content-Type-Options"] = "nosniff"  # Prevent MIME sniffing

    return response

# Override send_from_directory to add proper headers for static files
@app.route("/static/<path:filename>")
def send_static(filename):
    # Get the full file path
    static_folder = os.path.join(app.root_path, 'static')
    file_path = os.path.join(static_folder, filename)

    # Send the file with appropriate headers
    response = send_from_directory(static_folder, filename)

    # Set headers for static files
    response.headers["Cache-Control"] = "public, max-age=31536000"  # Cache for 1 year
    response.headers["X-Content-Type-Options"] = "nosniff"  # Prevent MIME sniffing

    # Set Content-Type based on file extension
    if filename.endswith(".css"):
        response.headers["Content-Type"] = "text/css"
    elif filename.endswith(".js"):
        response.headers["Content-Type"] = "application/javascript"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        response.headers["Content-Type"] = "image/jpeg"
    elif filename.endswith(".png"):
        response.headers["Content-Type"] = "image/png"
    # You can add more content types based on your static files

    return response

if __name__ == "__main__":
    app.run(debug=True)
