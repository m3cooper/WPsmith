import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime


class WordPressAPI:
    def __init__(self, wp_url, username, app_password):
        self.wp_url = wp_url
        self.username = username
        self.app_password = app_password
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.app_password)
        self.session.headers.update({"Content-Type": "application/json; charset=utf-8"})

    def publish_post(self, title, content, tags=None, category_id=None, excerpt=None, article_id=None):
        data = {
            "title": title,
            "content": content,
            "status": "draft",  # 改为草稿  publish 为直接发布
            "tags": tags or [],
            "categories": [category_id] if category_id else []
        }
        if excerpt:
            data["excerpt"] = excerpt
        if article_id:
            slug = f"{datetime.utcnow():%Y%m%d}-{article_id}"
            data["slug"] = slug
        response = self.session.post(f"{self.wp_url}/posts", json=data)
        if response.status_code == 201:
            return response.json().get('id')
        else:
            print(f"Failed to publish post: {response.status_code} {response.text}")
            return None

    def get_terms(self, term_type):
        response = self.session.get(f"{self.wp_url}/{term_type}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get terms: {response.status_code} {response.text}")

    def get_or_create_tag(self, tag_name):
        """查找或创建标签，返回标签ID"""
        if not tag_name:
            return None
        # 查找
        resp = self.session.get(f"{self.wp_url}/tags", params={"search": tag_name})
        if resp.status_code == 200:
            arr = resp.json()
            for t in arr:
                if t.get("name", "").lower() == tag_name.lower():
                    return t["id"]
        # 创建
        resp = self.session.post(f"{self.wp_url}/tags", json={"name": tag_name})
        if resp.status_code in (200, 201):
            return resp.json().get("id")
        return None

    def get_or_create_category(self, category_name):
        """只查找已存在分类，返回分类ID；不存在则返回 None，不自动创建"""
        if not category_name:
            return None
        resp = self.session.get(f"{self.wp_url}/categories", params={"search": category_name})
        if resp.status_code == 200:
            arr = resp.json()
            for c in arr:
                if c.get("name", "").lower() == category_name.lower():
                    return c["id"]
        # 不创建新分类
        return None