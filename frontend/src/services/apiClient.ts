export const TOKEN_STORAGE_KEY = 'virtual_lab_auth_token'
export const USER_STORAGE_KEY = 'virtual_lab_auth_user'

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export const getToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

export const setToken = (token: string): void => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
  } catch (e) {
    console.warn('عدم امکان ذخیره‌سازی توکن در حافظه محلی:', e)
  }
}

export const removeToken = (): void => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch (e) {
    console.warn('خطا در پاک‌سازی توکن:', e)
  }
}

export const getStoredUser = <T>(): T | null => {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const setStoredUser = <T>(user: T): void => {
  try {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  } catch (e) {
    console.warn('عدم امکان ذخیره‌سازی اطلاعات کاربر:', e)
  }
}

export const removeStoredUser = (): void => {
  try {
    localStorage.removeItem(USER_STORAGE_KEY)
  } catch (e) {
    console.warn('خطا در پاک‌سازی اطلاعات کاربر:', e)
  }
}

const getApiBaseUrl = (): string => {
  // اگر در متغیرهای محیطی آدرس مستقیم مشخص شده باشد از آن استفاده می‌کنیم، در غیر این صورت از مسیر پراکسی /api/v1
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL
  if (envUrl) return envUrl
  return '/api/v1'
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = getApiBaseUrl()
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  const fullUrl = cleanEndpoint.startsWith('http') ? cleanEndpoint : `${baseUrl}${cleanEndpoint}`

  const headers = new Headers(options.headers || {})

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const token = getToken()
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers
    })

    if (!response.ok) {
      let errorDetail = `خطای سرور (${response.status})`
      try {
        const errorJson = await response.json()
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail)
        }
      } catch {
        // بدنه پاسخ JSON نیست
      }

      if (response.status === 401) {
        removeToken()
        removeStoredUser()
      }

      throw new ApiError(response.status, errorDetail)
    }

    // اگر محتوا خالی باشد
    if (response.status === 204) {
      return {} as T
    }

    return await response.json()
  } catch (err) {
    if (err instanceof ApiError) {
      throw err
    }
    // خطای شبکه یا قطعی اینترنت
    console.warn(`[Network Warning] عدم برقراری ارتباط با ${fullUrl}:`, err)
    throw new ApiError(0, 'عدم برقراری ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید.')
  }
}

export const apiClient = {
  get: <T>(url: string, options?: RequestInit) => apiRequest<T>(url, { method: 'GET', ...options }),
  post: <T>(url: string, body?: any, options?: RequestInit) =>
    apiRequest<T>(url, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      ...options
    }),
  put: <T>(url: string, body?: any, options?: RequestInit) =>
    apiRequest<T>(url, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
      ...options
    }),
  delete: <T>(url: string, options?: RequestInit) => apiRequest<T>(url, { method: 'DELETE', ...options })
}
