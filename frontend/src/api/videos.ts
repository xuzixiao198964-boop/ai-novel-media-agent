import client from './client';
import { Video } from '@/types';

// 获取视频列表
export const getVideos = async (params?: {
  type?: string;
  page?: number;
  limit?: number;
}): Promise<{ videos: Video[]; total: number }> => {
  return client.get('/videos', { params });
};

// 获取视频详情
export const getVideoById = async (id: string): Promise<Video> => {
  return client.get(`/videos/${id}`);
};

// 删除视频
export const deleteVideo = async (id: string): Promise<void> => {
  return client.delete(`/videos/${id}`);
};

// 发布视频到平台
export const publishVideo = async (
  id: string,
  platform: string
): Promise<void> => {
  return client.post(`/videos/${id}/publish`, { platform });
};

// 下载视频
export const downloadVideo = async (id: string): Promise<Blob> => {
  return client.get(`/videos/${id}/download`, { responseType: 'blob' });
};
