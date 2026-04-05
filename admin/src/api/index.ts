import client from './client'

export const dashboardApi = {
  getStats: () => client.get('/admin/dashboard'),
  getIncomeTrend: (days = 30) => client.get(`/admin/dashboard/income-trend?days=${days}`),
  getRecentUsers: (limit = 5) => client.get(`/admin/dashboard/recent-users?limit=${limit}`),
  getTaskDistribution: () => client.get('/admin/dashboard/task-distribution'),
  getSubscriptionDistribution: () => client.get('/admin/dashboard/subscription-distribution'),
}

export const usersApi = {
  list: (params: any) => client.get('/admin/users', { params }),
  getDetail: (id: number) => client.get(`/admin/users/${id}`),
  update: (id: number, data: any) => client.patch(`/admin/users/${id}`, data),
}

export const novelsApi = {
  list: (params: any) => client.get('/admin/novels', { params }),
  updateStatus: (id: number, isPublic: boolean) =>
    client.patch(`/admin/novels/${id}/status`, { is_public: isPublic }),
  delete: (id: number) => client.delete(`/admin/novels/${id}`),
}

export const videosApi = {
  list: (params: any) => client.get('/admin/videos', { params }),
}

export const tasksApi = {
  getStats: () => client.get('/admin/tasks/stats'),
  list: (params: any) => client.get('/admin/tasks', { params }),
  stop: (id: number) => client.post(`/admin/tasks/${id}/stop`),
}

export const apiKeysApi = {
  list: (params: any) => client.get('/admin/api-keys', { params }),
  create: (data: any) => client.post('/admin/api-keys', data),
  revoke: (id: number) => client.delete(`/admin/api-keys/${id}`),
}

export const financeApi = {
  getSummary: () => client.get('/admin/finance/summary'),
  getTrend: (days = 30) => client.get(`/admin/finance/trend?days=${days}`),
}

export const publishApi = {
  list: (params: any) => client.get('/admin/publish', { params }),
  retry: (id: number) => client.post(`/admin/publish/${id}/retry`),
}

export const logsApi = {
  list: (params: any) => client.get('/admin/logs', { params }),
}

export const configApi = {
  getAll: () => client.get('/admin/config'),
  get: (key: string) => client.get(`/admin/config/${key}`),
  update: (data: any) => client.put('/admin/config', data),
}

export const authApi = {
  login: (username: string, password: string) =>
    client.post('/auth/login', { username, password }),
  logout: () => client.post('/auth/logout'),
}
