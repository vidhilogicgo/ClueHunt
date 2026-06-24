const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with ${response.status}`);
  }

  return response.json();
}

export function createCase(payload) {
  return request("/api/cases", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function submitAccusation(payload) {
  return request("/api/accuse", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
