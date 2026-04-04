import api from './client'

export interface Platform {
  platform: string
  bound: boolean
  account?: string
}

export const platformApi = {
  list: () => api.get('/platforms'),
  bind: (platform: string, authCode: string) => api.post('/platforms/bind', { platform, auth_code: authCode }),
  unbind: (platform: string) => api.post('/platforms/unbind', { platform }),

  publish: (contentId: string, platform: string) => api.post('/platforms/publish', { content_id: contentId, platform })
}
