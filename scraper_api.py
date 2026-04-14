import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY", "").strip()

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def scrape_url(url: str) -> str:
    try:
        resp = requests.post(
            "https://api.brightdata.com/request",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"
            },
            json={"url": url, "zone": "data_center", "format": "raw"},
            timeout=20
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:4000]
    except Exception as e:
        return f"Erreur: {str(e)}"

@app.route("/scrape", methods=["POST", "OPTIONS"])
def scrape():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json
    urls = data.get("urls", [])
    if not urls:
        return jsonify({"error": "Aucune URL fournie"}), 400
    results = [{"url": u, "text": scrape_url(u)} for u in urls[:5]]
    return jsonify({"results": results})

@app.route("/")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
