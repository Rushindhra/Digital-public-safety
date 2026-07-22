from app.ml.scam import analyse_scam
from app.schemas.platform import ScamRequest


def test_digital_arrest_message_is_high_risk():
    result = analyse_scam(ScamRequest(content="CBI says you are under digital arrest. Do not disconnect. Transfer money to a safe account immediately."))
    assert result.risk_score >= 75
    assert result.risk_level == "critical"
    assert "digital_arrest" in result.scam_types


def test_benign_message_is_low_risk():
    result = analyse_scam(ScamRequest(content="Please meet me for lunch tomorrow."))
    assert result.risk_level == "low"
    # ML classifier may have some false positive signals, so we allow score < 25 for low risk
    assert result.risk_score < 25

