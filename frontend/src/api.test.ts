import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from './api'

describe('ModaStock API client', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sends login credentials as JSON to the configured API path', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({
      access_token: 'test-token',
      token_type: 'bearer',
      expires_in: 1800,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }))

    const result = await api.login('staff@example.com', 'password-test')
    expect(result.access_token).toBe('test-token')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.any(Headers),
        body: JSON.stringify({ email: 'staff@example.com', password: 'password-test' }),
      }),
    )
    const requestOptions = fetchMock.mock.calls[0][1] as RequestInit
    expect(new Headers(requestOptions.headers).get('Content-Type')).toBe('application/json')
  })

  it('attaches bearer token to authenticated requests', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }))
    await api.products('session-token')
    const requestOptions = fetchMock.mock.calls[0][1] as RequestInit
    expect(new Headers(requestOptions.headers).get('Authorization')).toBe('Bearer session-token')
  })

  it('sends idempotency key with inventory movement', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ id: 'movement-1' }), { status: 201 }))
    await api.createMovement(
      'session-token',
      { variant_id: 'variant-1', movement_type: 'IN', quantity: 2, reason: 'Recepción' },
      'request-unique-1',
    )
    const requestOptions = fetchMock.mock.calls[0][1] as RequestInit
    const headers = new Headers(requestOptions.headers)
    expect(headers.get('Authorization')).toBe('Bearer session-token')
    expect(headers.get('Idempotency-Key')).toBe('request-unique-1')
  })

  it('converts API error details into ApiError with HTTP status', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ detail: 'Existencias insuficientes' }), {
      status: 409,
      headers: { 'Content-Type': 'application/json' },
    }))
    await expect(api.products('session-token')).rejects.toMatchObject({
      name: 'ApiError',
      message: 'Existencias insuficientes',
      status: 409,
    })
  })

  it('normalizes network failures into a connection ApiError', async () => {
    fetchMock.mockRejectedValue(new TypeError('Network unavailable'))
    await expect(api.products('session-token')).rejects.toBeInstanceOf(ApiError)
    await expect(api.products('session-token')).rejects.toMatchObject({ status: 0 })
  })
})
