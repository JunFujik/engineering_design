import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true // セッション管理のためのクッキーを送信
});

export const userAPI = {
  getAll: () => api.get('/users'),
  create: (data) => api.post('/users', data),
  delete: (id) => api.delete(`/users/${id}`),
  importUsers: (data) => api.post('/users/import', data)
};

export const qrAPI = {
  generate: (data) => api.post('/generate-qr', data),
  sendEmail: (data) => api.post('/send-qr-email', data),
  sendEmailToAll: () => api.post('/send-qr-email-all') // 追加
};

export const attendanceAPI = {
  check: (data) => api.post('/attendance/check', data),
  getAll: (params) => api.get('/attendance', { params }),
  requestMakeUpClass: (data) => api.post('/makeup-requests', data), // 補講申請
  updateMakeUpClassStatus: (id, status) =>
    api.patch(`/makeup-requests/${id}`, { status }), // ← 追加
};

export const authAPI = {
  login: (password) => api.post('/auth/login', { password }),
  logout: () => api.post('/auth/logout'),
  getStatus: () => api.get('/auth/status'),
  staffLogin: (password) => api.post('/auth/staff-login', { password }),
};

// インポートデータ関連API
export const importAPI = {
  saveData: (data) => api.post('/import-excel', data),
  getAll: () => api.get('/imported-data'),
  getDetail: (id) => api.get(`/imported-data/${id}`),
  delete: (id) => api.delete(`/imported-data/${id}`)
};

// 補講申請API
export const makeupAPI = {
  getAll: () => api.get('/makeup-requests'),
  create: (data) => api.post('/makeup-request', data),
  update: (id, data) => api.patch(`/makeup-requests/${id}`, data)  // ← これが足りないと PATCH 飛ばない
};

// 先生給料設定API
export const teacherSalaryAPI = {
  getAll: () => api.get('/teacher-salaries'),
  createOrUpdate: (data) => api.post('/teacher-salaries', data),
  delete: (id) => api.delete(`/teacher-salaries/${id}`)
};

export const paidLeaveAPI = {
  create: (data) => api.post('/paid-leave', data),
  getAll: () => api.get('/paid-leave'),
};

export default api;