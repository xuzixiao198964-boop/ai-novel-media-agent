import client from './client';
import { User } from '@/types';

// 注册
export const register = async (data: {
  username: string;
  email: string;
  password: string;
}): Promise<{ token: string; user: User }> => {
  return client.post('/auth/register', data);
};

// 登录
export const login = async (data: {
  username: string;
  password: string;
}): Promise<{ token: string; user: User }> => {
  const response: any = await client.post('/auth/login', data);
  return {
    token: response.access_token,
    user: response.user || { username: data.username }
  };
};

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User> => {
  return client.get('/auth/me');
};

// 更新用户信息
export const updateUser = async (data: Partial<User>): Promise<User> => {
  return client.put('/auth/me', data);
};
