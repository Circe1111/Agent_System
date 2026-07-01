import os
import json


class PromptManager:
    def __init__(self):
        self.prompts = {}
        self._load_prompts()

    def _load_prompts(self):
        data_path = os.path.join("数据", "数据", "Prompt模板", "prompt_templates.json")
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for prompt in data.get("prompts", []):
                    self.prompts[prompt["id"]] = prompt
            print(f">>> 加载Prompt模板: {len(self.prompts)} 个")
        else:
            print(">>> 未找到Prompt模板文件，使用默认模板")
            self._load_default_prompts()

    def _load_default_prompts(self):
        self.prompts = {
            "P001": {
                "id": "P001",
                "name": "讲义生成",
                "role": "你是一位Python程序设计课程的资深教师",
                "task": "请根据以下主题生成一份详细的讲义",
                "template": "你是一位Python程序设计课程的资深教师。请根据主题「{topic}」生成一份适合大学生学习的讲义。要求：1) 内容由浅入深 2) 包含代码示例 3) 包含常见错误说明 4) 包含课后思考题。主题：{topic}",
                "variables": ["topic"]
            },
            "P004": {
                "id": "P004",
                "name": "学习建议生成",
                "role": "你是一位个性化学习顾问",
                "task": "根据学生画像生成个性化学习建议",
                "template": "请根据以下学生画像生成个性化的学习建议：\n学生姓名：{name}\n专业：{major}\n课程：{course}\n学习目标：{goal}\n知识基础：{base}\n学习偏好：{preference}\n薄弱知识：{weakness}\n学习时间：{time}\n\n请提供：1) 学习计划建议 2) 重点突破方向 3) 学习资源推荐 4) 每周时间安排建议",
                "variables": ["name", "major", "course", "goal", "base", "preference", "weakness", "time"]
            },
            "P009": {
                "id": "P009",
                "name": "知识点讲解",
                "role": "你是一位擅长用例子讲解的Python教师",
                "task": "用通俗易懂的方式讲解指定知识点",
                "template": "请用通俗易懂的方式讲解「{topic}」。要求：1) 用生活中的类比引入 2) 给出至少3个代码示例 3) 给出常见误区和注意事项 4) 出一道自测题。知识点：{topic}",
                "variables": ["topic"]
            },
            "P012": {
                "id": "P012",
                "name": "学习路径规划",
                "role": "你是一位学习规划师",
                "task": "为不同起点的学生规划学习路径",
                "template": "请为{target_audience}规划一份学习Python的路径。起点水平：{start_level}。目标水平：{target_level}。可用时间：{available_time}。请按周给出学习计划，包含每周学习内容、练习项目和参考资料。",
                "variables": ["target_audience", "start_level", "target_level", "available_time"]
            },
            "P018": {
                "id": "P018",
                "name": "知识问答",
                "role": "你是一位Python知识库问答助手",
                "task": "回答学生关于Python的提问",
                "template": "学生提问：{question}\n\n请用清晰易懂的方式回答。如果问题涉及代码，请给出代码示例。如果问题涉及概念，请用类比帮助理解。",
                "variables": ["question"]
            },
            "P002": {
                "id": "P002",
                "name": "习题生成",
                "role": "你是一位Python出题专家",
                "task": "请生成一份关于指定知识点的练习题",
                "template": "请生成关于「{topic}」的{count}道练习题。题型包括选择题、填空题和编程题。每道题需要包含：题目、答案、解析。难度层级：{difficulty}。知识点：{topic}",
                "variables": ["topic", "count", "difficulty"]
            }
        }

    def get_prompt(self, prompt_id):
        return self.prompts.get(prompt_id)

    def render_prompt(self, prompt_id, **kwargs):
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return None
        try:
            return prompt["template"].format(**kwargs)
        except KeyError as e:
            print(f">>> Prompt渲染失败，缺少变量: {e}")
            return None

    def get_all_prompts(self):
        return list(self.prompts.values())

    def get_prompts_by_scenario(self, scenario):
        return [p for p in self.prompts.values() if scenario.lower() in p.get("usage_scenario", "").lower()]

    def search_prompts(self, keyword):
        results = []
        keyword = keyword.lower()
        for prompt in self.prompts.values():
            if (keyword in prompt.get("name", "").lower() or
                keyword in prompt.get("task", "").lower() or
                keyword in prompt.get("usage_scenario", "").lower()):
                results.append(prompt)
        return results


prompt_manager = PromptManager()