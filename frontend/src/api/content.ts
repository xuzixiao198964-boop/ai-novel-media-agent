import api from './client'

export interface Novel {
  novel_id: string
  title: string
  genre: string
  sub_genre: string
  word_count: number
  rating?: number
  published_to_square: boolean
  created_at: string
}

export interface Video {
  video_id: string
  title: string
  type: 'novel' | 'news'
  duration: number
  episodes?: number
  created_at: string
}

export const contentApi = {
  listNovels: () => api.get('/novels'),
  getNovel: (novelId: string) => api.get(`/novels/${novelId}`),
  downloadNovel: (novelId: string) => api.get(`/novels/${novelId}/download`, { responseType: 'blob' }),
  deleteNovel: (novelId: string) => api.delete(`/novels/${novelId}`),

  listVideos: () => api.get('/videos'),
  getVideo: (videoId: string) => api.get(`/videos/${videoId}`),
  downloadVideo: (videoId: string) => api.get(`/videos/${videoId}/download`, { responseType: 'blob' }),
  deleteVideo: (videoId: string) => api.delete(`/videos/${videoId}`),

  listSquare: () => api.get('/square')
}
