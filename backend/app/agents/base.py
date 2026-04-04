# -*- coding: utf-8 -*-
"""Agent基类定义"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from datetime import datetime


class AgentStatus:
    """Agent状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentResult:
    """Agent执行结果"""
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class BaseAgent(ABC):
    """所有Agent的基类"""

    name: str = "BaseAgent"

    def __init__(self, task_id: str, config: Optional[Dict[str, Any]] = None):
        self.task_id = task_id
        self.config = config or {}
        self.progress = 0.0
        self.status = AgentStatus.PENDING
        self.logs = []

    def log(self, level: str, message: str, detail: Optional[Dict] = None):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "level": level,
            "message": message,
            "detail": detail
        }
        self.logs.append(log_entry)
        print(f"[{level.upper()}] {self.name}: {message}")

    def update_progress(self, progress: float, message: str = ""):
        """更新进度"""
        self.progress = min(100.0, max(0.0, progress))
        if message:
            self.log("info", message)

    def set_running(self, message: str = ""):
        """设置为运行中"""
        self.status = AgentStatus.RUNNING
        self.log("info", message or f"{self.name} 开始执行")

    def set_completed(self, message: str = ""):
        """设置为完成"""
        self.status = AgentStatus.COMPLETED
        self.progress = 100.0
        self.log("info", message or f"{self.name} 执行完成")

    def set_failed(self, error: str):
        """设置为失败"""
        self.status = AgentStatus.FAILED
        self.log("error", f"{self.name} 执行失败: {error}")

    @abstractmethod
    async def run(self) -> AgentResult:
        """执行Agent主流程（子类必须实现）"""
        pass

    async def execute(self) -> AgentResult:
        """执行Agent（带异常处理）"""
        try:
            self.set_running()
            result = await self.run()

            if result.success:
                self.set_completed()
            else:
                self.set_failed(result.error or "未知错误")

            return result
        except Exception as e:
            self.set_failed(str(e))
            return AgentResult(success=False, error=str(e))
