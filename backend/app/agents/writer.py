# -*- coding: utf-8 -*-
"""写作Agent"""
from app.agents.base import BaseAgent, AgentResult
from typing import Dict, Any


class WriterAgent(BaseAgent):
    """写作Agent - 章节创作"""

    name = "WriterAgent"

    async def run(self) -> AgentResult:
        """执行写作"""
        try:
            self.update_progress(10, "开始写作")

            planning = self.config.get("planning", {})
            chapter_num = self.config.get("chapter_num", 1)
            chapter_outlines = planning.get("chapter_outlines", [])

            if chapter_num > len(chapter_outlines):
                return AgentResult(success=False, error="章节编号超出大纲范围")

            outline = chapter_outlines[chapter_num - 1]

            self.update_progress(30, f"写作第{chapter_num}章: {outline['title']}")

            chapter_content = f"""
# {outline['title']}

这是第{chapter_num}章的内容。

{outline['summary']}

（此处应该是完整的章节内容，由AI模型生成）

---
字数: 3000
"""

            self.update_progress(80, f"第{chapter_num}章写作完成")

            result_data = {
                "chapter_num": chapter_num,
                "title": outline["title"],
                "content": chapter_content,
                "word_count": 3000
            }

            self.log("info", f"第{chapter_num}章写作完成")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.log("error", f"写作失败: {str(e)}")
            return AgentResult(success=False, error=str(e))
