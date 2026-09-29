import random
from pathlib import Path

import pandas as pd


OUTPUT_PATH = Path(__file__).resolve().parent / "training_data.csv"

random.seed(42)


def calculate_risk(
    temperature: float,
    pressure: float,
    vibration: str,
) -> str:
    score = 0

    if temperature >= 85:
        score += 2
    elif temperature >= 70:
        score += 1

    if pressure >= 120:
        score += 2
    elif pressure >= 105:
        score += 1

    if vibration == "High":
        score += 2
    elif vibration == "Medium":
        score += 1

    if score >= 4:
        return "High"
    elif score >= 2:
        return "Medium"

    return "Low"


def generate_training_data(rows: int = 600):
    records = []

    vibration_levels = [
        "Low",
        "Medium",
        "High",
    ]

    for _ in range(rows):
        temperature = round(
            random.uniform(45, 105),
            2,
        )

        pressure = round(
            random.uniform(70, 145),
            2,
        )

        vibration = random.choice(
            vibration_levels
        )

        risk = calculate_risk(
            temperature,
            pressure,
            vibration,
        )

        records.append(
            {
                "temperature": temperature,
                "pressure": pressure,
                "vibration": vibration,
                "risk": risk,
            }
        )

    dataframe = pd.DataFrame(records)
    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Generated {len(dataframe)} training rows."
    )
    print(
        f"Saved training data to: {OUTPUT_PATH}"
    )
    print()
    print("Risk distribution:")
    print(
        dataframe["risk"].value_counts()
    )


if __name__ == "__main__":
    generate_training_data()