import cv2
import numpy as np
import pytest

from app.ml.counterfeit import InvalidNoteImage, analyse_note
from app.schemas.counterfeit import Denomination


def test_rejects_non_image_bytes():
    with pytest.raises(InvalidNoteImage):
        analyse_note(b"not-an-image", Denomination.INR_500)


def test_analysis_contract_for_valid_image():
    image = np.full((450, 1000, 3), 210, dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (980, 430), (60, 110, 160), 5)
    cv2.line(image, (500, 20), (500, 430), (10, 10, 10), 8)
    cv2.putText(image, "500 ABC123456", (360, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (20, 20, 20), 4)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    result = analyse_note(encoded.tobytes(), Denomination.INR_500)
    assert result.denomination == 500
    assert 0 <= result.counterfeit_probability <= 1
    assert len(result.features) == 6
    assert result.heatmap_png_base64
