import os
import logging
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
from api.wordpress_api import WordPressAPI
from utils.content_generator import ContentGenerator

# 加载环境变量
load_dotenv()

# 日志配置
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

BATCH_LIMIT = int(os.getenv('BATCH_LIMIT', '5'))

def get_posts_to_publish():
    """从数据库获取今天未发布的文章标题和ID"""
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title FROM articles WHERE publish_date = %s AND (published = 0 OR published IS NULL) ORDER BY id ASC LIMIT %s",
            (today, BATCH_LIMIT)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"DB query failed: {e}")
        return []

def mark_article_published(article_id):
    """标记文章已发布"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE articles SET published = 1, published_at = %s WHERE id = %s",
            (datetime.now(), article_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"DB update failed: {e}")

def main():
    logger.info("Starting WordPress content generator...")

    # 初始化 WordPress API
    wp_api = WordPressAPI(
        wp_url=os.getenv('WP_URL'),
        username=os.getenv('WP_USERNAME'),
        app_password=os.getenv('WP_APP_PASSWORD')
    )

    # 初始化内容生成器
    content_generator = ContentGenerator()

    # 批量获取待发布文章
    items = get_posts_to_publish()
    if not items:
        logger.info("No articles to publish today.")
        return

    # 读取提示词
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
    except Exception as e:
        logger.error(f"Prompt file error: {e}")
        return

    # 循环生成并发布
    for item in items:
        title = item['title']
        article_id = item['id']
        logger.info(f"Generating content for: {title}")

        # 生成内容（需支持 tags/category/meta）
        result = content_generator.generate_content(prompt, title)
        if not result or not result.get('content'):
            logger.error("Content generation failed.")
            continue

        # 格式化内容
        content = content_generator.format_content(result['content'])
        tags = result.get('tags', [])
        category = result.get('category')
        meta_desc = result.get('meta_description')

        # WordPress 标签/分类处理
        tag_ids = [wp_api.get_or_create_tag(t) for t in tags if t]
        category_id = wp_api.get_or_create_category(category) if category else None

        # 发布到 WordPress
        post_id = wp_api.publish_post(
            title=title,
            content=content,
            tags=tag_ids,
            category_id=category_id,  # 修正参数名
            excerpt=meta_desc,
            article_id=article_id
        )
        if post_id:
            logger.info(f"Post published: {post_id}")
            mark_article_published(article_id)
        else:
            logger.error("Failed to publish post.")

if __name__ == "__main__":
    main()