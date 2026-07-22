"""Fast, hybrid multilingual scam-risk engine (rules + ML + phishing patterns)."""
import re

from app.ml.scam_classifier import ml_scam_probability, phishing_pattern_hits
from app.schemas.platform import ScamRequest, ScamResult, Signal

PATTERNS = {
    "authority_impersonation": (
        24,
        [
            r"\b(cbi|enforcement directorate|ed officer|income tax|customs|police|court|rbi|ncrp)\b",
            r"सीबीआई|पुलिस|कस्टम|आयकर|साइबर",
        ],
    ),
    "digital_arrest": (
        30,
        [
            r"digital arrest|under arrest|arrest warrant|video call.*(?:stay|remain)|skype call",
            r"डिजिटल अरेस्ट|गिरफ्तार|वारंट",
        ],
    ),
    "payment_request": (
        25,
        [
            r"\b(upi|bank transfer|security deposit|safe account|pay now|transfer money|noc account)\b",
            r"पैसे भेज|भुगतान|खाते में जमा|ट्रांसफर",
        ],
    ),
    "urgency_threat": (
        17,
        [
            r"immediately|within \d+ (?:minute|hour)|do not disconnect|final warning|legal action|blocked within",
            r"तुरंत|फोन मत काट|कानूनी कार्रवाई",
        ],
    ),
    "secrecy_pressure": (
        12,
        [
            r"do not tell|keep (?:this )?secret|confidential investigation|don't contact",
            r"किसी को मत बताना|गुप्त",
        ],
    ),
    "credential_theft": (
        28,
        [r"\b(otp|cvv|pin|password|screen share|remote access|aadhaar link)\b"],
    ),
    "phishing_link": (20, []),
}


def analyse_scam(payload: ScamRequest) -> ScamResult:
    text = payload.content
    text_lower = text.lower()
    signals: list[Signal] = []
    score = 0.0
    scam_types: list[str] = []

    for name, (weight, patterns) in PATTERNS.items():
        evidence: list[str] = []
        for pattern in patterns:
            match = re.search(pattern, text_lower, flags=re.IGNORECASE)
            if match:
                evidence.append(match.group(0)[:80])
        if name == "phishing_link":
            phish_hits = phishing_pattern_hits(text)
            if phish_hits:
                evidence.extend(phish_hits)
        if evidence:
            signals.append(Signal(name=name, weight=weight, evidence=evidence))
            score += weight
            if name in {"authority_impersonation", "digital_arrest"}:
                scam_types.append("digital_arrest")
            if name == "phishing_link":
                scam_types.append("phishing")

    ml_prob, ml_conf = ml_scam_probability(text)
    if ml_prob >= 0.5:
        ml_weight = round(ml_prob * 40, 1)
        signals.append(
            Signal(
                name="ml_classifier",
                weight=ml_weight,
                evidence=[f"ML scam probability {ml_prob:.0%} (trained on UCI SMS + curated corpus)"],
            )
        )
        score += ml_weight
        if ml_prob >= 0.7:
            scam_types.append("ml_detected_fraud")

    score = min(score, 100)
    level = (
        "critical"
        if score >= 75
        else "high"
        if score >= 50
        else "medium"
        if score >= 25
        else "low"
    )

    rule_conf = min(0.55 + len(signals) * 0.08, 0.95) if signals else 0.62
    confidence = round(max(rule_conf, ml_conf) if ml_conf else rule_conf, 2)

    actions = [
        "Do not transfer money or share OTP, PIN, CVV, or passwords.",
        "End the call and verify independently using an official published number.",
    ]
    if score >= 50:
        actions += [
            "Call 1930 immediately if money was transferred.",
            "Report at https://cybercrime.gov.in and preserve messages, numbers, and receipts.",
        ]
    if "digital_arrest" in scam_types:
        actions.append("Digital arrest is a known scam — no Indian agency conducts arrests over video call.")

    return ScamResult(
        risk_score=round(score, 1),
        confidence=confidence,
        risk_level=level,
        scam_types=sorted(set(scam_types)) or (["suspicious_solicitation"] if signals else []),
        signals=signals,
        explanation=(
            f"Detected {len(signals)} independent manipulation or fraud indicators "
            f"(rule engine + ML trained on UCI SMS Spam Collection and curated Indian fraud corpus). "
            "This is decision support, not a legal finding."
        ),
        suggested_actions=actions,
    )
