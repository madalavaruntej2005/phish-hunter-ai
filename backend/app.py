"""
Phish Hunter AI — Flask REST API
Endpoint: POST /analyze
"""

from flask import Flask, request, jsonify, abort, redirect
from flask_cors import CORS
from dotenv import load_dotenv
import threading
import time
import requests as http_requests

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False
    print("Warning: flask-limiter not installed - no rate limiting")

from model import analyze, train_model, save_feedback, get_model
import os

load_dotenv()

# --- Self-ping keep-alive (prevents Render free-tier cold starts) ---
def _keep_alive():
    """Ping our own /api/health every 14 min so Render never spins down."""
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not base_url:
        return  # Only run on Render (env var is set automatically)
    url = f"{base_url}/api/health"
    while True:
        time.sleep(14 * 60)  # 14 minutes
        try:
            http_requests.get(url, timeout=10)
            print(f"[keep-alive] pinged {url}")
        except Exception as e:
            print(f"[keep-alive] ping failed: {e}")

_ka_thread = threading.Thread(target=_keep_alive, daemon=True)
_ka_thread.start()

app = Flask(__name__)

# --- Rate Limiter (optional) ---
if HAS_LIMITER:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
    )
else:
    # Stub so route decorators don't crash when HAS_LIMITER is False
    class _NoOpLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    limiter = _NoOpLimiter()

# --- CORS ---
# Allow Vercel frontend, localhost dev, and browser extension origins
ALLOWED_ORIGINS = [
    "https://phish-hunter-ai.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "null",   # browser extensions send Origin: null
]
# Also support any extra origins set via env var
extra = os.environ.get("ALLOWED_ORIGIN", "")
if extra:
    ALLOWED_ORIGINS.extend([o.strip() for o in extra.split(',') if o.strip()])

CORS(
    app,
    resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)


# --- Inject CORS headers on EVERY response (including errors & 503) ---
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS or not origin:
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
    else:
        response.headers["Access-Control-Allow-Origin"] = "https://phish-hunter-ai.vercel.app"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# --- Explicit OPTIONS handler for preflight ---
@app.route("/api/analyze", methods=["OPTIONS"])
@app.route("/api/feedback", methods=["OPTIONS"])
@app.route("/api/retrain", methods=["OPTIONS"])
@app.route("/api/health", methods=["OPTIONS"])
def handle_preflight():
    """Respond to CORS preflight requests immediately."""
    response = app.make_default_options_response()
    return response


# --- HTTPS redirect (production only, never for OPTIONS/preflight) ---
@app.before_request
def force_https():
    # Never redirect OPTIONS requests — browsers use them for CORS preflight
    if request.method == 'OPTIONS':
        return
    if os.environ.get("FLASK_ENV") == "production" and not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


# --- Routes ---

@app.route("/api/analyze", methods=["POST"])
@limiter.limit("10 per minute")
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


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """User feedback for model improvement."""
    data = request.get_json(silent=True)
    if not data or "text" not in data or "is_phish" not in data:
        return jsonify({"error": "Missing 'text' or 'is_phish'"}), 400
    text = data["text"][:1000]
    user_label = 1 if data["is_phish"] else 0
    save_feedback(text, 0.0, user_label)  # predicted_prob placeholder
    return jsonify({"message": "Feedback saved. Thanks for helping improve the model!"}), 200


@app.route("/api/retrain", methods=["POST"])
def retrain():
    """Retrain the model (admin endpoint - key protected)."""
    data = request.get_json(silent=True)
    if not data or data.get("key") != os.environ.get("RETRAIN_KEY"):
        abort(403)
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
    get_model()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    print(f"✅ API ready at http://localhost:{port}")
    app.run(debug=debug, host="0.0.0.0", port=port)