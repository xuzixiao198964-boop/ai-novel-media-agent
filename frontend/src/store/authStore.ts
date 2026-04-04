import { create } from 'zustand';
import { User } from '@/types';
import { getToken, setToken as saveToken, removeToken } from '@/utils/auth';
import * as authApi from '@/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: getToken(),
  isAuthenticated: !!getToken(),
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const { token, user } = await authApi.login({ email, password });
      saveToken(token);
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true });
    try {
      const { token, user } = await authApi.register({ username, email, password });
      saveToken(token);
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    removeToken();
    set({ user: null, token: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const user = await authApi.getCurrentUser();
      set({ user });
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  },

  updateUser: async (data: Partial<User>) => {
    try {
      const user = await authApi.updateUser(data);
      set({ user });
    } catch (error) {
      throw error;
    }
  },
}));
