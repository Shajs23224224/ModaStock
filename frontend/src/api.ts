const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
export type User = { id: string; email: string; full_name: string; role: string; is_active: boolean }
export type VariantInventory = {
  id: string
  product_id: string
  product_name: string
  model_reference: string
  size_name: string
  color_name: string
  sku: string
  quantity: number
  minimum_quantity: number
  low_stock: boolean
  is_active: boolean
}
export type Product = { id: string; name: string; model_reference: string; description?: string | null; is_active: boolean; created_at: string }
export type Token = { access_token: string; token_type: string; expires_in: number }
export class ApiError extends Error { constructor(message: string, public status: number) { super(message) } }
async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  let response: Response
  try { response = await fetch(`${API_URL}${path}`, { ...options, headers }) }
  catch { throw new ApiError('No se pudo conectar con el servidor. Comprueba que la API esté activa.', 0) }
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    throw new ApiError(typeof detail === 'string' ? detail : 'Ocurrió un error al procesar la solicitud.', response.status)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
export const api = {
  login: (email: string, password: string) => request<Token>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (full_name: string, email: string, password: string) => request<User>('/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) }),
  me: (token: string) => request<User>('/auth/me', {}, token),
  products: (token: string) => request<Product[]>('/products?limit=100&offset=0', {}, token),
  createProduct: (token: string, data: { name: string; model_reference: string; description?: string }) => request<Product>('/products', { method: 'POST', body: JSON.stringify(data) }, token),
  variants: (token: string, q = '') => request<VariantInventory[]>(`/variants?limit=200${q ? `&q=${encodeURIComponent(q)}` : ''}`, {}, token),
  movements: (token: string, variantId?: string) => request<unknown[]>(`/inventory/movements?limit=100${variantId ? `&variant_id=${encodeURIComponent(variantId)}` : ''}`, {}, token),
  updateMinimumStock: (token: string, variantId: string, minimum_quantity: number) => request(`/variants/${variantId}/minimum-stock`, { method: 'PATCH', body: JSON.stringify({ minimum_quantity }) }, token),
  createMovement: (token: string, data: { variant_id: string; movement_type: 'IN' | 'OUT'; quantity: number; reason: string }, key: string) => request('/inventory/movements', { method: 'POST', headers: { 'Idempotency-Key': key }, body: JSON.stringify(data) }, token),
}
