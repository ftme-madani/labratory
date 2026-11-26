import type { User, UserRole } from '../types/user'
import { apiClient, setToken, getToken, removeToken, setStoredUser, getStoredUser, removeStoredUser } from './apiClient'
import { MOCK_USER, MOCK_TEACHER } from './mockData'

interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number | string
    username: string
    email: string
    full_name: string
    role: UserRole
    grade?: string
    school_name?: string
    created_at: string
  }
}

function mapBackendUserToFrontend(raw: any): User {
  return {
    id: String(raw.id),
    username: raw.username,
    fullName: raw.full_name || raw.fullName,
    email: raw.email,
    role: raw.role,
    grade: raw.grade,
    schoolName: raw.school_name || raw.schoolName,
    createdAt: raw.created_at || raw.createdAt || new Date().toISOString()
  }
}

class AuthService {
  private currentUser: User | null = null

  constructor() {
    this.currentUser = getStoredUser<User>()
  }

  async login(role: UserRole = 'student'): Promise<User> {
    // ورود با حساب‌های رسمی بذرپاشی‌شده در پایگاه داده
    const credentials =
      role === 'teacher'
        ? { email: 'm.moradi@edu.ir', password: 'Teacher123456' }
        : { email: 'alireza@school.ir', password: 'Student123456' }

    return this.loginWithCredentials(credentials.email, credentials.password, role)
  }

  async loginWithCredentials(email: string, password: string, fallbackRole: UserRole = 'student'): Promise<User> {
    try {
      const data = await apiClient.post<AuthResponse>('/auth/login', { email, password })
      setToken(data.access_token)
      const user = mapBackendUserToFrontend(data.user)
      this.currentUser = user
      setStoredUser(user)
      return user
    } catch (err) {
      console.warn('[AuthService] ورود برخط با خطا مواجه شد، استفاده از حساب محلی:', err)
      // حالت آفلاین یا خطای سرور
      const fallbackUser = fallbackRole === 'teacher' ? MOCK_TEACHER : MOCK_USER
      this.currentUser = fallbackUser
      setStoredUser(fallbackUser)
      return fallbackUser
    }
  }

  async register(data: {
    fullName: string
    email: string
    password?: string
    role: UserRole
    grade?: string
    schoolName?: string
  }): Promise<User> {
    try {
      const payload = {
        username: data.email.split('@')[0],
        email: data.email,
        password: data.password || 'Student123456',
        full_name: data.fullName,
        role: data.role,
        grade: data.grade,
        school_name: data.schoolName
      }
      const res = await apiClient.post<AuthResponse>('/auth/register', payload)
      setToken(res.access_token)
      const user = mapBackendUserToFrontend(res.user)
      this.currentUser = user
      setStoredUser(user)
      return user
    } catch (err) {
      console.warn('[AuthService] ثبت‌نام برخط با خطا مواجه شد، استفاده از حساب محلی:', err)
      const localUser: User = {
        id: `usr-${Date.now()}`,
        username: data.email.split('@')[0],
        fullName: data.fullName,
        email: data.email,
        role: data.role,
        grade: data.grade,
        schoolName: data.schoolName,
        createdAt: new Date().toISOString()
      }
      this.currentUser = localUser
      setStoredUser(localUser)
      return localUser
    }
  }

  async fetchCurrentUser(): Promise<User | null> {
    const token = getToken()
    if (!token) {
      return this.currentUser
    }
    try {
      const raw = await apiClient.get<any>('/auth/me')
      const user = mapBackendUserToFrontend(raw)
      this.currentUser = user
      setStoredUser(user)
      return user
    } catch (err) {
      console.warn('[AuthService] استعلام پروفایل کاربر ناموفق بود:', err)
      return this.currentUser
    }
  }

  getCurrentUser(): User | null {
    if (!this.currentUser) {
      this.currentUser = getStoredUser<User>()
    }
    return this.currentUser || MOCK_USER
  }

  logout(): void {
    removeToken()
    removeStoredUser()
    this.currentUser = null
  }
}

export const authService = new AuthService()
