import { useEffect, useMemo, useState } from "react";

import { fieldApi, machineApi } from "../services/api";


function createInitialValues(fields, machine = null) {
  const values = {};

  for (const field of fields) {
    values[field.id] = "";

    if (machine) {
      const existingValue = machine.values.find(
        (item) => item.field_id === field.id
      );

      if (existingValue) {
        values[field.id] = existingValue.value;
      }
    }
  }

  return values;
}


function Machines() {
  const [fields, setFields] = useState([]);
  const [machines, setMachines] = useState([]);

  const [formValues, setFormValues] = useState({});
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  async function loadData() {
    try {
      setLoading(true);
      setError("");

      const [fieldData, machineData] = await Promise.all([
        fieldApi.getAll(),
        machineApi.getAll(),
      ]);

      setFields(fieldData);
      setMachines(machineData);

      if (!editingId) {
        setFormValues(
          createInitialValues(fieldData)
        );
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  const tableFields = useMemo(
    () => fields,
    [fields]
  );


  function resetForm() {
    setEditingId(null);
    setFormValues(
      createInitialValues(fields)
    );
  }


  function startEdit(machine) {
    setEditingId(machine.id);

    setFormValues(
      createInitialValues(
        fields,
        machine
      )
    );

    setError("");
    setMessage("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }


  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setMessage("");

    const values = fields
      .map((field) => ({
        field_id: field.id,
        value: formValues[field.id],
      }))
      .filter((item) => {
        return (
          item.value !== "" &&
          item.value !== null &&
          item.value !== undefined
        );
      });

    try {
      if (editingId) {
        await machineApi.update(editingId, {
          values,
        });

        setMessage("Machine updated successfully.");
      } else {
        await machineApi.create({
          values,
        });

        setMessage("Machine created successfully.");
      }

      setEditingId(null);

      const machineData = await machineApi.getAll();
      setMachines(machineData);

      setFormValues(
        createInitialValues(fields)
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(machineId) {
    const confirmed = window.confirm(
      `Delete machine #${machineId}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setMessage("");

      await machineApi.delete(machineId);

      if (editingId === machineId) {
        resetForm();
      }

      setMessage("Machine deleted successfully.");

      const machineData = await machineApi.getAll();
      setMachines(machineData);
    } catch (err) {
      setError(err.message);
    }
  }


  function getMachineValue(machine, fieldId) {
    const item = machine.values.find(
      (value) => value.field_id === fieldId
    );

    return item ? item.value : "—";
  }


  if (loading) {
    return (
      <div className="page">
        <p className="muted">Loading machine data...</p>
      </div>
    );
  }


  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Data Management</p>
          <h2>Machine Records</h2>
          <p className="page-description">
            Create and maintain machines using the currently
            configured dynamic fields.
          </p>
        </div>
      </div>

      {error && <div className="alert error-alert">{error}</div>}
      {message && <div className="alert success-alert">{message}</div>}

      <section className="card machine-form-card">
        <div className="card-header">
          <div>
            <h3>
              {editingId
                ? `Edit Machine #${editingId}`
                : "Add Machine"}
            </h3>

            <p>
              This form is generated from the field configuration.
            </p>
          </div>
        </div>

        {fields.length === 0 ? (
          <div className="empty-state">
            Configure at least one machine field before
            creating records.
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="dynamic-form-grid">
              {fields.map((field) => (
                <div
                  className="form-group"
                  key={field.id}
                >
                  <label htmlFor={`machine-field-${field.id}`}>
                    {field.name}

                    {field.required && (
                      <span className="required-star">*</span>
                    )}
                  </label>

                  {field.field_type === "dropdown" ? (
                    <select
                      id={`machine-field-${field.id}`}
                      required={field.required}
                      value={formValues[field.id] ?? ""}
                      onChange={(event) =>
                        setFormValues({
                          ...formValues,
                          [field.id]: event.target.value,
                        })
                      }
                    >
                      <option value="">
                        Select {field.name}
                      </option>

                      {(field.options || []).map((option) => (
                        <option
                          key={option}
                          value={option}
                        >
                          {option}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      id={`machine-field-${field.id}`}
                      type={
                        field.field_type === "number"
                          ? "number"
                          : "text"
                      }
                      step={
                        field.field_type === "number"
                          ? "any"
                          : undefined
                      }
                      required={field.required}
                      value={formValues[field.id] ?? ""}
                      onChange={(event) =>
                        setFormValues({
                          ...formValues,
                          [field.id]: event.target.value,
                        })
                      }
                    />
                  )}
                </div>
              ))}
            </div>

            <div className="form-actions">
              <button
                className="primary-button"
                type="submit"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                    ? "Save Changes"
                    : "Create Machine"}
              </button>

              {editingId && (
                <button
                  className="secondary-button"
                  type="button"
                  onClick={resetForm}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        )}
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <h3>Stored Machines</h3>
            <p>{machines.length} machine(s) stored.</p>
          </div>
        </div>

        {machines.length === 0 ? (
          <div className="empty-state">
            No machine records exist yet.
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>

                  {tableFields.map((field) => (
                    <th key={field.id}>
                      {field.name}
                    </th>
                  ))}

                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {machines.map((machine) => (
                  <tr key={machine.id}>
                    <td>#{machine.id}</td>

                    {tableFields.map((field) => (
                      <td key={field.id}>
                        {getMachineValue(
                          machine,
                          field.id
                        )}
                      </td>
                    ))}

                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className="text-button"
                          onClick={() =>
                            startEdit(machine)
                          }
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          className="text-button danger-text"
                          onClick={() =>
                            handleDelete(machine.id)
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}


export default Machines;