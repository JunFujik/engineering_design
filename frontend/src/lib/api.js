import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true // セッション管理のためのクッキーを送信
});

export const userAPI = {
  getAll: () => api.get('/users'),
  create: (data) => api.post('/users', data),
  delete: (id) => api.delete(`/users/${id}`)
};

export const qrAPI = {
  generate: (data) => api.post('/generate-qr', data),
  sendEmail: (data) => api.post('/send-qr-email', data),
  sendEmailToAll: () => api.post('/send-qr-email-all') // 追加
};

export const attendanceAPI = {
  check: (data) => api.post('/attendance/check', data),
  getAll: (params) => api.get('/attendance', { params }),
  requestMakeUpClass: (data) => api.post('/makeup-request', data) // 補講申請
};

export const authAPI = {
  login: (password) => api.post('/auth/login', { password }),
  logout: () => api.post('/auth/logout'),
  getStatus: () => api.get('/auth/status')
};

// 新しいAPI: インポートデータ関連
export const importAPI = {
  saveData: (data) => api.post('/import-excel', data),
  getAll: () => api.get('/imported-data'),
  getDetail: (id) => api.get(`/imported-data/${id}`),
  delete: (id) => api.delete(`/imported-data/${id}`)
};

// 補講申請API
export const makeupAPI = {
  create: (data) => api.post('/makeup-request', data),
  getAll: () => api.get('/makeup-requests')
};

export default api;