
"""Traditional ML pipeline for the KIO message router."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def build_ml_pipeline(C=1.0):
    """Build the text-classification pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "logreg",
                LogisticRegression(
                    C=C,
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )

