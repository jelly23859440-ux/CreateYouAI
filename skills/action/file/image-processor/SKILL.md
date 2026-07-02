---
name: image-processor
layer: action
category: file
status: unverified
description: 图片处理工具，支持格式转换、缩放、裁剪、水印、元数据读取
version: 1.0.0
author: CreateYouAI
tags: [image, processing, resize, crop, format, batch]
requirements: [Pillow]
platform: [windows, linux, macos]
difficulty: beginner
---

# Image Processor (图片处理器)

图片处理工具，支持裁剪、缩放、格式转换和批量处理。

## 功能特性

- 图片缩放（保持宽高比）
- 图片裁剪
- 格式转换（PNG, JPG, WEBP, BMP 等）
- 批量处理
- 添加水印
- 图片压缩
- 获取图片信息

## 安装依赖

```bash
pip install Pillow
```

## 使用方法

### 命令行使用

```bash
# 缩放图片
python image_processor.py resize input.jpg output.jpg --width 800

# 裁剪图片
python image_processor.py crop input.jpg output.jpg --box "100,100,400,300"

# 格式转换
python image_processor.py convert input.png output.jpg

# 批量处理
python image_processor.py batch ./input_folder ./output_folder --width 640

# 添加水印
python image_processor.py watermark input.jpg output.jpg --text "© 2024"

# 压缩图片
python image_processor.py compress input.jpg output.jpg --quality 85
```

### Python 代码示例

```python
"""
image_processor.py - 图片处理工具
支持裁剪、缩放、格式转换和批量处理
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Tuple, Optional, List
from pathlib import Path
import os


class ImageProcessor:
    """图片处理器"""
    
    # 支持的格式
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.webp', '.tiff', '.ico'
    }
    
    def __init__(self):
        """初始化处理器"""
        pass
    
    def resize(
        self,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_ratio: bool = True
    ) -> Image.Image:
        """
        缩放图片
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            width: 目标宽度
            height: 目标高度
            maintain_ratio: 是否保持宽高比
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            
            if width and height and not maintain_ratio:
                new_size = (width, height)
            elif width:
                ratio = width / original_width
                height = int(original_height * ratio)
                new_size = (width, height)
            elif height:
                ratio = height / original_height
                width = int(original_width * ratio)
                new_size = (width, height)
            else:
                new_size = img.size
            
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            resized_img.save(output_path)
            
            return resized_img
    
    def crop(
        self,
        input_path: str,
        output_path: str,
        box: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        裁剪图片
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            box: 裁剪区域 (left, top, right, bottom)
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            cropped_img = img.crop(box)
            cropped_img.save(output_path)
            
            return cropped_img
    
    def convert(
        self,
        input_path: str,
        output_path: str,
        quality: int = 95
    ) -> Image.Image:
        """
        格式转换
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            quality: 输出质量 (1-100)
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            # 如果目标格式不支持 alpha 通道，转换为 RGB
            output_format = Path(output_path).suffix.lower()
            if output_format in ('.jpg', '.jpeg', '.bmp') and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            save_kwargs = {}
            if output_format in ('.jpg', '.jpeg', '.webp'):
                save_kwargs['quality'] = quality
            
            img.save(output_path, **save_kwargs)
            
            return img
    
    def add_watermark(
        self,
        input_path: str,
        output_path: str,
        text: str,
        position: str = "bottom-right",
        opacity: int = 128,
        font_size: int = 24
    ) -> Image.Image:
        """
        添加文字水印
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            text: 水印文字
            position: 位置 (top-left, top-right, bottom-left, bottom-right, center)
            opacity: 不透明度 (0-255)
            font_size: 字体大小
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            # 转换为 RGBA 以支持透明度
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建水印层
            txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            # 尝试加载字体
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            
            # 获取文字大小
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            width, height = img.size
            padding = 20
            
            positions = {
                "top-left": (padding, padding),
                "top-right": (width - text_width - padding, padding),
                "bottom-left": (padding, height - text_height - padding),
                "bottom-right": (width - text_width - padding, height - text_height - padding),
                "center": ((width - text_width) // 2, (height - text_height) // 2),
            }
            
            x, y = positions.get(position, positions["bottom-right"])
            
            # 绘制文字
            draw.text((x, y), text, fill=(255, 255, 255, opacity), font=font)
            
            # 合并图层
            watermarked = Image.alpha_composite(img, txt_layer)
            watermarked = watermarked.convert('RGB')
            watermarked.save(output_path)
            
            return watermarked
    
    def compress(
        self,
        input_path: str,
        output_path: str,
        quality: int = 85,
        optimize: bool = True
    ) -> Image.Image:
        """
        压缩图片
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            quality: 压缩质量 (1-100)
            optimize: 是否优化
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            # 转换为 RGB（如果是 PNG 等）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(
                output_path,
                quality=quality,
                optimize=optimize
            )
            
            return img
    
    def get_info(self, image_path: str) -> dict:
        """
        获取图片信息
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片信息字典
        """
        with Image.open(image_path) as img:
            file_size = os.path.getsize(image_path)
            
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "file_size": file_size,
                "file_size_kb": file_size / 1024,
                "file_size_mb": file_size / (1024 * 1024),
            }
    
    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        operation: str = "resize",
        **kwargs
    ) -> List[str]:
        """
        批量处理目录中的图片
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            operation: 操作类型 (resize, convert, compress)
            **kwargs: 操作参数
            
        Returns:
            处理的文件列表
        """
        os.makedirs(output_dir, exist_ok=True)
        processed_files = []
        
        input_path = Path(input_dir)
        
        for img_file in input_path.iterdir():
            if img_file.suffix.lower() not in self.SUPPORTED_FORMATS:
                continue
            
            output_file = Path(output_dir) / img_file.name
            
            try:
                if operation == "resize":
                    self.resize(
                        str(img_file),
                        str(output_file),
                        width=kwargs.get('width'),
                        height=kwargs.get('height')
                    )
                elif operation == "convert":
                    target_format = kwargs.get('format', '.jpg')
                    output_file = output_file.with_suffix(target_format)
                    self.convert(str(img_file), str(output_file))
                elif operation == "compress":
                    self.compress(
                        str(img_file),
                        str(output_file),
                        quality=kwargs.get('quality', 85)
                    )
                
                processed_files.append(str(output_file))
                print(f"✓ 处理完成: {img_file.name}")
            
            except Exception as e:
                print(f"✗ 处理失败: {img_file.name} - {e}")
        
        return processed_files
    
    def resize_to_fit(
        self,
        input_path: str,
        output_path: str,
        max_width: int,
        max_height: int
    ) -> Image.Image:
        """
        缩放图片以适应指定尺寸（保持比例，不超过限制）
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            处理后的图片对象
        """
        with Image.open(input_path) as img:
            width, height = img.size
            
            # 计算缩放比例
            ratio = min(max_width / width, max_height / height)
            
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            img.save(output_path)
            
            return img
    
    def create_thumbnail(
        self,
        input_path: str,
        output_path: str,
        size: Tuple[int, int] = (128, 128)
    ) -> Image.Image:
        """
        创建缩略图
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            size: 缩略图尺寸
            
        Returns:
            缩略图对象
        """
        with Image.open(input_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path)
            
            return img


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="图片处理工具")
    parser.add_argument("action", choices=["resize", "crop", "convert", "compress", "info", "batch", "watermark"])
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("output", nargs="?", help="输出文件或目录")
    parser.add_argument("--width", type=int, help="目标宽度")
    parser.add_argument("--height", type=int, help="目标高度")
    parser.add_argument("--box", help="裁剪区域: left,top,right,bottom")
    parser.add_argument("--quality", type=int, default=85, help="输出质量")
    parser.add_argument("--text", help="水印文字")
    parser.add_argument("--format", help="目标格式")
    
    args = parser.parse_args()
    
    processor = ImageProcessor()
    
    if args.action == "info":
        info = processor.get_info(args.input)
        for key, value in info.items():
            print(f"{key}: {value}")
    
    elif args.action == "resize":
        processor.resize(args.input, args.output, width=args.width, height=args.height)
        print(f"缩放完成: {args.output}")
    
    elif args.action == "crop":
        box = tuple(map(int, args.box.split(',')))
        processor.crop(args.input, args.output, box)
        print(f"裁剪完成: {args.output}")
    
    elif args.action == "convert":
        processor.convert(args.input, args.output)
        print(f"转换完成: {args.output}")
    
    elif args.action == "compress":
        processor.compress(args.input, args.output, quality=args.quality)
        print(f"压缩完成: {args.output}")
    
    elif args.action == "watermark":
        processor.add_watermark(args.input, args.output, args.text)
        print(f"水印添加完成: {args.output}")
    
    elif args.action == "batch":
        processor.batch_process(
            args.input, args.output,
            operation="resize",
            width=args.width,
            height=args.height
        )
```

## 使用示例

```python
from image_processor import ImageProcessor

processor = ImageProcessor()

# 获取图片信息
info = processor.get_info("photo.jpg")
print(f"尺寸: {info['width']}x{info['height']}")
print(f"大小: {info['file_size_kb']:.1f} KB")

# 缩放图片
processor.resize("photo.jpg", "resized.jpg", width=800)

# 裁剪图片
processor.crop("photo.jpg", "cropped.jpg", (100, 100, 400, 300))

# 格式转换
processor.convert("photo.png", "photo.jpg", quality=90)

# 批量处理
processor.batch_process(
    "./photos",
    "./output",
    operation="resize",
    width=640
)

# 添加水印
processor.add_watermark("photo.jpg", "watermarked.jpg", "© 2024 MyBrand")
```

## 故障排除

### 问题：Pillow 未安装
```
错误: ModuleNotFoundError: No module named 'PIL'
```
**解决**: 安装 Pillow
```bash
pip install Pillow
```

### 问题：不支持的图片格式
```
错误: OSError: cannot identify image file
```
**解决**: 检查文件格式是否支持，或文件是否损坏

### 问题：内存不足（处理大图）
```
错误: MemoryError
```
**解决**: 使用流式处理或减小图片尺寸

### 问题：权限错误
```
错误: PermissionError: [Errno 13] Permission denied
```
**解决**: 检查文件写入权限，关闭占用文件的程序

## 参考链接

- [Pillow 官方文档](https://pillow.readthedocs.io/)
- [支持的图片格式](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)
