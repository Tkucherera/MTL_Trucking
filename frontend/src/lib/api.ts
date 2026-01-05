import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        if (typeof window !== 'undefined') {
          const refreshToken = localStorage.getItem('refresh_token');
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// API functions
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  
  verifyOTP: (tempToken: string, otpCode: string) =>
    api.post('/auth/login/otp/', { temp_token: tempToken, otp_code: otpCode }),
  
  requestEmailOTP: (email: string) =>
    api.post('/auth/otp/email/', { email }),
  
  verifyEmailOTP: (email: string, otpCode: string) =>
    api.post('/auth/otp/email/verify/', { email, otp_code: otpCode }),
  
  setupOTP: () => api.post('/auth/otp/setup/'),
  
  logout: (refreshToken: string) =>
    api.post('/auth/logout/', { refresh: refreshToken }),
};

export const driverApi = {
  getProfile: () => api.get('/drivers/me/'),
  getTrips: () => api.get('/trips/my_trips/'),
  getCurrentTrip: () => api.get('/trips/current_trip/'),
  getMileage: (driverId: number) => api.get(`/drivers/${driverId}/mileage/`),
  getDocuments: (driverId: number, type?: string) =>
    api.get(`/drivers/${driverId}/documents/${type ? `?type=${type}` : ''}`),
  getPayroll: (driverId: number) => api.get(`/drivers/${driverId}/payroll/`),
};

export const tripApi = {
  updateStatus: (tripId: number, data: any) =>
    api.post(`/trips/${tripId}/update_status/`, data),
  addRoutePoint: (tripId: number, data: any) =>
    api.post(`/trips/${tripId}/add_route_point/`, data),
  getRoute: (tripId: number) => api.get(`/trips/${tripId}/route/`),
  getUpdates: (tripId: number) => api.get(`/trips/${tripId}/updates/`),
};