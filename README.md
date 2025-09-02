# wp-content-generator

本项目是一个自动化的 WordPress 内容生成与发布工具，结合 AI 大模型（支持 OpenAI 和 DeepSeek）、MySQL 数据库和 WordPress REST API，实现技术博客内容的自动生成、润色、标签/分类归类及草稿发布。适用于技术站点、自媒体、内容运营等场景。

## 项目结构

- **src/main.py**: 主流程入口，负责初始化应用、批量内容生成与发布。
- **src/api/wordpress_api.py**: WordPress API 封装，包含文章发布、标签和分类查找等方法。
- **src/utils/content_generator.py**: AI内容生成与润色工具，负责调用大模型生成结构化内容并优化。
- **requirements.txt**: Python依赖包列表。
- **.env**: 环境变量配置（数据库、WordPress、AI接口等）。
- **prompts.txt**: 内容生成提示词。
- **refine_prompt.txt**: 润色提示词（可选）。

## 安装与配置

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd wp-content-generator
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量 `.env`，填写数据库、WordPress、AI接口等信息：
   ```env
   WP_URL=<your_wordpress_url>
   WP_USERNAME=<your_username>
   WP_APP_PASSWORD=<your_app_password>
   DB_USER=<your_db_user>
   DB_PASSWORD=<your_db_password>
   DB_HOST=<your_db_host>
   DB_NAME=<your_db_name>
   ```

4. 数据库建表 SQL（MySQL）：
   ```sql
   CREATE TABLE articles (
     id INT PRIMARY KEY AUTO_INCREMENT,
     title VARCHAR(255) NOT NULL,
     publish_date DATE NOT NULL,
     published TINYINT(1) DEFAULT 0,
     published_at DATETIME DEFAULT NULL
   );
   ```

5. 编辑 `prompts.txt`，自定义内容生成要求。可选 `refine_prompt.txt` 定义润色要求。

## 使用方法

在虚拟环境下运行主程序：

```bash
python src/main.py
```

程序会自动读取数据库中当天未发布的文章标题，调用 AI 生成结构化内容（HTML），自动归类标签和分类，并发布为 WordPress 草稿，便于人工审核。

## 关键特性

- 支持 AI 自动生成 HTML 格式内容，适配 WordPress 古腾堡编辑器
- 内容自动润色，提升专业性和可读性
- 标签自动查找或创建，分类仅归入已存在目录
- 支持自定义提示词和润色提示词
- 日志记录与异常处理，便于监控和排查

## 注意事项

- 分类（目录）只使用 WordPress 已有分类，不自动新建
- 标签可自动创建，分类不可自动创建
- 内容生成和润色均可自定义提示词，提升个性化和专业性
- 所有内容先发布为草稿，便于人工审核和修改

## 适用场景

- 技术博客自动化运营
- 自媒体内容批量生成与发布
- 企业知识库自动填充
- SEO内容自动生成

如需定制功能或扩展支持，请联系项目维护