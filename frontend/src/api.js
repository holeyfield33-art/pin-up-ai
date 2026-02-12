const BASE_URL = "http://127.0.0.1:8000";

export const api = async (path, options = {}) => {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
};

export const snippetsAPI = {
  list: (limit = 50, offset = 0, collectionId = null) =>
    api(`/snippets/?limit=${limit}&offset=${offset}${collectionId ? `&collection_id=${collectionId}` : ""}`),
  create: (data) => api("/snippets/", { method: "POST", body: JSON.stringify(data) }),
  get: (id) => api(`/snippets/${id}`),
  search: (q, limit = 50) => api(`/snippets/search/query?q=${encodeURIComponent(q)}&limit=${limit}`),
  delete: (id) => api(`/snippets/${id}`, { method: "DELETE" }),
};

export const tagsAPI = {
  list: (limit = 100) => api(`/tags/?limit=${limit}`),
  create: (data) => api("/tags/", { method: "POST", body: JSON.stringify(data) }),
};

export const collectionsAPI = {
  list: (limit = 100) => api(`/collections/?limit=${limit}`),
  create: (data) => api("/collections/", { method: "POST", body: JSON.stringify(data) }),
};
