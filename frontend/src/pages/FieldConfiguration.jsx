import { useEffect, useState } from "react";

import { fieldApi } from "../services/api";


const emptyForm = {
  name: "",
  field_type: "text",
  required: false,
  options: "",
};


function FieldConfiguration() {
  const [fields, setFields] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  async function loadFields() {
    try {
      setLoading(true);
      setError("");

      const data = await fieldApi.getAll();
      setFields(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadFields();
  }, []);


  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }


  function handleEdit(field) {
    setEditingId(field.id);

    setForm({
      name: field.name,
      field_type: field.field_type,
      required: field.required,
      options: field.options
        ? field.options.join(", ")
        : "",
    });

    setError("");
    setMessage("");
  }


  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setMessage("");

    const payload = {
      name: form.name.trim(),
      field_type: form.field_type,
      required: form.required,
      options:
        form.field_type === "dropdown"
          ? form.options
              .split(",")
              .map((option) => option.trim())
              .filter(Boolean)
          : null,
    };

    try {
      if (editingId) {
        await fieldApi.update(editingId, payload);
        setMessage("Field updated successfully.");
      } else {
        await fieldApi.create(payload);
        setMessage("Field added successfully.");
      }

      resetForm();
      await loadFields();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(field) {
    const confirmed = window.confirm(
      `Delete "${field.name}"? Existing values for this field will also be removed.`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setMessage("");

      await fieldApi.delete(field.id);

      if (editingId === field.id) {
        resetForm();
      }

      setMessage("Field deleted successfully.");
      await loadFields();
    } catch (err) {
      setError(err.message);
    }
  }


  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Configuration</p>
          <h2>Machine Fields</h2>
          <p className="page-description">
            Configure the fields used to describe machine records.
            New fields become available without changing the database schema.
          </p>
        </div>
      </div>

      {error && <div className="alert error-alert">{error}</div>}
      {message && <div className="alert success-alert">{message}</div>}

      <div className="two-column-grid">
        <section className="card">
          <div className="card-header">
            <div>
              <h3>
                {editingId ? "Edit Field" : "Add Field"}
              </h3>
              <p>
                Text, numeric, and dropdown fields are supported.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="form-stack">
            <div className="form-group">
              <label htmlFor="field-name">Field Name</label>

              <input
                id="field-name"
                type="text"
                value={form.name}
                placeholder="e.g. Humidity"
                required
                onChange={(event) =>
                  setForm({
                    ...form,
                    name: event.target.value,
                  })
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="field-type">Field Type</label>

              <select
                id="field-type"
                value={form.field_type}
                onChange={(event) =>
                  setForm({
                    ...form,
                    field_type: event.target.value,
                    options:
                      event.target.value === "dropdown"
                        ? form.options
                        : "",
                  })
                }
              >
                <option value="text">Text</option>
                <option value="number">Number</option>
                <option value="dropdown">Dropdown</option>
              </select>
            </div>

            {form.field_type === "dropdown" && (
              <div className="form-group">
                <label htmlFor="options">
                  Dropdown Options
                </label>

                <input
                  id="options"
                  type="text"
                  value={form.options}
                  placeholder="Low, Medium, High"
                  onChange={(event) =>
                    setForm({
                      ...form,
                      options: event.target.value,
                    })
                  }
                />

                <span className="field-help">
                  Separate options with commas.
                </span>
              </div>
            )}

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={form.required}
                onChange={(event) =>
                  setForm({
                    ...form,
                    required: event.target.checked,
                  })
                }
              />

              <span>Required field</span>
            </label>

            <div className="form-actions">
              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : editingId
                    ? "Save Changes"
                    : "Add Field"}
              </button>

              {editingId && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={resetForm}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </section>

        <section className="card">
          <div className="card-header">
            <div>
              <h3>Configured Fields</h3>
              <p>{fields.length} field(s) currently configured.</p>
            </div>
          </div>

          {loading ? (
            <p className="muted">Loading fields...</p>
          ) : fields.length === 0 ? (
            <div className="empty-state">
              No fields have been configured.
            </div>
          ) : (
            <div className="field-list">
              {fields.map((field) => (
                <div className="field-item" key={field.id}>
                  <div className="field-item-main">
                    <div className="field-title-row">
                      <strong>{field.name}</strong>

                      {field.required && (
                        <span className="badge required-badge">
                          Required
                        </span>
                      )}
                    </div>

                    <div className="field-metadata">
                      <span className="badge">
                        {field.field_type}
                      </span>

                      <span>Key: {field.key}</span>
                    </div>

                    {field.options && (
                      <div className="option-list">
                        {field.options.map((option) => (
                          <span
                            className="option-chip"
                            key={option}
                          >
                            {option}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="row-actions">
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => handleEdit(field)}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="text-button danger-text"
                      onClick={() => handleDelete(field)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}


export default FieldConfiguration;