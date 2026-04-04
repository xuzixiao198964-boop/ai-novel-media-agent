import api from './client'

export interface TaskConfig {
  task_type: 'novel_only' | 'novel_video' | 'external_video' | 'news_video'
  novel_config?: {
    length_type: string
    genre: string
    sub_genres?: string[]
  }
  video_config?: {
    visual_mode: string
    enable_voice: boolean
    enable_subtitle: boolean
    enable_bgm: boolean
  }
  api_preference?: string
}

export interface Task {
  task_id: string
  user_id: string
  task_type: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  queue_position?: number
  current_agent?: string
  estimated_time?: number
  created_at: string
  updated_at: string
}

export const taskApi = {
  create: (config: TaskConfig) => api.post('/tasks', config),
  list: () => api.get('/tasks'),
  get: (taskId: string) => api.get(`/tasks/${taskId}`),
  cancel: (taskId: string) => api.post(`/tasks/${taskId}/cancel`)
}

// 导出单独的函数供其他模块使用
export const getTasks = () => api.get('/tasks').then(res => res.data)
export const getTaskById = (taskId: string) => api.get(`/tasks/${taskId}`).then(res => res.data)
export const createNovelTask = (config: TaskConfig) => api.post('/tasks', config).then(res => res.data)
export const cancelTask = (taskId: string) => api.post(`/tasks/${taskId}/cancel`).then(res => res.data)
export const getRunningTasks = () => api.get('/tasks?status=running').then(res => res.data)
