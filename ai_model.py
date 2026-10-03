from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "random_forest_model.pkl"
FEATURE_NAMES = [
    "cyclomatic_complexity",
    "code_duplication",
    "unused_variables",
    "max_nesting",
    "avg_function_length",
    "long_functions",
    "lines_of_code",
    "functions",
    "classes",
]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("AI model not found. Run: python train_model.py")
    return joblib.load(MODEL_PATH)


def predict(features):
    model = load_model()
    row = [[features[name] for name in FEATURE_NAMES]]
    prediction = int(model.predict(row)[0])
    probability = None
    if hasattr(model, "predict_proba"):
        probability = float(max(model.predict_proba(row)[0]))
    return {
        "label": "Healthy" if prediction == 0 else "Potentially Problematic",
        "class": prediction,
        "confidence": round(probability * 100, 1) if probability is not None else None,
    }
