from pathlib import Path
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
DATASET = BASE_DIR / "dataset" / "code_health_dataset.csv"
MODEL_PATH = BASE_DIR / "model" / "random_forest_model.pkl"
FEATURE_NAMES = [
    "cyclomatic_complexity", "code_duplication", "unused_variables", "max_nesting",
    "avg_function_length", "long_functions", "lines_of_code", "functions", "classes"
]


def main():
    df = pd.read_csv(DATASET)
    X = df[FEATURE_NAMES]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
    }
    joblib.dump(model, MODEL_PATH)
    print("Model saved:", MODEL_PATH)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
    print("\nClassification report:\n", classification_report(y_test, pred, zero_division=0))


if __name__ == "__main__":
    main()
