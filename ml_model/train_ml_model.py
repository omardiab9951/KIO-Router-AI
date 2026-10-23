"""Train the KIO model on training messages only.

TF-IDF turns words and word pairs into numbers; SVD compresses them to two
dimensions; polynomial features allow a curved boundary; scaling normalizes
features; logistic regression predicts the route.
"""

 # Project root is the parent of this file's folder.
 # Add it so imports work when launched from the System folder.
import sys

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold, cross_val_score

from kio.config import PROJECT_DIR, build_ml_pipeline
from kio.data import get_train

RANDOM_STATE = 42
C_VALUES = [0.1, 1, 10, 100]


def main():
    # Only get_train() is used. No held-out messages are loaded.
    frame = get_train()
    X, y, groups = frame["Message"], frame["Flag"], frame["Group_ID"]
    cv_name = "StratifiedGroupKFold"
    try:
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        folds = list(cv.split(X, y, groups))
    except Exception:
        cv_name = "GroupKFold"
        cv = GroupKFold(n_splits=5)
        folds = list(cv.split(X, y, groups))
    rows = []
    for C in C_VALUES:
        scores = cross_val_score(build_ml_pipeline(C), X, y, groups=groups, cv=folds, scoring="accuracy")
        rows.append({"C": C, "cv_accuracy": float(scores.mean()), "fold_scores": [float(x) for x in scores]})
    chosen = min(rows, key=lambda row: (-row["cv_accuracy"], row["C"]))
    model = build_ml_pipeline(chosen["C"]).fit(X, y)
    train_accuracy = float(accuracy_score(y, model.predict(X)))
    results_dir, models_dir = PROJECT_DIR / "results", PROJECT_DIR / "models"
    results_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    settings = {"C_values": C_VALUES, "chosen_C": chosen["C"], "cv": cv_name, "random_state": RANDOM_STATE,
                "cv_results": rows, "training_accuracy": train_accuracy,
                "cross_validated_accuracy": chosen["cv_accuracy"]}
    (results_dir / "ml_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    joblib.dump(model, models_dir / "ml_model.joblib")
    _save_boundary(model, X, y, results_dir / "ml_boundary_train.png")
    _save_top_terms(model, results_dir / "ml_top_terms.csv")
    print(json.dumps(settings, indent=2))
    print(f"saved model: {models_dir / 'ml_model.joblib'}")


def _save_boundary(model, X, y, path):
    """Draw the boundary in the two-dimensional SVD space."""
    transformed = model[:-3].transform(X)
    x_min, x_max = transformed[:, 0].min() - .5, transformed[:, 0].max() + .5
    y_min, y_max = transformed[:, 1].min() - .5, transformed[:, 1].max() + .5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 250), np.linspace(y_min, y_max, 250))
    grid = np.c_[xx.ravel(), yy.ravel()]
    scores = model[-3:].decision_function(grid).reshape(xx.shape)
    plt.figure(figsize=(8, 6))
    plt.contourf(xx, yy, scores, levels=20, alpha=.25, cmap="coolwarm")
    plt.contour(xx, yy, scores, levels=[0], colors="black")
    for value, label, color in [(0, "Support", "tab:blue"), (1, "Sales", "tab:orange")]:
        mask = y.to_numpy() == value
        plt.scatter(transformed[mask, 0], transformed[mask, 1], label=label, color=color, edgecolor="black")
    plt.xlabel("SVD component 1")
    plt.ylabel("SVD component 2")
    plt.title("ML decision boundary — training data only")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _save_top_terms(model, path):
    # Each word is mapped through SVD; a local gradient of the polynomial
    # logistic boundary gives a simple approximate word-importance score.
    tfidf, svd, poly, scale, logreg = model.named_steps.values()
    center = np.zeros((1, 2)); eps = 1e-5
    gradient = []
    for axis in range(2):
        shift = np.zeros((1, 2)); shift[0, axis] = eps
        hi = logreg.decision_function(scale.transform(poly.transform(center + shift)))[0]
        lo = logreg.decision_function(scale.transform(poly.transform(center - shift)))[0]
        gradient.append((hi - lo) / (2 * eps))
    scores = svd.components_.T @ np.array(gradient)
    terms = np.array(tfidf.get_feature_names_out())
    records = []
    for direction, name in [(1, "sales"), (-1, "support")]:
        for index in np.argsort(direction * scores)[-10:][::-1]:
            records.append({"class": name, "term": terms[index], "approximate_weight": float(direction * scores[index])})
    pd.DataFrame(records).to_csv(path, index=False)


if __name__ == "__main__":
    main()

