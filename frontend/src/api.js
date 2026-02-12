export const api = async (path: string, options = {}) => {
  const res = await fetch(`http://127.0.0.1:8000${path}`, options);
  return res.json();
};
