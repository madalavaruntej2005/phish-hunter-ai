"""
Phish Hunter AI — Flask REST API
Endpoint: POST /analyze
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from model import analyze, train_model
import os

app = Flask(__name__)

# Allow local dev, browser extensions, and deployed frontend (set ALLOWED_ORIGIN on Render)
_frontend_url = os.environ.get("ALLOWED_ORIGIN", "")
_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "chrome-extension://*",
    "moz-extension://*",
]
if _frontend_url:
    _origins.append(_frontend_url)

CORS(app, resources={r"/api/*": {"origins": _origins}}, supports_credentials=False)



@app.route("/api/analyze", methods=["POST"])
def analyze_text():
    """Analyze submitted text for phishing/scam indicators."""
    data = request.get_json(silent=True)

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body."}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text cannot be empty."}), 400

    if len(text) > 5000:
        return jsonify({"error": "Text too long. Maximum 5000 characters."}), 400

    try:
        result = analyze(text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/retrain", methods=["POST"])
def retrain():
    """Retrain the model (admin endpoint)."""
    global _model
    from model import _model
    try:
        train_model()
        return jsonify({"message": "Model retrained successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "Phish Hunter AI"}), 200


@app.route("/", methods=["GET"])
def index():
    """Root endpoint - API info."""
    return jsonify({
        "service": "Phish Hunter AI",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/analyze": "Analyze text for phishing (body: {\"text\": \"message\"})",
            "GET /api/health": "Health check",
            "POST /api/retrain": "Retrain the model (admin)"
        }
    }), 200


if __name__ == "__main__":
    # Warm up model on startup
    print("🚀 Starting Phish Hunter AI backend...")
    from model import get_model
    get_model()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    print(f"✅ API ready at http://localhost:{port}")
    app.run(debug=debug, host="0.0.0.0", port=port)

