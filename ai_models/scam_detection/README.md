# Scam Detection Model

Rule-based multilingual NLP engine with weighted pattern matching for digital-arrest and payment fraud signals.

## Files

- `training.py` — builds pattern-weight artifact from `datasets/scam_transcripts.json`
- `predict.py` — calls backend `app.ml.scam.analyse_scam`
- `utils.py` — dataset and artifact helpers

## Usage

```powershell
cd ai_models/scam_detection
python training.py
python predict.py
```
