# scraper_api.py
# Installe les dépendances : pip install requests flask flask-cors beautifulsoup4

import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

# ⚠️ Régénère cette clé dans ton dashboard Bright Data après configuration
BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY", "")

def scrape_url(url: str) -> str:
    """Scrape une URL via l'API REST Bright Data et retourne le texte brut."""
    try:
        resp = requests.post(
            "https://api.brightdata.com/request",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"
            },
            json={"url": url, "format": "raw"},
            timeout=20
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:4000]
    except Exception as e:
        return f"Erreur scraping {url}: {str(e)}"

@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Body attendu : { "urls": ["https://...", "https://..."] }
    Retourne : { "results": [{ "url": "...", "text": "..." }] }
    """
    data = request.json
    urls = data.get("urls", [])
    if not urls:
        return jsonify({"error": "Aucune URL fournie"}), 400

    results = []
    for url in urls[:5]:  # max 5 URLs par appel
        text = scrape_url(url)
        results.append({"url": url, "text": text})

    return jsonify({"results": results})

if __name__ == "__main__":
    print("Serveur de scraping démarré sur http://localhost:5050")
    app.run(port=5050, debug=False)
