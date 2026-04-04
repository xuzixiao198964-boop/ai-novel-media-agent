// 用户类型
export interface User {
  id: string;
  username: string;
  email: string;
  balance: number;
  package: 'basic' | 'advanced' | 'professional' | 'enterprise';
  createdAt: string;
}

// 任务状态
export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

// 任务类型
export type TaskType = 'novel' | 'video' | 'news_video';

// Agent状态
export interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: string;
  note?: string;
}

// 任务详情
export interface Task {
  id: string;
  type: TaskType;
  status: TaskStatus;
  title: string;
  description: string;
  progress: number;
  currentStep?: string;
  estimatedTime?: number;
  queuePosition?: number;
  agents?: AgentStatus[];
  cost?: number;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

// 小说配置
export interface NovelConfig {
  length: 'micro' | 'short' | 'medium' | 'long' | 'super_long' | 'random';
  category: 'children' | 'male' | 'female' | 'random';
  subCategories: string[];
  apiPreference: 'auto' | 'deepseek' | 'gemini' | 'openai';
}

// 视频配置
export interface VideoConfig {
  mode: 'ai_generated' | 'image_only' | 'imported' | 'random';
  enableVoice: boolean;
  lipSync: boolean;
  voiceSpeed: number;
  voiceType: string;
  enableSubtitle: boolean;
  enableMusic: boolean;
  subtitleFont: string;
  subtitleColor: string;
  subtitlePosition: 'bottom' | 'top' | 'center';
}

// 创作模式
export type CreationMode = 'novel_only' | 'novel_video' | 'external_video' | 'news_video';

// 小说作品
export interface Novel {
  id: string;
  title: string;
  category: string;
  length: string;
  wordCount: number;
  rating: number;
  status: 'draft' | 'published';
  publishedTo?: string[];
  createdAt: string;
  updatedAt: string;
}

// 视频作品
export interface Video {
  id: string;
  title: string;
  type: 'novel' | 'news';
  duration: number;
  episodes?: number;
  status: 'processing' | 'completed';
  publishedTo?: string[];
  createdAt: string;
}

// 消费记录
export interface BillingRecord {
  id: string;
  date: string;
  task: string;
  type: string;
  quantity: string;
  amount: number;
}

// 平台绑定
export interface PlatformBinding {
  platform: 'douyin' | 'xiaohongshu' | 'fanqie' | 'qidian';
  name: string;
  icon: string;
  description: string;
  bound: boolean;
  accountName?: string;
}

// 统计数据
export interface Stats {
  runningTasks: number;
  queuedTasks: number;
  completedWorks: number;
  novels: number;
  videos: number;
  monthlySpending: number;
  novelSpending: number;
  videoSpending: number;
  currentPackage: string;
}
