import { useState, useCallback, useEffect } from 'react'
import './index.css'
import ResultCard from './components/ResultCard.jsx'

// In production (Vercel), VITE_API_URL is set to the Render backend URL.
// In local dev, use localhost:5000 directly to avoid proxy issues.
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'


const EXAMPLE_INPUTS = [
    {
        icon: '🚨',
        label: 'Phishing SMS',
        text: "URGENT: Your bank account has been suspended. Click here immediately to restore access: http://bank-secure-login.xyz/verify",
    },
    {
        icon: '🎁',
        label: 'Prize Scam',
        text: "Congratulations! You've won $1000 Amazon gift card. Claim now before it expires: bit.ly/win-prize-now",
    },
    {
        icon: '✅',
        label: 'Legit Message',
        text: "Hi, your Uber ride is arriving in 3 minutes. Driver: Raju, Car: MH-02-AB-1234.",
    },
    {
        icon: '👻',
        label: 'Phishing Email',
        text: "Action Required: Your Apple ID has been locked. Verify your identity to unlock: apple-id-help.ml/verify",
    },
]

export default function App() {
    const [inputText, setInputText] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [installPrompt, setInstallPrompt] = useState(null)
    const [showInstallBanner, setShowInstallBanner] = useState(false)

    // Capture PWA install prompt
    useEffect(() => {
        const handler = (e) => {
            e.preventDefault()
            setInstallPrompt(e)
            setShowInstallBanner(true)
        }
        window.addEventListener('beforeinstallprompt', handler)
        return () => window.removeEventListener('beforeinstallprompt', handler)
    }, [])

    const handleInstall = async () => {
        if (!installPrompt) return
        installPrompt.prompt()
        const { outcome } = await installPrompt.userChoice
        if (outcome === 'accepted') {
            setShowInstallBanner(false)
            setInstallPrompt(null)
        }
    }

    const handleAnalyze = useCallback(async () => {
        if (!inputText.trim()) return
        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputText.trim() }),
            })

            // Get response text first to handle empty or non-JSON responses
            const responseText = await response.text()

            if (!responseText || !responseText.trim()) {
                throw new Error('Empty response from server. Please make sure the backend is running.')
            }

            let data
            try {
                data = JSON.parse(responseText)
            } catch (parseError) {
                // Server returned non-JSON response (like an error page)
                throw new Error(`Server returned invalid response: ${responseText.substring(0, 100)}`)
            }

            if (!response.ok) {
                throw new Error(data.error || `Analysis failed with status ${response.status}`)
            }

            setResult(data)
        } catch (err) {
            setError(err.message || 'Could not connect to the backend. Make sure Flask is running on port 5000.')
        } finally {
            setLoading(false)
        }
    }, [inputText])

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            handleAnalyze()
        }
    }

    const handleExample = (text) => {
        setInputText(text)
        setResult(null)
        setError(null)
    }

    const charLimit = 5000
    const charCount = inputText.length

    return (
        <div className="app-container">
            {/* Header */}
            <header className="header">
                <div className="header-badge">
                    <span className="dot" />
                    AI-Powered Detection
                </div>
                <h1>Phish Hunter AI</h1>
                <p className="header-subtitle">
                    Paste any email, SMS, URL, or QR code text below.
                    Our ML model instantly detects phishing, scams, and fraud.
                </p>
            </header>

            {/* Main Card */}
            <main className="main-card" role="main">
                {/* Input Section */}
                <div className="input-section">
                    <label htmlFor="phish-input">Paste Message / URL / QR Code Text</label>
                    <div className="textarea-wrapper">
                        <textarea
                            id="phish-input"
                            className="input-textarea"
                            placeholder={'Try pasting:\n• A suspicious SMS or email\n• A URL you want to check\n• A QR code\'s decoded text\n\nPress Ctrl+Enter to analyze quickly.'}
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            maxLength={charLimit}
                            aria-label="Input text to analyze"
                        />
                    </div>
                    <div className="char-count">
                        <span style={{ color: charCount > charLimit * 0.9 ? '#f59e0b' : 'inherit' }}>
                            {charCount.toLocaleString()}
                        </span>
                        {' / '}
                        {charLimit.toLocaleString()} characters
                    </div>
                </div>

                {/* Analyze Button */}
                <button
                    id="btn-analyze"
                    className="btn-analyze"
                    onClick={handleAnalyze}
                    disabled={loading || !inputText.trim()}
                    aria-label="Analyze text for phishing"
                >
                    {loading ? (
                        <>
                            <span className="spinner" />
                            Analyzing…
                        </>
                    ) : (
                        <>
                            🔍 Analyze for Scams
                        </>
                    )}
                </button>

                {/* Results */}
                {(result || error) && <div className="divider" />}

                {error && (
                    <div className="error-box" role="alert">
                        <span>⚠️</span>
                        <span>{error}</span>
                    </div>
                )}

                {result && <ResultCard result={result} />}
            </main>

            {/* Examples */}
            <section className="examples-section" aria-label="Example inputs">
                <p className="examples-header">Try an example</p>
                <div className="examples-grid">
                    {EXAMPLE_INPUTS.map((ex) => (
                        <button
                            key={ex.label}
                            className="example-btn"
                            onClick={() => handleExample(ex.text)}
                            title={ex.text}
                            id={`example-${ex.label.toLowerCase().replace(/\s+/g, '-')}`}
                        >
                            <span className="ex-icon">{ex.icon}</span>
                            <span>
                                <strong>{ex.label}</strong>
                                <br />
                                {ex.text.length > 70 ? ex.text.slice(0, 70) + '…' : ex.text}
                            </span>
                        </button>
                    ))}
                </div>
            </section>

            {/* PWA Install Banner */}
            {showInstallBanner && (
                <div className="install-banner" role="banner">
                    <div className="install-banner-left">
                        <span className="install-icon">📱</span>
                        <div>
                            <strong>Install Phish Hunter AI</strong>
                            <p>Add to your home screen for quick access</p>
                        </div>
                    </div>
                    <div className="install-banner-actions">
                        <button className="btn-install" onClick={handleInstall} id="btn-pwa-install">
                            Install
                        </button>
                        <button className="btn-dismiss" onClick={() => setShowInstallBanner(false)} aria-label="Dismiss">
                            ✕
                        </button>
                    </div>
                </div>
            )}

            {/* Footer */}
            <footer className="footer">
                <p>Phish Hunter AI • Built with React + Flask + Scikit-Learn</p>
                <p style={{ marginTop: '6px' }}>
                    For educational purposes. Always verify suspicious messages independently.
                </p>
            </footer>
        </div>
    )
}
