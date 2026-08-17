const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = window.localStorage.getItem('edusync-token');
  const isMultipart = options?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { ...(isMultipart ? {} : { 'Content-Type': 'application/json' }), ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options?.headers },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(error?.detail || `API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}
