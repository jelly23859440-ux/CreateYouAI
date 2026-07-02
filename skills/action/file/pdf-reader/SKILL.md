---
name: PDF 读取器
layer: action
category: file
status: unverified
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
| 图片提取 | 提取 PDF 中嵌入的图片（JPEG/PNG） |
| 加密 PDF | 支持密码解密 |

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

def read_pdf_text(
    pdf_path: str, 
    password: Optional[str] = None
) -> dict:
    """
    读取 PDF 全部文本。
    
    Args:
        pdf_path: PDF 文件路径
        password: PDF 密码（加密 PDF 需要）
    
    Returns:
        {
            "filename": str,
            "total_pages": int,
            "metadata": dict,
            "pages": [{"page": int, "text": str}, ...]
        }
    """
    reader = PdfReader(pdf_path)
    
    # 处理加密 PDF
    if reader.is_encrypted:
        if not password:
            return {"error": "PDF 已加密，需要提供 password 参数"}
        reader.decrypt(password)
    
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
    
    # 加密 PDF
    result = read_pdf_text("encrypted.pdf", password="1234")
```

### 提取指定页

```python
def read_pdf_pages(
    pdf_path: str, 
    pages: List[int],
    password: Optional[str] = None
) -> List[dict]:
    """
    读取指定页码的内容（页码从 1 开始）。
    
    Args:
        pdf_path: PDF 文件路径
        pages: 要提取的页码列表，如 [1, 3, 5]
        password: PDF 密码（加密 PDF 需要）
    
    Returns:
        [{"page": int, "text": str}, ...]
    """
    reader = PdfReader(pdf_path)
    
    # 处理加密 PDF
    if reader.is_encrypted:
        if not password:
            return [{"page": p, "text": "[PDF 已加密]"} for p in pages]
        reader.decrypt(password)
    
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

def extract_images(
    pdf_path: str, 
    output_dir: str = "pdf_images",
    password: Optional[str] = None
) -> List[dict]:
    """
    提取 PDF 中嵌入的图片。
    
    注意：仅支持 JPEG/PNG 等常见格式。
    扫描版 PDF（图片为 CCITT/JBIG2/JPEG2000）需要 OCR 处理。
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 图片保存目录
        password: PDF 密码（加密 PDF 需要）
    
    Returns:
        [{"page": int, "image_index": int, "path": str, "width": int, "height": int, "error": str}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    
    # 处理加密 PDF
    if reader.is_encrypted:
        if not password:
            return [{"error": "PDF 已加密，需要提供 password 参数"}]
        reader.decrypt(password)
    
    extracted = []
    
    for page_num, page in enumerate(reader.pages):
        image_index = 0
        
        # 安全获取 Resources 对象
        resources = page.get("/Resources")
        if resources:
            # 处理 IndirectObject 解引用
            if hasattr(resources, 'get_object'):
                resources = resources.get_object()
            
            if "/XObject" in resources:
                x_objects = resources["/XObject"]
                if hasattr(x_objects, 'get_object'):
                    x_objects = x_objects.get_object()
                
                for obj_name in x_objects:
                    obj = x_objects[obj_name]
                    if hasattr(obj, 'get_object'):
                        obj = obj.get_object()
                    
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
                                "error": None,
                            })
                            image_index += 1
                        except Exception as e:
                            # 记录失败信息，不静默跳过
                            extracted.append({
                                "page": page_num + 1,
                                "image_index": image_index,
                                "path": None,
                                "width": 0,
                                "height": 0,
                                "error": str(e),
                            })
                            image_index += 1
    
    return extracted

# 使用示例
if __name__ == "__main__":
    images = extract_images("document.pdf", "output_images")
    for img in images:
        if img.get("error"):
            print(f"第 {img['page']} 页, 图片 {img['image_index']}: 提取失败 - {img['error']}")
        else:
            print(f"第 {img['page']} 页, 图片 {img['image_index']}: {img['path']}")
```

### 快速摘要

```python
def pdf_summary(pdf_path: str, password: Optional[str] = None) -> str:
    """生成 PDF 的简要摘要"""
    result = read_pdf_text(pdf_path, password)
    
    if "error" in result:
        return f"错误: {result['error']}"
    
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

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'pypdf'` | 未安装依赖 | `pip install pypdf Pillow` |
| 提取的文本为空或乱码 | 扫描版 PDF 或特殊编码 | 使用 OCR 工具（如 Tesseract） |
| `PdfReadError: EOF marker not found` | PDF 文件损坏 | 检查文件完整性 |
| `PdfReadError: File has not been decrypted` | 加密 PDF | 传入 `password` 参数 |
| 图片提取失败 | 特殊压缩格式（CCITT/JBIG2） | 仅支持 JPEG/PNG，其他需 OCR |
| `TypeError` on Resources | IndirectObject 未解引用 | 代码已用 `get_object()` 处理 |

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| pypdf | 3.17+ | PDF 解析 |
| Pillow | 10.0+ | 图片提取（可选） |

## 图片格式说明

本工具支持 JPEG/PNG 等常见格式的图片提取。以下格式**不支持**：
- CCITT（传真格式）
- JBIG2（黑白扫描）
- JPEG2000
- 矢量图（PDF 绘图）

扫描版 PDF 中的图片通常是以上格式，需要使用 OCR 工具（如 Tesseract）处理。
