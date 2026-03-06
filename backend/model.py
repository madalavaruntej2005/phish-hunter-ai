"""
Phish Hunter AI — Machine Learning Model
Uses TF-IDF vectorizer + Logistic Regression to detect phishing/scam content.
"""

import os
import re
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from train_data import get_training_data

# --- Suspicious keyword patterns ---
PHISHING_KEYWORDS = [
    "urgent", "click here", "verify", "suspended", "winner", "congratulations",
    "claim", "prize", "free", "limited time", "act now", "immediately",
    "account blocked", "will be cancelled", "OTP", "bank account", "update kyc",
    "unusual activity", "locked", "expires", "arrested", "irs", "lottery",
    "unclaimed", "inheritance", "final notice", "security alert", "credentials",
    "won", "lucky draw", "bitcoin", "refund", "pending", "dispute",
]

SUSPICIOUS_DOMAIN_PATTERNS = [
    r"https?://[^\s]*\.(xyz|ml|tk|cc|ga|cf|gq|pw|top|icu|club|online|live|click)[^\s]*",
    r"https?://[^\s]*(-secure-|-login-|-verify-|-update-|-billing-)[^\s]*",
    r"bit\.ly|tinyurl|goo\.gl|t\.co/[a-z0-9]+",
    r"https?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
]

URGENCY_PHRASES = [
    "within 24 hours", "immediately", "right now", "do not delay",
    "act fast", "expires today", "last chance", "act now", "before it's too late",
    "limited time", "your account will be", "will be suspended", "will be blocked",
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "phish_model.pkl")


def preprocess(text: str) -> str:
    """Lowercase and normalize text."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_features(text: str) -> dict:
    """Extract interpretable features from the text."""
    text_lower = text.lower()

    flagged_keywords = [kw for kw in PHISHING_KEYWORDS if kw.lower() in text_lower]

    suspicious_domains = []
    for pattern in SUSPICIOUS_DOMAIN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        suspicious_domains.extend(matches)

    urgency_phrases = [ph for ph in URGENCY_PHRASES if ph.lower() in text_lower]

    has_url = bool(re.search(r"https?://", text, re.IGNORECASE))
    has_phone = bool(re.search(r"\b\d{10}\b", text))
    has_money = bool(re.search(r"(rs\.?|₹|\$|£)\s*[\d,]+", text, re.IGNORECASE))
    excessive_caps = len(re.findall(r'[A-Z]', text)) > len(text) * 0.25

    return {
        "flagged_keywords": flagged_keywords,
        "suspicious_domains": suspicious_domains,
        "urgency_phrases": urgency_phrases,
        "has_url": has_url,
        "has_phone": has_phone,
        "has_money": has_money,
        "excessive_caps": excessive_caps,
    }


def build_explanation(features: dict, probability: float) -> str:
    """Generate a human-readable explanation of the prediction."""
    reasons = []

    if features["flagged_keywords"]:
        kws = ", ".join(f'"{k}"' for k in features["flagged_keywords"][:5])
        reasons.append(f"Contains suspicious keywords: {kws}")

    if features["suspicious_domains"]:
        reasons.append(f"Links to suspicious/untrustworthy domain(s): {', '.join(features['suspicious_domains'][:2])}")

    if features["urgency_phrases"]:
        phrases = ", ".join(f'"{p}"' for p in features["urgency_phrases"][:3])
        reasons.append(f"Uses urgency/pressure tactics: {phrases}")

    if features["excessive_caps"]:
        reasons.append("Uses excessive capitalization (common in scam messages)")

    if features["has_money"]:
        reasons.append("Mentions monetary amounts (common in prize/refund scams)")

    if features["has_phone"] and probability > 0.4:
        reasons.append("Contains a phone number with suspicious context")

    if not reasons:
        if probability < 0.3:
            return "No significant phishing indicators detected. This message appears legitimate."
        else:
            return "ML model detected subtle phishing patterns based on message structure and vocabulary."

    return " | ".join(reasons)


def train_model():
    """Train and save the TF-IDF + Logistic Regression pipeline."""
    print("🧠 Training Phish Hunter AI model...")
    data = get_training_data()
    texts, labels = zip(*data)

    # Preprocess
    texts_clean = [preprocess(t) for t in texts]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            strip_accents='unicode',
            analyzer='word',
            min_df=1,
        )),
        ('clf', LogisticRegression(
            C=1.0,
            max_iter=500,
            random_state=42,
            class_weight='balanced',
        ))
    ])

    # Train (use all data — small dataset, no need for test split here)
    pipeline.fit(texts_clean, labels)

    # Quick eval on training data (for logging only)
    preds = pipeline.predict(texts_clean)
    acc = accuracy_score(labels, preds)
    print(f"✅ Model trained. Training accuracy: {acc*100:.1f}%")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")
    return pipeline


def load_model():
    """Load the saved model or train a fresh one."""
    if os.path.exists(MODEL_PATH):
        print("📦 Loading existing model...")
        return joblib.load(MODEL_PATH)
    else:
        return train_model()


# Global model instance
_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


def analyze(text: str) -> dict:
    """
    Analyze text for phishing/scam content.
    Returns: probability (%), risk_level, explanation, flagged_keywords.
    """
    model = get_model()

    # Preprocess & predict
    clean = preprocess(text)
    prob_array = model.predict_proba([clean])[0]
    # Index 1 = phishing probability
    phishing_prob = float(prob_array[1])

    # Extract human-readable features
    features = extract_features(text)

    # Boost probability based on hard signals
    boost = 0.0
    if features["suspicious_domains"]:
        boost += 0.15
    if len(features["flagged_keywords"]) >= 3:
        boost += 0.10
    if features["urgency_phrases"]:
        boost += 0.08

    phishing_prob = min(phishing_prob + boost, 0.99)

    # Build explanation
    explanation = build_explanation(features, phishing_prob)

    # Determine risk level
    if phishing_prob >= 0.70:
        risk_level = "DANGEROUS"
    elif phishing_prob >= 0.40:
        risk_level = "SUSPICIOUS"
    else:
        risk_level = "SAFE"

    return {
        "probability": round(phishing_prob * 100, 1),
        "risk_level": risk_level,
        "explanation": explanation,
        "flagged_keywords": features["flagged_keywords"],
        "suspicious_domains": features["suspicious_domains"],
        "urgency_phrases": features["urgency_phrases"],
    }
