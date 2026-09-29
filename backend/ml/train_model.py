from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


ML_DIR = Path(__file__).resolve().parent

DATA_PATH = ML_DIR / "training_data.csv"
MODEL_PATH = ML_DIR / "risk_model.joblib"


def train_model():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "training_data.csv was not found. "
            "Run generate_data.py first."
        )

    dataframe = pd.read_csv(DATA_PATH)

    features = dataframe[
        [
            "temperature",
            "pressure",
            "vibration",
        ]
    ]

    target = dataframe["risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "vibration",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                ["vibration"],
            ),
        ],
        remainder="passthrough",
    )

    classifier = DecisionTreeClassifier(
        max_depth=6,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", classifier),
        ]
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print(
        f"Test accuracy: {accuracy:.3f}"
    )

    print()
    print("Classification report:")
    print(
        classification_report(
            y_test,
            predictions,
        )
    )

    joblib.dump(
        pipeline,
        MODEL_PATH,
    )

    print(
        f"Model saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    train_model()