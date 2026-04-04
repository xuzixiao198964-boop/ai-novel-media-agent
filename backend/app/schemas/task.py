# -*- coding: utf-8 -*-
"""Pydantic数据模型 - 任务相关"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class NovelConfig(BaseModel):
    """小说配置"""
    length_type: Literal["micro", "short", "medium", "long", "super_long", "random"] = "random"
    genre: Literal["children", "male", "female", "random"] = "random"
    sub_genre: Optional[str] = None
    age_group: Optional[str] = None  # 儿童故事年龄段

    # 外部小说来源
    external_url: Optional[str] = None
    external_text: Optional[str] = None

    # API偏好
    api_preference: Optional[List[str]] = None


class SubtitleConfig(BaseModel):
    """字幕配置"""
    enabled: bool = True
    font: str = "Arial"
    size: int = 24
    color: str = "#FFFFFF"
    position: Literal["bottom", "top", "center"] = "bottom"


class VoiceConfig(BaseModel):
    """语音配置"""
    enabled: bool = True
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(1.0, ge=0.5, le=2.0)
    voice_id: str = "default"


class VideoConfig(BaseModel):
    """视频配置"""
    visual_mode: Literal["ai_generated", "images_only", "user_import", "random"] = "random"
    lip_sync: bool = False
    background_music: Optional[str] = None
    subtitle: SubtitleConfig = SubtitleConfig()
    voice: VoiceConfig = VoiceConfig()
    source_novels: Optional[List[str]] = None


class NewsConfig(BaseModel):
    """资讯配置"""
    article_ids: Optional[List[int]] = None
    category_id: Optional[int] = None
    auto_translate: bool = True


class PublishConfig(BaseModel):
    """发布配置"""
    platforms: List[str] = []  # douyin, xiaohongshu, fanqiao, qidian
    auto_publish: bool = False
    publish_to_square: bool = False


class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    task_type: Literal["novel_only", "novel_video", "external_video", "news_video"]

    novel_config: Optional[NovelConfig] = None
    video_config: Optional[VideoConfig] = None
    news_config: Optional[NewsConfig] = None
    publish_config: Optional[PublishConfig] = None

    auto_mode: bool = False  # 冲突时自动决策


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    task_id: str
    type: str
    status: str
    progress: float
    current_step: Optional[str]
    queue_position: Optional[int]
    estimated_time: Optional[int]
    cost_estimate: Optional[float]
    actual_cost: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    task_id: str
    status: str
    progress: float
    current_step: Optional[str]
    queue_position: Optional[int]
    estimated_time: Optional[int]
    agent_progress: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: List[TaskResponse]
