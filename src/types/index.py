from typing import List, Dict, Any

class Post:
    def __init__(self, title: str, content: str, excerpt: str, tags: List[str], category: str):
        self.title = title
        self.content = content
        self.excerpt = excerpt
        self.tags = tags
        self.category = category

class Tag:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Category:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class ApiResponse:
    def __init__(self, status: str, data: Any):
        self.status = status
        self.data = data

class ContentFormat:
    def __init__(self, html_content: str, meta_description: str):
        self.html_content = html_content
        self.meta_description = meta_description