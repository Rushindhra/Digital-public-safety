"""Explainable OpenCV screening for Indian currency-note photographs.

This is a screening model, not forensic authentication. It measures visible
proxies for note security features and deliberately lowers confidence when
image quality is poor. A calibrated classifier can replace the scoring layer
later without changing the API contract.
"""
import base64
import json
from pathlib import Path

import cv2
import numpy as np

from app.ml.rbi_reference import expected_aspect_ratio, get_denomination_spec
from app.schemas.counterfeit import CounterfeitAnalysis, Denomination, SecurityFeature


class InvalidNoteImage(ValueError):
    """Raised when bytes cannot be safely analysed as a note image."""


def decode_image(content: bytes) -> np.ndarray:
    if not content:
        raise InvalidNoteImage("The uploaded file is empty")
    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidNoteImage("The file is not a supported or valid image")
    height, width = image.shape[:2]
    if height < 160 or width < 320:
        raise InvalidNoteImage("Image resolution must be at least 320x160 pixels")
    return image


def _feature(name: str, score: float, explanation: str) -> SecurityFeature:
    score = float(np.clip(score, 0, 1))
    return SecurityFeature(
        name=name, score=round(score, 3), detected=score >= 0.45,
        explanation=explanation,
    )


def analyse_note(content: bytes, denomination: Denomination) -> CounterfeitAnalysis:
    image = decode_image(content)
    normalized = cv2.resize(image, (1000, 450), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(normalized, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(normalized, cv2.COLOR_BGR2HSV)

    sharpness = min(cv2.Laplacian(gray, cv2.CV_64F).var() / 500.0, 1.0)
    contrast = min(float(gray.std()) / 64.0, 1.0)

    # Security-thread proxy: a strong, narrow vertical structure near centre.
    vertical = cv2.morphologyEx(
        gray, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 91))
    )
    thread_band = vertical[:, 350:650]
    thread_score = min(float(np.percentile(thread_band, 99)) / 100.0, 1.0)

    # Fine high-frequency detail is a proxy for microprinting and bleed lines.
    edges = cv2.Canny(gray, 80, 180)
    micro_score = min(float(edges.mean()) / 35.0, 1.0) * sharpness
    side_edges = np.concatenate((edges[:, :100].ravel(), edges[:, -100:].ravel()))
    bleed_score = min(float(side_edges.mean()) / 30.0, 1.0) * sharpness

    # Low-gradient, locally contrasted region approximates a visible watermark.
    watermark_roi = gray[70:380, 80:360]
    watermark_score = min(float(watermark_roi.std()) / 55.0, 1.0) * contrast

    # Saturated colour diversity is a proxy for optically variable ink.
    saturation = hsv[:, :, 1]
    ovi_score = min(float(np.percentile(saturation, 90)) / 150.0, 1.0)

    # OCR is intentionally not claimed; digit-like contours estimate serial visibility.
    serial_roi = gray[280:430, 420:970]
    binary = cv2.threshold(serial_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    digit_like = sum(1 for c in contours if 8 <= cv2.boundingRect(c)[2] <= 55 and 18 <= cv2.boundingRect(c)[3] <= 90)
    serial_score = min(digit_like / 8.0, 1.0) * sharpness

    features = [
        _feature("security_thread", thread_score, "Vertical security-thread pattern strength"),
        _feature("microprinting", micro_score, "Fine-print edge density and image sharpness"),
        _feature("watermark", watermark_score, "Watermark-region tonal variation"),
        _feature("serial_number", serial_score, "Serial-region character-like structures"),
        _feature("optically_variable_ink", ovi_score, "Colour and saturation variation"),
        _feature("bleed_lines", bleed_score, "Fine line density along note edges"),
    ]
    authenticity = sum(f.score for f in features) / len(features)
    quality = 0.6 * sharpness + 0.4 * contrast
    probability = float(np.clip(1.0 - authenticity, 0.02, 0.98))
    confidence = float(np.clip(0.35 + 0.6 * quality, 0.35, 0.95))

    heat = cv2.applyColorMap(cv2.GaussianBlur(edges, (0, 0), 7), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(normalized, 0.68, heat, 0.32, 0)
    ok, encoded = cv2.imencode(".png", overlay)
    if not ok:
        raise InvalidNoteImage("Could not generate the analysis visualization")

    warnings: list[str] = []
    if quality < 0.45:
        warnings.append(
            "Low image quality reduced confidence; use bright, even lighting and hold the camera steady."
        )

    spec = get_denomination_spec(int(denomination))
    if spec:
        expected_ratio = expected_aspect_ratio(int(denomination))
        if expected_ratio:
            actual_ratio = normalized.shape[1] / normalized.shape[0]
            if abs(actual_ratio - expected_ratio) > 0.35:
                warnings.append(
                    f"Image aspect ratio ({actual_ratio:.2f}) differs from RBI "
                    f"{denomination} note specification ({expected_ratio:.2f}). "
                    "Ensure the full note is captured flat."
                )
        expected_features = spec.get("security_features", [])
        detected_count = sum(1 for f in features if f.detected)
        if expected_features and detected_count < len(expected_features) // 2:
            warnings.append(
                f"Only {detected_count}/{len(features)} visible security proxies detected; "
                f"RBI {denomination} notes include: {', '.join(expected_features[:4])}..."
            )

    warnings.append("This automated screening result is not a legal or forensic determination.")
    verdict = "high_risk" if probability >= 0.65 else "review" if probability >= 0.4 else "likely_genuine"
    return CounterfeitAnalysis(
        denomination=denomination,
        counterfeit_probability=round(probability, 3), confidence=round(confidence, 3),
        verdict=verdict, features=features, warnings=warnings,
        heatmap_png_base64=base64.b64encode(encoded.tobytes()).decode("ascii"),
    )

