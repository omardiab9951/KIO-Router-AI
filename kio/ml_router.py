"""Traditional scikit-learn router for Agent KIO."""

import json
import time
from pathlib import Path

import joblib

from .base import BaseRouter, RouterOutput
from .config import ML_MODEL_PATH
from .validation import validate_output


class MLRouter(BaseRouter):
    """Route messages with the frozen TF-IDF/logistic-regression pipeline."""

    def __init__(self, model_path=None):
        self.model_path = Path(model_path) if model_path else ML_MODEL_PATH
        self.name = "scikit-learn"
        self._model = None

    def _load_model(self):
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"ML model not found: {self.model_path}")
            self._model = joblib.load(self.model_path)
        return self._model

    def predict(self, message: str) -> RouterOutput:
        started = time.perf_counter()
        if not isinstance(message, str) or not message.strip():
            return RouterOutput("invalid", None, None, "", (time.perf_counter() - started) * 1000,
                                "empty_message", self.name)
        try:
            model = self._load_model()
            predicted = model.predict([message])[0]
            probabilities = model.predict_proba([message])[0]
            classes = list(model.classes_)
            probability_map = {str(label).strip().lower(): float(value)
                               for label, value in zip(classes, probabilities)}
            normalized = str(predicted).strip().lower()
            aliases = {"0": "support", "support": "support", "1": "sales", "sales": "sales"}
            label = aliases.get(normalized)
            if label is None or not all(key in probability_map for key in ("support", "sales")):
                return RouterOutput("invalid", None, None, json.dumps(probability_map),
                                    (time.perf_counter() - started) * 1000,
                                    "unexpected_model_output", self.name)
            output = validate_output(label, self.name, (time.perf_counter() - started) * 1000)
            output.confidence = probability_map[label]
            output.raw = json.dumps({"label": label, "probabilities": probability_map}, sort_keys=True)
            return output
        except FileNotFoundError as exc:
            return RouterOutput("invalid", None, None, "", (time.perf_counter() - started) * 1000,
                                f"missing_model: {exc}", self.name)
        except Exception as exc:
            return RouterOutput("invalid", None, None, "", (time.perf_counter() - started) * 1000,
                                f"model_error_{type(exc).__name__}: {exc}", self.name)
