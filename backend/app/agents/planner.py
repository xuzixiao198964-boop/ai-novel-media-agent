# -*- coding: utf-8 -*-
"""策划Agent"""
from app.agents.base import BaseAgent, AgentResult
from typing import Dict, Any, List
import json


class PlannerAgent(BaseAgent):
    """策划Agent - 生成小说大纲"""

    name = "PlannerAgent"

    async def run(self) -> AgentResult:
        """执行策划"""
        try:
            self.update_progress(10, "开始策划")

            # 获取前置Agent的结果
            trend_data = self.config.get("trend_data", {})
            style_data = self.config.get("style_data", {})

            suggested_chapters = trend_data.get("suggested_chapters", 30)
            genre = trend_data.get("genre", "male")
            sub_genre = trend_data.get("sub_genre", "玄幻")

            self.update_progress(30, "生成策划案")

            # 生成策划案
            planning = {
                "title": f"《{self._generate_title(genre, sub_genre)}》",
                "genre": genre,
                "sub_genre": sub_genre,
                "theme": self._generate_theme(genre, sub_genre),
                "protagonist": self._generate_protagonist(genre),
                "world_setting": self._generate_world_setting(genre, sub_genre),
                "conflict": self._generate_conflict(genre),
                "chapters": suggested_chapters
            }

            self.update_progress(60, "生成章节大纲")

            # 生成章节大纲
            chapter_outlines = []
            for i in range(1, min(suggested_chapters + 1, 11)):  # 先生成前10章大纲
                chapter_outlines.append({
                    "chapter": i,
                    "title": f"第{i}章 {self._generate_chapter_title(i, genre)}",
                    "summary": f"第{i}章内容概要",
                    "key_events": [f"事件{j}" for j in range(1, 4)]
                })

            planning["chapter_outlines"] = chapter_outlines

            self.update_progress(90, "策划完成")

            self.log("info", f"策划完成: {planning['title']}")

            return AgentResult(success=True, data=planning)

        except Exception as e:
            self.log("error", f"策划失败: {str(e)}")
            return AgentResult(success=False, error=str(e))

    def _generate_title(self, genre: str, sub_genre: str) -> str:
        """生成标题"""
        titles = {
            "male": ["龙族传说", "星际征途", "武道巅峰", "仙路漫漫"],
            "female": ["霸总的秘密", "穿越之盛世嫡女", "重生之豪门千金", "甜宠日常"],
            "children": ["小兔子的冒险", "魔法森林", "勇敢的小勇士", "星星的故事"]
        }
        import random
        return random.choice(titles.get(genre, ["未命名小说"]))

    def _generate_theme(self, genre: str, sub_genre: str) -> str:
        """生成主题"""
        return f"{sub_genre}题材，讲述主角的成长与冒险"

    def _generate_protagonist(self, genre: str) -> Dict[str, str]:
        """生成主角设定"""
        return {
            "name": "主角",
            "age": "18",
            "personality": "勇敢、坚韧、善良",
            "background": "普通出身，机缘巧合踏上修炼之路"
        }

    def _generate_world_setting(self, genre: str, sub_genre: str) -> str:
        """生成世界观设定"""
        return f"{sub_genre}世界，拥有独特的力量体系和社会结构"

    def _generate_conflict(self, genre: str) -> str:
        """生成核心冲突"""
        return "主角面临强大敌人的威胁，必须不断提升实力"

    def _generate_chapter_title(self, chapter_num: int, genre: str) -> str:
        """生成章节标题"""
        if chapter_num == 1:
            return "初入江湖"
        elif chapter_num == 2:
            return "意外相遇"
        else:
            return f"冒险继续"
