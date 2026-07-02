---
name: Web 抓取 + Markdown 转换
layer: action
category: web
description: >
  抓取网页内容，转换为 Markdown 格式。
  当用户想要获取网页内容、提取文章正文、将网页转为 Markdown、
  或需要网页数据抓取时触发。
  关键词：web fetch、网页抓取、网页转 Markdown、scrape、crawl、网页内容提取。
---

# Web 抓取 + Markdown 转换

抓取任意 URL 的 HTML 内容，提取正文并转换为干净的 Markdown。

## 能力概览

| 能力 | 说明 |
|------|------|
| URL 抓取 | 支持 HTTP/HTTPS，自动处理重定向 |
| HTML 转 Markdown | 提取正文，去除广告/导航等噪音 |
| 缓存控制 | 支持本地缓存，避免重复请求 |
| 错误处理 | 网络超时、404、编码异常的优雅处理 |

## 前置条件

- Python 3.8+
- pip 包管理器

## 安装步骤

```bash
pip install requests beautifulsoup4 markdownify
```

验证安装：

```bash
python -c "import requests, bs4, markdownify; print('OK')"
```

## 使用方法

### 基础用法：抓取并转 Markdown

```python
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Optional

def fetch_url(
    url: str,
    timeout: int = 10,
    user_agent: str = "Mozilla/5.0 (compatible; WebFetchSkill/1.0)"
) -> dict:
    """
    抓取 URL 并返回结构化结果。

    Returns:
        {"url": str, "status": int, "html": str, "title": str, "error": str|None}
    """
    headers = {"User-Agent": user_agent}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return {
            "url": resp.url,
            "status": resp.status_code,
            "html": resp.text,
            "title": _extract_title(resp.text),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"url": url, "status": 0, "html": "", "title": "", "error": "请求超时"}
    except requests.exceptions.HTTPError as e:
        return {"url": url, "status": resp.status_code, "html": "", "title": "", "error": f"HTTP {resp.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "status": 0, "html": "", "title": "", "error": str(e)}

def _extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else ""

def extract_main_content(html: str) -> str:
    """从 HTML 中提取正文内容，去除导航/页脚等噪音"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["nav", "footer", "header", "aside", "script", "style"]):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=lambda c: c and ("content" in c.lower() or "article" in c.lower()))
        or soup.find("body")
    )
    return str(main) if main else str(soup)

def html_to_markdown(html: str) -> str:
    """将 HTML 转换为 Markdown"""
    main_html = extract_main_content(html)
    return md(main_html, heading_style="ATX", strip=["img", "input"]).strip()

def fetch_as_markdown(url: str, timeout: int = 10) -> dict:
    """
    一步完成：抓取 URL 并转为 Markdown。

    Returns:
        {"url": str, "title": str, "markdown": str, "error": str|None}
    """
    result = fetch_url(url, timeout=timeout)
    if result["error"]:
        return {"url": url, "title": "", "markdown": "", "error": result["error"]}

    markdown = html_to_markdown(result["html"])
    return {"url": result["url"], "title": result["title"], "markdown": markdown, "error": None}

# 使用示例
if __name__ == "__main__":
    result = fetch_as_markdown("https://example.com")
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"# {result['title']}\n")
        print(result["markdown"][:2000])
```

### 进阶：带缓存的抓取

```python
import os
import json
import hashlib
import time

CACHE_DIR = ".web_cache"

def _cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

def fetch_with_cache(
    url: str,
    timeout: int = 10,
    max_age: int = 3600
) -> dict:
    """带本地文件缓存的抓取"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _cache_key(url)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if time.time() - cached["timestamp"] < max_age:
            return cached["result"]

    result = fetch_as_markdown(url, timeout=timeout)
    cache_data = {"timestamp": time.time(), "result": result}
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    return result

# 使用示例
if __name__ == "__main__":
    result = fetch_with_cache("https://example.com", max_age=7200)
    if not result["error"]:
        print(result["markdown"][:1000])
```

### 批量抓取

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_multiple(urls: list, max_workers: int = 5) -> list:
    """并发抓取多个 URL"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(fetch_as_markdown, url): url for url in urls}
        for future in as_completed(future_map):
            url = future_map[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({"url": url, "title": "", "markdown": "", "error": str(e)})
    return results

# 使用示例
if __name__ == "__main__":
    urls = ["https://example.com", "https://httpbin.org/html"]
    results = fetch_multiple(urls)
    for r in results:
        print(f"{r['url']}: {'OK' if not r['error'] else r['error']}")
```

## 问题排查

### 问题 1：`ModuleNotFoundError: No module named 'requests'`

**原因**：未安装依赖。

**解决**：`pip install requests beautifulsoup4 markdownify`

### 问题 2：`ConnectionError` 或超时

**原因**：网络不通或目标服务器拒绝连接。

**解决**：检查网络，增大 `timeout` 参数，或检查目标 URL 是否需要代理。

### 问题 3：抓取到空内容或乱码

**原因**：目标页面使用 JavaScript 动态渲染，或编码检测失败。

**解决**：此工具仅支持静态 HTML。对于 SPA 页面，需要使用 Playwright/Selenium 等工具。

### 问题 4：Markdown 格式混乱

**原因**：目标 HTML 结构不规范，正文提取失败。

**解决**：手动指定 CSS 选择器，如 `soup.find("div", id="article-body")`。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| requests | 2.28+ | 必需 |
| beautifulsoup4 | 4.12+ | 必需 |
| markdownify | 0.11+ | 必需 |
