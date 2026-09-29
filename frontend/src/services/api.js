const API_BASE_URL = "http://127.0.0.1:8000";


async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let message = "Something went wrong.";

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      } else if (error.detail) {
        message = JSON.stringify(error.detail);
      }
    } catch {
      message = `Request failed with status ${response.status}.`;
    }

    throw new Error(message);
  }

  return response.json();
}


export const fieldApi = {
  getAll() {
    return request("/fields");
  },

  create(data) {
    return request("/fields", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update(fieldId, data) {
    return request(`/fields/${fieldId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  delete(fieldId) {
    return request(`/fields/${fieldId}`, {
      method: "DELETE",
    });
  },
};


export const machineApi = {
  getAll() {
    return request("/machines");
  },

  getOne(machineId) {
    return request(`/machines/${machineId}`);
  },

  create(data) {
    return request("/machines", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update(machineId, data) {
    return request(`/machines/${machineId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  delete(machineId) {
    return request(`/machines/${machineId}`, {
      method: "DELETE",
    });
  },
};


export const predictionApi = {
  predict(machineId) {
    return request("/predictions", {
      method: "POST",
      body: JSON.stringify({
        machine_id: Number(machineId),
      }),
    });
  },
};