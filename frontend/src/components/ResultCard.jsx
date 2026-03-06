import { useEffect, useRef } from 'react'

const CIRCUMFERENCE = 2 * Math.PI * 46 // radius = 46

const getRiskConfig = (riskLevel) => {
    switch (riskLevel) {
        case 'DANGEROUS':
            return {
                color: '#ef4444',
                badgeClass: 'dangerous',
                icon: '🚨',
                title: 'Dangerous — High Scam Risk',
                subtitle: 'This message shows strong signs of phishing or fraud.',
            }
        case 'SUSPICIOUS':
            return {
                color: '#f59e0b',
                badgeClass: 'suspicious',
                icon: '⚠️',
                title: 'Suspicious — Proceed with Caution',
                subtitle: 'This message has some indicators of a scam.',
            }
        default:
            return {
                color: '#10b981',
                badgeClass: 'safe',
                icon: '✅',
                title: 'Safe — No Threats Detected',
                subtitle: 'This message appears legitimate.',
            }
    }
}

export default function ResultCard({ result }) {
    const ringRef = useRef(null)
    const { probability, risk_level, explanation, flagged_keywords, suspicious_domains, urgency_phrases } = result
    const config = getRiskConfig(risk_level)

    const offset = CIRCUMFERENCE - (probability / 100) * CIRCUMFERENCE

    useEffect(() => {
        if (ringRef.current) {
            // Animate from full offset (empty) to target
            ringRef.current.style.strokeDashoffset = CIRCUMFERENCE
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    ringRef.current.style.strokeDashoffset = offset
                })
            })
        }
    }, [probability, offset])

    const hasKeywords = flagged_keywords?.length > 0
    const hasDomains = suspicious_domains?.length > 0
    const hasUrgency = urgency_phrases?.length > 0
    const hasTags = hasKeywords || hasDomains || hasUrgency

    return (
        <div className="result-card">
            {/* Top: Ring + Info */}
            <div className="result-top">
                {/* SVG Probability Ring */}
                <div className="prob-ring-container">
                    <svg viewBox="0 0 110 110">
                        <circle className="prob-ring-bg" cx="55" cy="55" r="46" />
                        <circle
                            ref={ringRef}
                            className="prob-ring-fill"
                            cx="55"
                            cy="55"
                            r="46"
                            stroke={config.color}
                            strokeDasharray={CIRCUMFERENCE}
                            strokeDashoffset={CIRCUMFERENCE}
                            style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
                        />
                    </svg>
                    <div className="prob-ring-label">
                        <span className="prob-pct" style={{ color: config.color }}>
                            {probability}%
                        </span>
                        <span className="prob-pct-sub">Scam</span>
                    </div>
                </div>

                {/* Info */}
                <div className="result-info">
                    <span className={`risk-badge ${config.badgeClass}`}>
                        <span className="badge-icon">{config.icon}</span>
                        {risk_level}
                    </span>
                    <p className="result-title">{config.title}</p>
                    <p className="result-subtitle">{config.subtitle}</p>

                    {/* Mini progress bar */}
                    <div className="prob-bar-track">
                        <div
                            className="prob-bar-fill"
                            style={{
                                width: `${probability}%`,
                                background: `linear-gradient(90deg, ${config.color}88, ${config.color})`,
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Explanation */}
            <div className="explanation-box">
                <h3>🔍 Analysis Explanation</h3>
                <p>{explanation}</p>
            </div>

            {/* Flagged Tags */}
            {hasTags && (
                <div className="tags-section">
                    <h3>🏷️ Detected Signals</h3>
                    <div className="tags-container">
                        {flagged_keywords?.map((kw, i) => (
                            <span key={`kw-${i}`} className="tag tag-keyword">⚠ {kw}</span>
                        ))}
                        {urgency_phrases?.map((ph, i) => (
                            <span key={`up-${i}`} className="tag tag-urgency">⏰ {ph}</span>
                        ))}
                        {suspicious_domains?.map((dm, i) => (
                            <span key={`dm-${i}`} className="tag tag-domain">🔗 {dm}</span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
