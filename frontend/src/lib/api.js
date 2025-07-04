import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const userAPI = {
  getAll: () => api.get('/users'),
  create: (data) => api.post('/users', data),
  delete: (id) => api.delete(`/users/${id}`)
};

export const qrAPI = {
  generate: (data) => api.post('/generate-qr', data),
  sendEmail: (data) => api.post('/send-qr-email', data)
};

export const attendanceAPI = {
  check: (data) => api.post('/attendance/check', data),
  getAll: (params) => api.get('/attendance', { params })
};

export default api;