import api from './client'

export interface BillingRecord {
  id: string
  type: 'novel' | 'video' | 'recharge'
  amount: number
  description: string
  created_at: string
}

export const billingApi = {
  getBalance: () => api.get('/billing/balance'),
  recharge: (amount: number, method: string) => api.post('/billing/recharge', { amount, method }),
  getRecords: () => api.get('/billing/records'),

  getPackage: () => api.get('/billing/package'),
  switchPackage: (packageType: string) => api.post('/billing/package', { package_type: packageType })
}
