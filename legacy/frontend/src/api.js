// Cliente HTTP mínimo hacia el backend FastAPI (real, sin datos simulados).
// En desarrollo, Vite hace proxy de /api/* -> http://127.0.0.1:8000 (ver vite.config.js).
// En producción, el frontend compilado se sirve desde el mismo origen que la API,
// así que las rutas relativas funcionan igual en ambos casos.

async function parseJsonOrThrow(res) {
  let data = null;
  try {
    data = await res.json();
  } catch {
    // respuesta sin cuerpo JSON (p.ej. error de red genérico)
  }
  if (!res.ok) {
    const msg = (data && (data.detail || data.error)) || `Error HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export async function fetchConfig() {
  const res = await fetch('/api/config');
  return parseJsonOrThrow(res);
}

export async function predecir(texto) {
  const res = await fetch('/api/predecir', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texto }),
  });
  return parseJsonOrThrow(res);
}

export async function predecirLote(archivo) {
  const formData = new FormData();
  formData.append('archivo', archivo);
  const res = await fetch('/api/lote', { method: 'POST', body: formData });
  return parseJsonOrThrow(res);
}
