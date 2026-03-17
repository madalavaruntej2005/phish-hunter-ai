# Phish Hunter AI Error Fixes TODO

## 1. Fix SW Cache Error (chrome-extension scheme)
- [ ] Edit frontend/public/sw.js: Add scheme check before cache.put
- [ ] Test locally: npm run dev, check console for chrome-extension requests
- [ ] Deploy to Vercel

## 2. Fix API 405
- [ ] Deploy backend to Render (render.yaml)
- [ ] Get Render URL
- [ ] Set Vercel env: VITE_API_URL=render-url
- [ ] Test POST /api/analyze

## 3. PWA Banner
- [ ] Check manifest.json scope/start_url
- [ ] Test install banner

## Testing & Local Setup
**IMPORTANT: Run BOTH servers simultaneously!**

1. Backend: `cd backend && pip install -r requirements.txt && python app.py` (runs on http://localhost:5000)
2. Frontend: New terminal `cd frontend && npm install && npm run dev` (runs on http://localhost:5173, proxies /api → 5000)

Vite.config.js already proxies /api to localhost:5000 for dev.

- Prod: Deploy backend Render.com, frontend Vercel, set VITE_API_URL=render-url

Common issues:
- API 404/405: Backend not running on 5000
- Vite HMR WS fail: Normal if file:// open; use npm run dev
- SW fetch fail: Backend down or CORS
