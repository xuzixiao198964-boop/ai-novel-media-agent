import { create } from 'zustand'

interface User {
  id: string
  username: string
  email: string
  balance: number
  package: string
}

interface UserStore {
  user: User | null
  setUser: (user: User) => void
  updateBalance: (balance: number) => void
}

export const useUserStore = create<UserStore>((set) => ({
  user: {
    id: '1',
    username: 'AI创作者',
    email: 'user@example.com',
    balance: 88.30,
    package: '进阶版'
  },
  setUser: (user) => set({ user }),
  updateBalance: (balance) => set((state) => ({
    user: state.user ? { ...state.user, balance } : null
  }))
}))
