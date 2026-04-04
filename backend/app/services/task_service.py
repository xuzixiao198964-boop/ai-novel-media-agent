# -*- coding: utf-8 -*-
"""任务服务层"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task, TaskStatus
from app.schemas.task import TaskCreateRequest, TaskProgressResponse
from app.config import settings
import asyncio


class TaskService:
    """任务管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def estimate_cost(self, request: TaskCreateRequest) -> float:
        """预估任务成本"""
        total_cost = 0.0

        # 小说成本估算
        if request.novel_config:
            length_map = {
                "micro": 3000,
                "short": 15000,
                "medium": 65000,
                "long": 300000,
                "super_long": 500000,
                "random": 50000
            }
            estimated_words = length_map.get(request.novel_config.length_type, 50000)
            novel_cost = (estimated_words / 1000) * settings.novel_price_per_1k_words
            total_cost += novel_cost

        # 视频成本估算
        if request.video_config:
            # 假设平均每集3分钟
            estimated_seconds = 180
            video_cost = estimated_seconds * settings.video_price_per_second
            total_cost += video_cost

        # 应用倍率
        markup = (settings.billing_markup_min + settings.billing_markup_max) / 2
        return round(total_cost * markup, 2)

    async def submit_to_queue(self, task: Task):
        """提交任务到队列"""
        # TODO: 实现Celery任务提交
        # from app.tasks import process_novel_task, process_video_task
        # if task.type in ["novel_only", "novel_video"]:
        #     process_novel_task.delay(task.task_id)
        # elif task.type in ["external_video", "news_video"]:
        #     process_video_task.delay(task.task_id)
        pass

    async def get_progress(self, task: Task) -> TaskProgressResponse:
        """获取任务进度"""
        # TODO: 从Redis获取实时进度
        return TaskProgressResponse(
            task_id=task.task_id,
            status=task.status.value,
            progress=task.progress,
            current_step=task.current_step,
            queue_position=task.queue_position,
            estimated_time=task.estimated_time,
            agent_progress=[],
            logs=[]
        )

    async def update_progress(
        self,
        task_id: str,
        progress: float,
        current_step: Optional[str] = None,
        status: Optional[TaskStatus] = None
    ):
        """更新任务进度"""
        # TODO: 更新Redis和数据库
        pass
