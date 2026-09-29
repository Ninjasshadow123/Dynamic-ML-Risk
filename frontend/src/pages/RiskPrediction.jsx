import { useEffect, useState } from "react";

import {
  machineApi,
  predictionApi,
} from "../services/api";


function getMachineName(machine) {
  const nameField = machine.values.find(
    (value) => value.field_key === "machine_name"
  );

  return nameField
    ? nameField.value
    : `Machine #${machine.id}`;
}


function RiskPrediction() {
  const [machines, setMachines] = useState([]);
  const [selectedMachineId, setSelectedMachineId] = useState("");

  const [prediction, setPrediction] = useState(null);

  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);

  const [error, setError] = useState("");


  useEffect(() => {
    async function loadMachines() {
      try {
        setLoading(true);

        const data = await machineApi.getAll();
        setMachines(data);

        if (data.length > 0) {
          setSelectedMachineId(
            String(data[0].id)
          );
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadMachines();
  }, []);


  async function handlePrediction(event) {
    event.preventDefault();

    if (!selectedMachineId) {
      return;
    }

    try {
      setPredicting(true);
      setError("");
      setPrediction(null);

      const result = await predictionApi.predict(
        selectedMachineId
      );

      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setPredicting(false);
    }
  }


  const selectedMachine = machines.find(
    (machine) =>
      String(machine.id) === String(selectedMachineId)
  );


  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Local Machine Learning</p>
          <h2>Risk Prediction</h2>
          <p className="page-description">
            Select a stored machine and run the locally trained
            risk classification model.
          </p>
        </div>
      </div>

      {error && <div className="alert error-alert">{error}</div>}

      <div className="prediction-layout">
        <section className="card">
          <div className="card-header">
            <div>
              <h3>Run Prediction</h3>
              <p>
                The current model uses Temperature,
                Pressure, and Vibration.
              </p>
            </div>
          </div>

          {loading ? (
            <p className="muted">Loading machines...</p>
          ) : machines.length === 0 ? (
            <div className="empty-state">
              Create a machine before running a prediction.
            </div>
          ) : (
            <form
              onSubmit={handlePrediction}
              className="form-stack"
            >
              <div className="form-group">
                <label htmlFor="machine-select">
                  Machine
                </label>

                <select
                  id="machine-select"
                  value={selectedMachineId}
                  onChange={(event) => {
                    setSelectedMachineId(
                      event.target.value
                    );

                    setPrediction(null);
                  }}
                >
                  {machines.map((machine) => (
                    <option
                      key={machine.id}
                      value={machine.id}
                    >
                      {getMachineName(machine)}
                      {" — "}
                      #{machine.id}
                    </option>
                  ))}
                </select>
              </div>

              {selectedMachine && (
                <div className="machine-summary">
                  {selectedMachine.values.map((item) => (
                    <div
                      className="summary-row"
                      key={item.field_id}
                    >
                      <span>{item.field_name}</span>
                      <strong>{item.value}</strong>
                    </div>
                  ))}
                </div>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={predicting}
              >
                {predicting
                  ? "Running Model..."
                  : "Predict Risk"}
              </button>
            </form>
          )}
        </section>

        <section className="card prediction-result-card">
          <div className="card-header">
            <div>
              <h3>Prediction Result</h3>
              <p>
                Output from the local Python ML model.
              </p>
            </div>
          </div>

          {!prediction ? (
            <div className="prediction-placeholder">
              <div className="prediction-icon">ML</div>

              <p>
                Select a machine and run the model to
                display its risk level.
              </p>
            </div>
          ) : (
            <div className="prediction-result">
              <p className="result-label">
                Predicted Risk
              </p>

              <div
                className={`risk-result risk-${prediction.risk_level.toLowerCase()}`}
              >
                {prediction.risk_level} Risk
              </div>

              <div className="features-used">
                <h4>Model Inputs</h4>

                <div className="summary-row">
                  <span>Temperature</span>
                  <strong>
                    {prediction.features_used.temperature}
                  </strong>
                </div>

                <div className="summary-row">
                  <span>Pressure</span>
                  <strong>
                    {prediction.features_used.pressure}
                  </strong>
                </div>

                <div className="summary-row">
                  <span>Vibration</span>
                  <strong>
                    {prediction.features_used.vibration}
                  </strong>
                </div>
              </div>

              <p className="model-note">
                Additional dynamic fields such as Humidity
                are stored by the application but are not
                inputs to the current trained model.
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}


export default RiskPrediction;