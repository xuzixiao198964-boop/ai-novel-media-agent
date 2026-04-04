import client from './client';
import { Stats, BillingRecord } from '@/types';

// 获取统计数据
export const getStats = async (): Promise<Stats> => {
  return client.get('/stats');
};

// 获取消费记录
export const getBillingRecords = async (params?: {
  startDate?: string;
  endDate?: string;
  page?: number;
  limit?: number;
}): Promise<{ records: BillingRecord[]; total: number }> => {
  return client.get('/billing', { params });
};

// 充值
export const recharge = async (data: {
  amount: number;
  paymentMethod: 'wechat' | 'alipay';
}): Promise<{ orderId: string; qrCode: string }> => {
  return client.post('/recharge', data);
};
