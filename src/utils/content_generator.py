import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        if self.provider == 'openai':
            self.client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url=os.getenv('OPENAI_BASE_URL')
            )
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        elif self.provider == 'deepseek':
            self.client = OpenAI(
                api_key=os.getenv('DEEPSEEK_API_KEY'),
                base_url=os.getenv('DEEPSEEK_API_BASE')
            )
            self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
        else:
            raise ValueError("Unsupported AI_PROVIDER")

    def generate_content(self, prompt, title):
        sys_msg = (
            "你是一位资深技术写作者。请根据题目和写作要求，生成一篇完整的技术博客文章。"
            "正文请用 HTML 格式输出，合适位置插入相关配图（<img>标签，图片地址可用示例或主题相关网络图片）。"
            "输出严格为 JSON，字段："
            "{\n"
            "  \"content\": string  // 正文 HTML，不要包含主标题H1/H2；小节用二级/三级标题; 段落紧凑, 有示例/步骤;\n"
            "  \"meta_description\": string  // 120~160字;\n"
            "  \"tags\": [string, ...]       // 3-8 个, 中文优先;\n"
            "  \"category\": string          // 单一分类, 中文;\n"
            "}"
        )
        user_msg = (
            f"题目：{title}\n"
            f"写作要求：{prompt}\n"
            "注意：不要把主标题写进正文；小节标题可以使用 '## ' 或 '### '。"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=2200,
                temperature=0.5,
            )
            raw = resp.choices[0].message.content
            import json, re
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group())
                return {
                    "content": data.get("content"),
                    "meta_description": data.get("meta_description"),
                    "tags": data.get("tags", []),
                    "category": data.get("category")
                }
        except Exception as e:
            print(f"AI生成失败: {e}")
        return {}

    def format_content(self, content):
        # 处理内容格式，例如去除多余的空格或标签
        return content.strip()

    def refine_content(self, content):
        """
        使用 AI 对内容进行润色，使其更流畅、专业，避免口水话和逻辑跳跃。
        支持自定义提示词 refine_prompt.txt。
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "../../refine_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                sys_msg = f.read().strip()
        else:
            sys_msg = (
                "你是专业技术编辑，请对以下内容进行润色，使其更流畅、专业，逻辑清晰，避免口水话和逻辑跳跃。"
                "只返回润色后的内容，保持原有格式。"
            )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": content}
                ],
                max_tokens=1800,
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"润色失败: {e}")
            return content