import { create } from 'zustand';
import { User, Driver } from './types';

interface AuthState {
  user: User | null;
  driver: Driver | null;
  isAuthenticated: boolean;
  setAuth: (user: User, driver?: Driver) => void;
  logout: () => void;
  loadFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  driver: null,
  isAuthenticated: false,
  
  setAuth: (user, driver) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
      if (driver) {
        localStorage.setItem('driver', JSON.stringify(driver));
      }
    }
    set({ user, driver, isAuthenticated: true });
  },
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('driver');
    }
    set({ user: null, driver: null, isAuthenticated: false });
  },
  
  loadFromStorage: () => {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      const driverStr = localStorage.getItem('driver');
      const token = localStorage.getItem('access_token');
      
      if (userStr && token) {
        const user = JSON.parse(userStr);
        const driver = driverStr ? JSON.parse(driverStr) : null;
        set({ user, driver, isAuthenticated: true });
      }
    }
  },
}));