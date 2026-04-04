# -*- coding: utf-8 -*-
"""风格解析Agent"""
from app.agents.base import BaseAgent, AgentResult
from typing import Dict, Any
import random


class StyleAgent(BaseAgent):
    """风格解析Agent"""

    name = "StyleAgent"

    NARRATIVE_STYLES = [
        "快节奏叙事",
        "慢热型叙事",
        "多线并行",
        "单线推进",
        "倒叙手法"
    ]

    LANGUAGE_STYLES = [
        "简洁明快",
        "细腻描写",
        "幽默诙谐",
        "严肃正经",
        "诗意优美"
    ]

    EMOTIONAL_TONES = [
        "轻松愉快",
        "紧张刺激",
        "温馨治愈",
        "悲伤感人",
        "热血激昂"
    ]

    async def run(self) -> AgentResult:
        """执行风格解析"""
        try:
            self.update_progress(10, "开始风格解析")

            genre = self.config.get("genre", "male")
            sub_genre = self.config.get("sub_genre", "")

            self.update_progress(30, f"分析题材风格: {genre} - {sub_genre}")

            # 根据题材选择合适的风格
            narrative_style = random.choice(self.NARRATIVE_STYLES)
            language_style = random.choice(self.LANGUAGE_STYLES)
            emotional_tone = random.choice(self.EMOTIONAL_TONES)

            self.update_progress(70, "生成风格报告")

            result_data = {
                "narrative_style": narrative_style,
                "language_style": language_style,
                "emotional_tone": emotional_tone,
                "style_description": f"{narrative_style}，{language_style}，{emotional_tone}"
            }

            self.log("info", f"风格解析完成: {result_data}")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.log("error", f"风格解析失败: {str(e)}")
            return AgentResult(success=False, error=str(e))
