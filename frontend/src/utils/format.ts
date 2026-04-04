// 格式化金额
export const formatCurrency = (amount: number): string => {
  return `¥${amount.toFixed(2)}`;
};

// 格式化日期
export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('zh-CN');
};

// 格式化时间
export const formatDateTime = (date: string): string => {
  return new Date(date).toLocaleString('zh-CN');
};

// 格式化时长（秒转分钟）
export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

// 格式化字数
export const formatWordCount = (count: number): string => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万字`;
  }
  return `${count}字`;
};
