# 🎣 Phish Hunter AI

**Real-time scam and phishing detection powered by Machine Learning.**

Paste any suspicious email, SMS, URL, or QR code text — Phish Hunter AI instantly analyzes it using a TF-IDF + Logistic Regression model and explains exactly why it was flagged.

![Phish Hunter AI](https://phish-hunter-ai.vercel.app/og.png)

---

## 🚀 Live Demo

| Service | URL |
|---|---|
| 🌐 **Web App** | [phish-hunter-ai.vercel.app](https://phish-hunter-ai.vercel.app) |
| 🔧 **API** | [phish-hunter-ai-backend.onrender.com](https://phish-hunter-ai-backend.onrender.com/api/health) |

---

## ✨ Features

- 🔍 **Instant analysis** of emails, SMS, URLs, and QR code text
- 📊 **Scam probability %** with animated probability ring
- 🚨 **Risk level badge** — SAFE / SUSPICIOUS / DANGEROUS
- 🏷️ **Flagged signal tags** — keywords, urgency phrases, suspicious domains
- 📱 **PWA** — install on your phone from Chrome/Safari
- 🧩 **Browser Extension** — right-click any text to analyze (Chrome/Firefox)

---

## 🧠 How It Works

```
User Input → TF-IDF Vectorizer → Logistic Regression → Probability Score
                                                      ↓
                            Feature Extraction (keywords, domains, urgency)
                                                      ↓
                              Probability Boosting → Risk Level → Explanation
```

---

## 🏗️ Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Styling | Vanilla CSS (Glassmorphism) |
| Backend | Python Flask |
| ML | scikit-learn (TF-IDF + Logistic Regression) |
| Deployment | Vercel (frontend) + Render (backend) |

---

## ⚙️ Run Locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
# API ready at http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App ready at http://localhost:5173
```

---

## 📁 Project Structure

```
Phish Hunter AI/
├── backend/
│   ├── app.py          # Flask REST API
│   ├── model.py        # TF-IDF + Logistic Regression
│   ├── train_data.py   # 50 phishing + safe training examples
│   ├── requirements.txt
│   ├── Procfile        # Render/Heroku deployment
│   └── render.yaml     # Render auto-deploy config
├── frontend/
│   ├── src/
│   │   ├── App.jsx     # Main UI
│   │   ├── index.css   # Dark glassmorphism styles
│   │   └── components/ResultCard.jsx
│   ├── public/
│   │   ├── manifest.json  # PWA manifest
│   │   └── sw.js          # Service worker
│   └── vercel.json     # Vercel SPA routing
└── browser-extension/
    ├── manifest.json   # Chrome MV3
    ├── popup.html/js/css
    ├── background.js   # Context menu
    └── content.js
```

---

## 🧩 Install Browser Extension

1. Go to `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load unpacked** → select the `browser-extension/` folder
4. The 🎣 icon appears in your toolbar!

---

## 📄 API Reference

**POST** `/api/analyze`

```json
// Request
{ "text": "URGENT: Your account is suspended. Click: http://fake-bank.xyz" }

// Response
{
  "probability": 95.2,
  "risk_level": "DANGEROUS",
  "explanation": "Contains suspicious keywords: urgent, verify | Suspicious domain: .xyz",
  "flagged_keywords": ["urgent", "verify", "click here"],
  "suspicious_domains": ["fake-bank.xyz"],
  "urgency_phrases": ["immediately"]
}
```

---

## 📝 License

MIT — free to use, modify, and distribute.

---

<p align="center">Built with ❤️ using React + Flask + scikit-learn</p>
