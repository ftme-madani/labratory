import { create } from 'zustand'

export type ThemeMode = 'light' | 'dark'

interface ThemeState {
  theme: ThemeMode
  setTheme: (theme: ThemeMode) => void
  toggleTheme: () => void
}

const getInitialTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'light'
  const saved = localStorage.getItem('lab_theme') as ThemeMode | null
  if (saved === 'dark' || saved === 'light') return saved
  return 'light' // Default to Day mode as requested
}

const applyThemeToDOM = (theme: ThemeMode) => {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
    root.classList.remove('light')
    root.setAttribute('data-theme', 'dark')
  } else {
    root.classList.add('light')
    root.classList.remove('dark')
    root.setAttribute('data-theme', 'light')
  }
}

export const useThemeStore = create<ThemeState>((set, get) => {
  const initialTheme = getInitialTheme()
  applyThemeToDOM(initialTheme)

  return {
    theme: initialTheme,
    setTheme: (theme: ThemeMode) => {
      localStorage.setItem('lab_theme', theme)
      applyThemeToDOM(theme)
      set({ theme })
    },
    toggleTheme: () => {
      const current = get().theme
      const next: ThemeMode = current === 'dark' ? 'light' : 'dark'
      get().setTheme(next)
    }
  }
})
