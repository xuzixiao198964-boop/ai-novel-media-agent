import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  username: string | null
  login: (username: string, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('admin_token'),
  username: localStorage.getItem('admin_username'),
  login: (username, token) => {
    localStorage.setItem('admin_token', token)
    localStorage.setItem('admin_username', username)
    set({ isAuthenticated: true, username })
  },
  logout: () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_username')
    set({ isAuthenticated: false, username: null })
  },
}))
