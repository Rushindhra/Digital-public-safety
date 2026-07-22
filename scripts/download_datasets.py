#!/usr/bin/env python3
"""
Download and prepare public datasets for the Digital Public Safety platform.

Sources (see datasets/SOURCES.md):
- UCI SMS Spam Collection
- geohacker/india GeoJSON
- Curated RBI banknote specifications
- Curated digital-arrest / cyber fraud transcripts
- Phishing pattern corpus (derived from public phishing research corpora)
- Fraud-network seed graphs (IEEE-CIS / credit-card fraud inspired)

Kaggle datasets require manual download — see download_kaggle.ps1
"""
from __future__ import annotations

import json
import logging
import shutil
import urllib.request
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("download_datasets")

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
RAW = DATASETS / "raw"
PROCESSED = DATASETS / "processed"
REFERENCE = DATASETS / "reference"
GEO = DATASETS / "geo"

UCI_SMS_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
GEO_URLS = {
    "india_states.geojson": "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
    "india_districts.geojson": "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson",
}


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("Already exists: %s", dest.name)
        return
    logger.info("Downloading %s", url)
    urllib.request.urlretrieve(url, dest)


def download_uci_sms() -> Path:
    zip_path = RAW / "sms_spam_collection.zip"
    _download(UCI_SMS_URL, zip_path)
    extract_dir = RAW / "sms_spam"
    if not (extract_dir / "SMSSpamCollection").exists():
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(extract_dir)
    return extract_dir / "SMSSpamCollection"


def download_geojson() -> None:
    for name, url in GEO_URLS.items():
        _download(url, GEO / name)


def write_rbi_reference() -> None:
    """RBI Mahatma Gandhi (New) series security features — public reference data."""
    specs = {
        "source": "Reserve Bank of India — Know Your Banknotes (Mahatma Gandhi Series)",
        "source_url": "https://www.rbi.org.in/commonman/English/Scripts/KnowYourBankNotes.aspx",
        "denominations": {
            "100": {
                "dimensions_mm": [142, 66],
                "color": "lavender",
                "security_features": [
                    "see_through_register",
                    "latent_image",
                    "microletters",
                    "intaglio_printing",
                    "security_thread",
                    "watermark",
                    "optically_variable_ink",
                    "raised_printing",
                ],
                "thread": "greenish_blue_silver_dash",
                "watermark": "mahatma_gandhi_electrotype_100",
            },
            "200": {
                "dimensions_mm": [146, 66],
                "color": "bright_yellow",
                "security_features": [
                    "see_through_register",
                    "latent_image",
                    "microletters",
                    "intaglio_printing",
                    "security_thread",
                    "watermark",
                    "optically_variable_ink",
                ],
                "thread": "greenish_blue",
                "watermark": "mahatma_gandhi_electrotype_200",
            },
            "500": {
                "dimensions_mm": [150, 66],
                "color": "stone_grey",
                "security_features": [
                    "see_through_register",
                    "latent_image",
                    "microletters",
                    "intaglio_printing",
                    "security_thread",
                    "watermark",
                    "optically_variable_ink",
                    "raised_printing",
                    "bleed_lines",
                ],
                "thread": "green_to_blue_500",
                "watermark": "mahatma_gandhi_electrotype_500",
            },
            "2000": {
                "dimensions_mm": [166, 66],
                "color": "magenta",
                "security_features": [
                    "see_through_register",
                    "latent_image",
                    "microletters",
                    "intaglio_printing",
                    "security_thread",
                    "watermark",
                    "optically_variable_ink",
                    "raised_printing",
                    "bleed_lines",
                    "hidden_image",
                ],
                "thread": "green_to_blue_2000",
                "watermark": "mahatma_gandhi_electrotype_2000",
            },
        },
        "ocr_tools_recommended": [
            "https://github.com/tesseract-ocr/tesseract",
            "https://github.com/JaidedAI/EasyOCR",
        ],
    }
    REFERENCE.mkdir(parents=True, exist_ok=True)
    path = REFERENCE / "rbi_banknote_specs.json"
    path.write_text(json.dumps(specs, indent=2), encoding="utf-8")
    logger.info("Wrote %s", path)


def write_digital_arrest_corpus() -> None:
    """Curated Indian digital-arrest and cyber-fraud messages (NCRB / cybercrime.gov.in patterns)."""
    corpus = [
        {
            "id": "da_001",
            "content": "This is CBI cyber crime branch. You are under digital arrest. Do not disconnect the Skype call. Transfer all savings to the NOC safe account immediately or warrant will be issued.",
            "label": "scam",
            "category": "digital_arrest",
            "tags": ["authority_impersonation", "digital_arrest", "payment_request", "urgency_threat"],
            "language": "en",
            "source": "curated_ncrb_cybercrime_patterns",
        },
        {
            "id": "da_002",
            "content": "Enforcement Directorate officer here. Your Aadhaar linked to money laundering case. Pay verification fee via UPI to avoid arrest.",
            "label": "scam",
            "category": "digital_arrest",
            "tags": ["authority_impersonation", "payment_request", "urgency_threat"],
            "language": "en",
            "source": "curated_ncrb_cybercrime_patterns",
        },
        {
            "id": "da_003",
            "content": "आप डिजिटल गिरफ्तारी में हैं। वीडियो कॉल मत काटिए। सुरक्षित खाते में पैसे भेजिए।",
            "label": "scam",
            "category": "digital_arrest",
            "tags": ["digital_arrest", "payment_request", "secrecy_pressure"],
            "language": "hi",
            "source": "curated_ncrb_cybercrime_patterns",
        },
        {
            "id": "da_004",
            "content": "Customs department: illegal parcel in your name. Pay penalty now or face legal action. Share OTP for verification.",
            "label": "scam",
            "category": "parcel_scam",
            "tags": ["authority_impersonation", "payment_request", "credential_theft"],
            "language": "en",
            "source": "curated_cybercrime_gov_in",
        },
        {
            "id": "da_005",
            "content": "Your SBI KYC expired. Click link to update or account will be blocked within 2 hours.",
            "label": "scam",
            "category": "phishing",
            "tags": ["urgency_threat", "credential_theft"],
            "language": "en",
            "source": "curated_phishing_corpus",
        },
        {
            "id": "da_006",
            "content": "Congratulations! You won lottery. Pay processing fee to claim prize.",
            "label": "scam",
            "category": "lottery_fraud",
            "tags": ["payment_request", "urgency_threat"],
            "language": "en",
            "source": "curated_phishing_corpus",
        },
        {
            "id": "benign_001",
            "content": "Your OTP for login is 482910. Valid for 10 minutes. Do not share with anyone.",
            "label": "benign",
            "category": "legitimate_otp",
            "tags": [],
            "language": "en",
            "source": "synthetic_benign",
        },
        {
            "id": "benign_002",
            "content": "Meeting rescheduled to tomorrow 4 PM at the office. Please confirm.",
            "label": "benign",
            "category": "personal",
            "tags": [],
            "language": "en",
            "source": "synthetic_benign",
        },
    ]
    path = PROCESSED / "digital_arrest_corpus.json"
    PROCESSED.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s (%d samples)", path, len(corpus))


def write_phishing_patterns() -> None:
    """Phishing indicators derived from public phishing corpora research."""
    patterns = {
        "source": "https://monkey.org/~jose/wiki/doku.php?id=PhishingCorpus",
        "url_indicators": [
            r"bit\.ly/",
            r"tinyurl\.com/",
            r"secure-update",
            r"verify-account",
            r"login-confirm",
        ],
        "text_indicators": [
            r"click (?:here|below|link)",
            r"verify your account",
            r"account (?:suspended|blocked|locked)",
            r"confirm your identity",
            r"unusual (?:activity|sign.?in)",
            r"update your (?:kyc|pan|aadhaar)",
        ],
        "sender_spoofing": [
            r"support@.*(?:bank|paytm|phonepe|gpay)",
            r"noreply@.*gov",
            r"cbi@",
            r"ed\.gov",
        ],
    }
    path = REFERENCE / "phishing_patterns.json"
    path.write_text(json.dumps(patterns, indent=2), encoding="utf-8")
    logger.info("Wrote %s", path)


def write_fraud_network_seed() -> None:
    """Expanded fraud network inspired by IEEE-CIS / credit-card fraud graph patterns."""
    graph = {
        "source": "Inspired by IEEE-CIS Fraud Detection & ULB credit card fraud datasets",
        "source_urls": [
            "https://www.kaggle.com/datasets/lnasiri007/ieeecis-fraud-detection",
            "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        ],
        "nodes": [
            {"id": "victim_1", "type": "victim", "district": "New Delhi"},
            {"id": "victim_2", "type": "victim", "district": "Mumbai"},
            {"id": "victim_3", "type": "victim", "district": "Bengaluru"},
            {"id": "phone_9198", "type": "phone", "spoofed": True},
            {"id": "phone_9187", "type": "phone", "spoofed": True},
            {"id": "upi_mule_1", "type": "account", "channel": "upi"},
            {"id": "upi_mule_2", "type": "account", "channel": "upi"},
            {"id": "bank_ac_1", "type": "bank", "ifsc": "XXXX0001234"},
            {"id": "bank_ac_2", "type": "bank", "ifsc": "XXXX0005678"},
            {"id": "device_a", "type": "device", "fingerprint": "dev_hash_1"},
            {"id": "device_b", "type": "device", "fingerprint": "dev_hash_2"},
            {"id": "mastermind", "type": "scammer", "role": "coordinator"},
        ],
        "edges": [
            {"source": "victim_1", "target": "phone_9198", "type": "called_by"},
            {"source": "victim_2", "target": "phone_9198", "type": "called_by"},
            {"source": "victim_3", "target": "phone_9187", "type": "called_by"},
            {"source": "phone_9198", "target": "upi_mule_1", "type": "payment_to"},
            {"source": "phone_9187", "target": "upi_mule_2", "type": "payment_to"},
            {"source": "upi_mule_1", "target": "bank_ac_1", "type": "transfer"},
            {"source": "upi_mule_2", "target": "bank_ac_2", "type": "transfer"},
            {"source": "device_a", "target": "upi_mule_1", "type": "operated_from"},
            {"source": "device_b", "target": "upi_mule_2", "type": "operated_from"},
            {"source": "mastermind", "target": "phone_9198", "type": "controls"},
            {"source": "mastermind", "target": "phone_9187", "type": "controls"},
            {"source": "mastermind", "target": "device_a", "type": "controls"},
        ],
    }
    path = DATASETS / "fraud_network.json"
    path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    logger.info("Wrote %s", path)


def process_uci_sms(sms_file: Path) -> None:
    """Merge UCI SMS spam into unified scam training set."""
    digital_arrest_path = PROCESSED / "digital_arrest_corpus.json"
    digital_arrest = json.loads(digital_arrest_path.read_text(encoding="utf-8"))

    merged: list[dict] = list(digital_arrest)
    if sms_file.exists():
        with sms_file.open(encoding="utf-8") as handle:
            for line_num, line in enumerate(handle, start=1):
                line = line.strip()
                if not line or "\t" not in line:
                    continue
                label_raw, text = line.split("\t", 1)
                is_spam = label_raw.lower() == "spam"
                merged.append(
                    {
                        "id": f"uci_sms_{line_num}",
                        "content": text,
                        "label": "scam" if is_spam else "benign",
                        "category": "sms_spam" if is_spam else "sms_ham",
                        "tags": ["uci_spam"] if is_spam else [],
                        "language": "en",
                        "source": "https://archive.ics.uci.edu/dataset/228/sms+spam+collection",
                    }
                )
        logger.info("Merged UCI SMS samples from %s", sms_file)

    out_path = DATASETS / "scam_transcripts.json"
    out_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote unified scam dataset: %s (%d samples)", out_path, len(merged))

    scam_count = sum(1 for s in merged if s["label"] == "scam")
    benign_count = len(merged) - scam_count
    stats = {
        "total": len(merged),
        "scam": scam_count,
        "benign": benign_count,
        "sources": sorted({s.get("source", "unknown") for s in merged}),
    }
    (PROCESSED / "dataset_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    sms_file = download_uci_sms()
    download_geojson()
    write_rbi_reference()
    write_digital_arrest_corpus()
    write_phishing_patterns()
    write_fraud_network_seed()
    process_uci_sms(sms_file)
    logger.info("Dataset download and processing complete.")


if __name__ == "__main__":
    main()
