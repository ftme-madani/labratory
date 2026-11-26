import { create } from 'zustand'
import type { User, UserRole } from '../types/user'
import { authService } from '../services/authService'
import { getToken } from '../services/apiClient'

interface AuthStoreState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (role?: UserRole) => Promise<void>
  loginWithCredentials: (email: string, password: string) => Promise<User>
  logout: () => void
  switchRole: (role: UserRole) => Promise<void>
  checkAuth: () => Promise<void>
}

const initialUser = authService.getCurrentUser()

export const useAuthStore = create<AuthStoreState>((set) => ({
  user: initialUser,
  isAuthenticated: Boolean(initialUser || getToken()),
  isLoading: false,

  login: async (role = 'student') => {
    set({ isLoading: true })
    try {
      const user = await authService.login(role)
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      set({ isLoading: false })
    }
  },

  loginWithCredentials: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      const user = await authService.loginWithCredentials(email, password)
      set({ user, isAuthenticated: true, isLoading: false })
      return user
    } finally {
      set({ isLoading: false })
    }
  },

  logout: () => {
    authService.logout()
    set({ user: null, isAuthenticated: false, isLoading: false })
  },

  switchRole: async (role: UserRole) => {
    set({ isLoading: true })
    try {
      const user = await authService.login(role)
      set({ user, isAuthenticated: true, isLoading: false })
    } finally {
      set({ isLoading: false })
    }
  },

  checkAuth: async () => {
    const user = await authService.fetchCurrentUser()
    if (user) {
      set({ user, isAuthenticated: true })
    }
  }
}))

// راه‌اندازی نشست پیش‌فرض برای بازدیدکنندگان مهمان تا هیچ خطای ۴۰۱ در لابراتوار رخ ندهد
if (typeof window !== 'undefined' && !getToken()) {
  authService.login('student').then((user) => {
    useAuthStore.setState({ user, isAuthenticated: true })
  }).catch(() => {})
}

