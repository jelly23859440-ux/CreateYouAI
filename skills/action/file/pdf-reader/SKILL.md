---
name: PDF 读取器
layer: action
category: file
description: >
  读取 PDF 文件，提取文本内容、页面信息和图片。
  当用户想要读取 PDF、提取 PDF 文本、解析 PDF 内容、
  获取 PDF 页数、提取 PDF 中的图片时触发。
  关键词：PDF 读取、PDF 提取、PDF 解析、PDF 转文本、PDF 文本提取。
---

# PDF 读取器

读取 PDF 文件，提取文本、元数据和图片。

## 能力概览

| 能力 | 说明 |
|------|------|
| 文本提取 | 逐页提取 PDF 中的文本内容 |
| 元数据读取 | 标题、作者、创建日期等 |
| 页面信息 | 总页数、指定页内容 |
| 图片提取 | 提取 PDF 中嵌入的图片 |

## 前置条件

- Python 3.8+
- pip 包管理器

## 安装步骤

```bash
pip install pypdf Pillow
```

验证安装：

```bash
python -c "from pypdf import PdfReader; print('OK')"
```

## 使用方法

### 基础用法：提取文本

```python
from pypdf import PdfReader
from typing import List, Optional

def read_pdf_text(pdf_path: str) -> dict:
    """
    读取 PDF 全部文本。

    Returns:
        {
            "filename": str,
            "total_pages": int,
            "metadata": dict,
            "pages": [{"page": int, "text": str}, ...]
        }
    """
    reader = PdfReader(pdf_path)

    metadata = {}
    if reader.metadata:
        metadata = {
            "title": reader.metadata.get("/Title", ""),
            "author": reader.metadata.get("/Author", ""),
            "creator": reader.metadata.get("/Creator", ""),
            "producer": reader.metadata.get("/Producer", ""),
            "creation_date": str(reader.metadata.get("/CreationDate", "")),
        }

    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page": i + 1, "text": text})

    return {
        "filename": pdf_path,
        "total_pages": len(reader.pages),
        "metadata": metadata,
        "pages": pages,
    }

# 使用示例
if __name__ == "__main__":
    result = read_pdf_text("document.pdf")
    print(f"文件: {result['filename']}")
    print(f"页数: {result['total_pages']}")
    print(f"标题: {result['metadata'].get('title', 'N/A')}")
    for page in result["pages"]:
        print(f"\n--- 第 {page['page']} 页 ---")
        print(page["text"][:500])
```

### 提取指定页

```python
def read_pdf_pages(pdf_path: str, pages: List[int]) -> List[dict]:
    """
    读取指定页码的内容（页码从 1 开始）。

    Args:
        pdf_path: PDF 文件路径
        pages: 要提取的页码列表，如 [1, 3, 5]

    Returns:
        [{"page": int, "text": str}, ...]
    """
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    results = []

    for page_num in pages:
        if 1 <= page_num <= total:
            text = reader.pages[page_num - 1].extract_text() or ""
            results.append({"page": page_num, "text": text})
        else:
            results.append({"page": page_num, "text": f"[页码超出范围: 1-{total}]"})

    return results

# 使用示例
if __name__ == "__main__":
    pages = read_pdf_pages("document.pdf", [1, 3])
    for p in pages:
        print(f"第 {p['page']} 页:\n{p['text'][:300]}\n")
```

### 提取图片

```python
import os
from PIL import Image
import io

def extract_images(pdf_path: str, output_dir: str = "pdf_images") -> List[dict]:
    """
    提取 PDF 中嵌入的图片。

    Args:
        pdf_path: PDF 文件路径
        output_dir: 图片保存目录

    Returns:
        [{"page": int, "image_index": int, "path": str, "width": int, "height": int}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    extracted = []

    for page_num, page in enumerate(reader.pages):
        image_index = 0
        if "/XObject" in (page.get("/Resources") or {}):
            x_objects = page["/Resources"]["/XObject"].get_object()
            for obj_name in x_objects:
                obj = x_objects[obj_name].get_object()
                if obj.get("/Subtype") == "/Image":
                    try:
                        width = obj.get("/Width", 0)
                        height = obj.get("/Height", 0)
                        filename = f"page{page_num + 1}_img{image_index}.png"
                        filepath = os.path.join(output_dir, filename)

                        data = obj.get_data()
                        img = Image.open(io.BytesIO(data))
                        img.save(filepath)

                        extracted.append({
                            "page": page_num + 1,
                            "image_index": image_index,
                            "path": filepath,
                            "width": width,
                            "height": height,
                        })
                        image_index += 1
                    except Exception:
                        pass

    return extracted

# 使用示例
if __name__ == "__main__":
    images = extract_images("document.pdf", "output_images")
    for img in images:
        print(f"第 {img['page']} 页, 图片 {img['image_index']}: {img['path']}")
```

### 快速摘要

```python
def pdf_summary(pdf_path: str) -> str:
    """生成 PDF 的简要摘要"""
    result = read_pdf_text(pdf_path)
    lines = [
        f"## PDF 摘要",
        f"- **文件**: {result['filename']}",
        f"- **页数**: {result['total_pages']}",
    ]
    if result["metadata"].get("title"):
        lines.append(f"- **标题**: {result['metadata']['title']}")
    if result["metadata"].get("author"):
        lines.append(f"- **作者**: {result['metadata']['author']}")

    lines.append(f"\n### 文本预览")
    for page in result["pages"][:3]:
        preview = page["text"][:200].replace("\n", " ")
        lines.append(f"\n**第 {page['page']} 页**: {preview}...")

    if result["total_pages"] > 3:
        lines.append(f"\n*（还有 {result['total_pages'] - 3} 页未显示）*")

    return "\n".join(lines)

# 使用示例
if __name__ == "__main__":
    print(pdf_summary("document.pdf"))
```

## 问题排查

### 问题 1：`ModuleNotFoundError: No module named 'pypdf'`

**原因**：未安装依赖。

**解决**：`pip install pypdf Pillow`

### 问题 2：提取的文本为空或乱码

**原因**：PDF 使用扫描图片而非文字图层，或使用了特殊编码。

**解决**：使用 OCR 工具（如 Tesseract）处理扫描版 PDF。

### 问题 3：`PdfReadError: EOF marker not found`

**原因**：PDF 文件损坏或不是有效 PDF。

**解决**：检查文件是否完整，用其他 PDF 阅读器验证。

### 问题 4：图片提取失败

**原因**：PDF 中的图片使用了非标准压缩。

**解决**：pypdf 支持大多数常见格式，少数特殊格式需要专用库。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| pypdf | 3.17+ | 必需 |
| Pillow | 10.0+ | 可选（图片提取时必需） |
