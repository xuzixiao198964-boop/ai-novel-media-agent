import client from './client';
import { Novel } from '@/types';

// 获取小说列表
export const getNovels = async (params?: {
  category?: string;
  page?: number;
  limit?: number;
}): Promise<{ novels: Novel[]; total: number }> => {
  return client.get('/novels', { params });
};

// 获取小说详情
export const getNovelById = async (id: string): Promise<Novel> => {
  return client.get(`/novels/${id}`);
};

// 删除小说
export const deleteNovel = async (id: string): Promise<void> => {
  return client.delete(`/novels/${id}`);
};

// 发布小说到平台
export const publishNovel = async (
  id: string,
  platform: string
): Promise<void> => {
  return client.post(`/novels/${id}/publish`, { platform });
};

// 下载小说
export const downloadNovel = async (id: string): Promise<Blob> => {
  return client.get(`/novels/${id}/download`, { responseType: 'blob' });
};
