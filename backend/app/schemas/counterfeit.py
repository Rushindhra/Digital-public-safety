"""API contracts for explainable currency-note screening."""
from enum import IntEnum

from pydantic import BaseModel, Field


class Denomination(IntEnum):
    INR_100 = 100
    INR_200 = 200
    INR_500 = 500
    INR_2000 = 2000


class SecurityFeature(BaseModel):
    name: str
    score: float = Field(ge=0, le=1)
    detected: bool
    explanation: str


class CounterfeitAnalysis(BaseModel):
    denomination: Denomination
    counterfeit_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    verdict: str
    features: list[SecurityFeature]
    warnings: list[str]
    heatmap_png_base64: str
    model_version: str = "opencv-explainable-1.0"

