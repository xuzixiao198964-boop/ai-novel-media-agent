# -*- coding: utf-8 -*-
"""趋势分析Agent"""
from app.agents.base import BaseAgent, AgentResult
from typing import Dict, Any
import random


class TrendAgent(BaseAgent):
    """热门趋势分析Agent"""

    name = "TrendAgent"

    GENRES = {
        "children": ["0-3岁启蒙", "3-6岁童话", "6-9岁冒险", "9-12岁成长", "12+青少年"],
        "male": ["玄幻", "仙侠", "军事", "都市", "科幻", "历史"],
        "female": ["古代言情", "现代言情", "霸总", "悬疑推理", "纯爱", "宫斗"]
    }

    LENGTH_CONFIG = {
        "micro": {"min_chapters": 1, "max_chapters": 5, "words_per_chapter": 1000},
        "short": {"min_chapters": 5, "max_chapters": 30, "words_per_chapter": 1500},
        "medium": {"min_chapters": 30, "max_chapters": 100, "words_per_chapter": 2000},
        "long": {"min_chapters": 100, "max_chapters": 500, "words_per_chapter": 3000},
        "super_long": {"min_chapters": 500, "max_chapters": 2000, "words_per_chapter": 3000}
    }

    async def run(self) -> AgentResult:
        """执行趋势分析"""
        try:
            self.update_progress(10, "开始趋势分析")

            genre = self.config.get("genre", "random")
            sub_genre = self.config.get("sub_genre", "random")
            length_type = self.config.get("length_type", "random")

            if genre == "random":
                genre = random.choice(["children", "male", "female"])

            if sub_genre == "random" and genre in self.GENRES:
                sub_genre = random.choice(self.GENRES[genre])

            if length_type == "random":
                length_type = random.choice(["micro", "short", "medium", "long"])

            self.update_progress(50, f"分析题材: {genre} - {sub_genre}")

            length_config = self.LENGTH_CONFIG.get(length_type, self.LENGTH_CONFIG["medium"])
            suggested_chapters = random.randint(
                length_config["min_chapters"],
                length_config["max_chapters"]
            )

            self.update_progress(80, f"建议章节数: {suggested_chapters}")

            result_data = {
                "genre": genre,
                "sub_genre": sub_genre,
                "length_type": length_type,
                "suggested_chapters": suggested_chapters,
                "words_per_chapter": length_config["words_per_chapter"],
                "estimated_total_words": suggested_chapters * length_config["words_per_chapter"]
            }

            self.log("info", f"趋势分析完成: {result_data}")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.log("error", f"趋势分析失败: {str(e)}")
            return AgentResult(success=False, error=str(e))
