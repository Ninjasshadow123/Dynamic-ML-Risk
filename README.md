# Dynamic Machine Risk Management

A simple full-stack web application for managing dynamic machine information and predicting machine risk using a locally trained Python machine learning model.

The application allows users to configure machine fields at runtime, create and manage machine records using those fields, and classify machine risk as **Low**, **Medium**, or **High**.

## Features

### Dynamic Field Configuration

Users can configure machine fields without modifying the database schema or application code.

Supported field types:

- Text
- Number
- Dropdown

Each field can be configured as required or optional. Dropdown fields support configurable options.

The initial fields are:

- Machine Name
- Temperature
- Pressure
- Vibration

Additional fields can be created through the web interface.

### Machine Management

The application dynamically generates the machine data-entry form from the configured fields.

Users can:

- Create machine records
- View stored machines
- Edit machine records
- Delete machine records

Newly configured fields automatically appear in the machine form and machine records table.

### Risk Prediction

A locally trained Python machine learning model predicts machine risk as:

- Low
- Medium
- High

The current model uses:

- Temperature
- Pressure
- Vibration

No external AI or cloud-based prediction API is used.

---

## Technology Stack

### Frontend

- React
- Vite
- React Router
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Database

- SQLite

### Machine Learning

- scikit-learn
- pandas
- joblib
- Decision Tree classifier

---

## Architecture

The application uses a simple full-stack architecture:

```text
React Web UI
     |
     | HTTP / JSON
     v
FastAPI Backend
     |
     +--------------------+
     |                    |
     v                    v
SQLite Database      Local ML Model
     |                    |
     |                    |
Machine Data         Risk Prediction
     |                    |
     +---------+----------+
               |
               v
          FastAPI Response
               |
               v
           React Web UI
```

The machine learning model is integrated into the FastAPI application and runs locally. A separate ML server is not required.

---

## Repository Structure

```text
Dynamic-ML-Risk/
|
|-- backend/
|   |-- app/
|   |   |-- models/
|   |   |-- routers/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- database.py
|   |   `-- main.py
|   |
|   |-- ml/
|   |   |-- generate_data.py
|   |   |-- train_model.py
|   |   |-- training_data.csv
|   |   `-- risk_model.joblib
|   |
|   `-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- App.jsx
|   |   |-- index.css
|   |   `-- main.jsx
|   |
|   |-- package.json
|   `-- vite.config.js
|
|-- .gitignore
`-- README.md
```

---

## Prerequisites

Install:

- Python 3
- Node.js
- npm
- Git

The project was developed and tested using Python 3.13 and Node.js 24.

---

## Backend Setup

From the repository root:

```bash
cd backend
```

Create a Python virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

A SQLite database is created automatically when the backend starts.

The runtime database file is intentionally excluded from Git.

---

## Frontend Setup

Open another terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at:

```text
http://localhost:5173
```

Keep both the FastAPI backend and React frontend running while using the application.

---

## Running the Machine Learning Component

A trained local model is included in:

```text
backend/ml/risk_model.joblib
```

Therefore, normal application startup does not require retraining the model.

The FastAPI backend loads this saved model when a prediction is requested.

### Regenerating the Synthetic Training Data

From the `backend` directory:

```bash
python -m ml.generate_data
```

This generates:

```text
ml/training_data.csv
```

### Retraining the Model

After generating the training data:

```bash
python -m ml.train_model
```

This trains the model and writes:

```text
ml/risk_model.joblib
```

The training script also prints evaluation information for the trained classifier.

The generated data is synthetic and is intended only to demonstrate the complete machine-learning workflow. It is not intended to represent a production predictive-maintenance dataset.

---

## Machine Learning Approach

The application demonstrates supervised multiclass classification.

The model uses three input features:

```text
Temperature
Pressure
Vibration
```

and predicts one of three classes:

```text
Low
Medium
High
```

Synthetic training data is generated locally with combinations of temperature, pressure, and vibration conditions.

The preprocessing and Decision Tree classifier are stored together in a scikit-learn pipeline and persisted using `joblib`.

During prediction:

1. The user selects a machine in the web interface.
2. React sends the machine ID to FastAPI.
3. FastAPI retrieves the machine's dynamic values from SQLite.
4. The backend extracts Temperature, Pressure, and Vibration using their stable field keys.
5. These values are passed to the saved local ML pipeline.
6. The model predicts Low, Medium, or High risk.
7. FastAPI returns the result to the React interface.

---

## Dynamic Field Design

Machine fields are not implemented as dedicated database columns such as:

```text
temperature
pressure
vibration
humidity
```

Instead, the application stores field definitions separately from machine values.

Conceptually, the database contains:

```text
machines
machine_fields
machine_field_values
```

`machine_fields` stores configuration such as:

- Field name
- Stable field key
- Field type
- Required/optional status
- Dropdown options

`machine_field_values` associates a machine with a configured field and its value.

This design means adding a new field does **not** require adding a new database column or running a schema migration.

---

## Dynamic Humidity Example

A useful way to demonstrate the dynamic-field behavior is to add **Humidity** after the application is running.

Open:

```text
Field Configuration
```

Create:

```text
Field Name: Humidity
Field Type: Number
Required: No
```

Then navigate to:

```text
Machine Records
```

Humidity will automatically appear in the machine form.

No frontend code modification, backend model modification, or database schema migration is required to store the new field.

This demonstrates that the machine-management portion of the application can adapt to newly configured fields.

---

## Does the Existing ML Model Use Humidity?

No.

The current trained model intentionally continues to use only:

```text
Temperature
Pressure
Vibration
```

Humidity can still be configured, entered, stored, retrieved, edited, and displayed by the application, but it is not automatically passed into the existing model.

This separates two concerns:

1. **Dynamic application data** — new machine fields can be added at runtime.
2. **ML feature schema** — the trained model expects the features it was trained with.

Automatically retraining the model whenever a field is created is outside the scope of this implementation.

---

## How Humidity Could Be Used in a Future Model

To incorporate Humidity into a future version of the prediction model:

1. Collect or generate training data containing Humidity.
2. Add Humidity to the model's training features.
3. Update the preprocessing pipeline if required.
4. Retrain and evaluate the classifier.
5. Save the updated model artifact.
6. Update the prediction service to extract the stable `humidity` field key and pass it to the new model.

The dynamic database design itself would not need to change because Humidity is already stored using the generic field/value structure.

---

## API Overview

The FastAPI backend exposes endpoints for the three primary application areas.

### Field Configuration

```text
GET    /fields
POST   /fields
PUT    /fields/{field_id}
DELETE /fields/{field_id}
```

### Machine Records

```text
GET    /machines
GET    /machines/{machine_id}
POST   /machines
PUT    /machines/{machine_id}
DELETE /machines/{machine_id}
```

### Risk Prediction

```text
POST /predictions
```

Example request:

```json
{
  "machine_id": 1
}
```

Example response structure:

```json
{
  "machine_id": 1,
  "risk_level": "High",
  "features_used": {
    "temperature": 90,
    "pressure": 125,
    "vibration": "High"
  }
}
```

---

## Suggested Evaluation Flow

After starting the backend and frontend:

1. Open **Field Configuration**.
2. Confirm the initial Machine Name, Temperature, Pressure, and Vibration fields.
3. Add an optional Number field named **Humidity**.
4. Open **Machine Records** and confirm Humidity automatically appears.
5. Create a machine with values for all configured fields.
6. Edit the machine and confirm the changes persist.
7. Open **Risk Prediction**.
8. Select the machine and run the prediction.
9. Confirm the application displays Low, Medium, or High risk.
10. Observe that the model inputs contain Temperature, Pressure, and Vibration while Humidity remains stored as dynamic machine information.
11. Delete a machine to verify the complete CRUD flow.

---

## Design Decisions

### SQLite

SQLite keeps the assessment easy to run locally without requiring a separate database server.

### Generic Field/Value Storage

Separating field definitions from field values allows new machine attributes to be added without modifying the database schema for each field.

### Stable Field Keys

Fields have stable internal keys in addition to their display names. This allows application code such as the prediction service to identify model features reliably even if a display name changes.

### Local ML Pipeline

The prediction model is stored locally as a `joblib` artifact. No cloud AI service or external AI API is required.

### Synthetic Data

Synthetic data keeps the ML workflow reproducible and self-contained while demonstrating data generation, training, persistence, loading, and prediction.

---

## Notes

This project is intentionally scoped as a simple technical-assessment application. The focus is on demonstrating:

- Dynamic machine fields
- Machine CRUD operations
- Database persistence
- Local Python machine learning
- End-to-end prediction flow
- A clean, usable web interface

Production concerns such as authentication, authorization, deployment infrastructure, advanced model monitoring, and automatic model retraining are outside the scope of this implementation.