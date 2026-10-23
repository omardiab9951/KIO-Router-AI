"""Scikit-learn router backed by the saved training model."""

import time
from pathlib import Path

import joblib

from .base import BaseRouter, RouterOutput
from .validation import validate_output


class MLRouter(BaseRouter):
    name = "scikit-learn"

    def __init__(self, model_path=None):
        self.model_path = Path(model_path or Path(__file__).resolve().parent.parent / "models" / "ml_model.joblib")
        self._model = None

    def predict(self, message):
        started = time.perf_counter()
        if not self.model_path.is_file():
            return RouterOutput("invalid", None, None, "", 0.0, f"model_missing: {self.model_path}", self.name)
        if not isinstance(message, str) or not message.strip():
            return RouterOutput("invalid", None, None, "", 0.0, "empty_message", self.name)
        try:
            if self._model is None:
                self._model = joblib.load(self.model_path)
            probabilities = self._model.predict_proba([message])[0]
            index = int(probabilities.argmax())
            raw = str(self._model.classes_[index])
            output = validate_output(raw, self.name, (time.perf_counter() - started) * 1000)
            output.confidence = float(probabilities[index])
            output.raw = raw
            return output
        except Exception as exc:
            return RouterOutput("invalid", None, None, "", (time.perf_counter() - started) * 1000, f"prediction_error: {exc}", self.name)

