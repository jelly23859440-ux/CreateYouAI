---
name: csv-json-converter
category: file
description: CSV 和 JSON 格式互相转换，支持大文件流式处理
version: 1.0.0
author: CreateYouAI
tags: [csv, json, converter, data, streaming]
requirements: []
platform: [windows, linux, macos]
difficulty: beginner
---

# CSV/JSON Converter (数据转换工具)

CSV 和 JSON 格式互相转换，支持大文件流式处理，内存占用低。

## 功能特性

- CSV → JSON 转换
- JSON → CSV 转换
- 大文件流式处理（不加载全部到内存）
- 自定义分隔符
- 编码支持（UTF-8, GBK 等）
- 批量文件转换

## 安装依赖

无需额外安装，使用 Python 标准库：
- `csv` 模块
- `json` 模块

## 使用方法

### 命令行使用

```bash
# CSV 转 JSON
python csv_json_converter.py csv2json input.csv output.json

# JSON 转 CSV
python csv_json_converter.py json2csv input.json output.csv

# 指定编码
python csv_json_converter.py csv2json input.csv output.json --encoding gbk

# 指定分隔符
python csv_json_converter.py csv2json input.csv output.json --delimiter ";"
```

### Python 代码示例

```python
"""
csv_json_converter.py - CSV/JSON 数据转换工具
支持 CSV 和 JSON 互相转换，大文件流式处理
"""
import csv
import json
import os
from typing import List, Dict, Any, Iterator, Optional
from pathlib import Path
from io import StringIO


class CSVJSONConverter:
    """CSV/JSON 转换器"""
    
    def __init__(self, encoding: str = "utf-8", delimiter: str = ","):
        """
        初始化转换器
        
        Args:
            encoding: 文件编码
            delimiter: CSV 分隔符
        """
        self.encoding = encoding
        self.delimiter = delimiter
    
    def csv_to_json(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        indent: int = 2
    ) -> List[Dict[str, Any]]:
        """
        CSV 转 JSON
        
        Args:
            input_file: CSV 文件路径
            output_file: 输出 JSON 文件路径（可选）
            indent: JSON 缩进
            
        Returns:
            转换后的数据列表
        """
        data = []
        
        with open(input_file, 'r', encoding=self.encoding) as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            for row in reader:
                data.append(dict(row))
        
        if output_file:
            with open(output_file, 'w', encoding=self.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return data
    
    def csv_to_json_streaming(
        self,
        input_file: str,
        output_file: str,
        chunk_size: int = 1000
    ) -> int:
        """
        流式 CSV 转 JSON（适用于大文件）
        
        Args:
            input_file: CSV 文件路径
            output_file: 输出 JSON 文件路径
            chunk_size: 每次处理的行数
            
        Returns:
            处理的总行数
        """
        total_rows = 0
        
        with open(input_file, 'r', encoding=self.encoding) as infile, \
             open(output_file, 'w', encoding=self.encoding) as outfile:
            
            reader = csv.DictReader(infile, delimiter=self.delimiter)
            outfile.write('[\n')
            
            first_chunk = True
            while True:
                chunk = []
                for _ in range(chunk_size):
                    try:
                        row = next(reader)
                        chunk.append(dict(row))
                    except StopIteration:
                        break
                
                if not chunk:
                    break
                
                if not first_chunk:
                    outfile.write(',\n')
                first_chunk = False
                
                for i, item in enumerate(chunk):
                    json_str = json.dumps(item, ensure_ascii=False)
                    if i < len(chunk) - 1:
                        outfile.write(json_str + ',\n')
                    else:
                        outfile.write(json_str)
                
                total_rows += len(chunk)
            
            outfile.write('\n]')
        
        return total_rows
    
    def json_to_csv(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        JSON 转 CSV
        
        Args:
            input_file: JSON 文件路径
            output_file: 输出 CSV 文件路径（可选）
            
        Returns:
            转换后的数据列表
        """
        with open(input_file, 'r', encoding=self.encoding) as f:
            data = json.load(f)
        
        if not data:
            return []
        
        if output_file:
            # 确保数据是列表格式
            if isinstance(data, dict):
                data = [data]
            
            # 获取所有字段名
            fieldnames = list(data[0].keys())
            
            with open(output_file, 'w', encoding=self.encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                writer.writerows(data)
        
        return data
    
    def json_to_csv_streaming(
        self,
        input_file: str,
        output_file: str,
        chunk_size: int = 1000
    ) -> int:
        """
        流式 JSON 转 CSV（适用于大文件）
        
        Args:
            input_file: JSON 文件路径
            output_file: 输出 CSV 文件路径
            chunk_size: 每次处理的行数
            
        Returns:
            处理的总行数
        """
        total_rows = 0
        
        with open(input_file, 'r', encoding=self.encoding) as infile:
            data = json.load(infile)
            
            if isinstance(data, dict):
                data = [data]
            
            if not data:
                return 0
            
            fieldnames = list(data[0].keys())
        
        with open(output_file, 'w', encoding=self.encoding, newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=self.delimiter)
            writer.writeheader()
            
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                writer.writerows(chunk)
                total_rows += len(chunk)
        
        return total_rows
    
    def convert_directory(
        self,
        input_dir: str,
        output_dir: str,
        direction: str = "csv2json"
    ) -> Dict[str, str]:
        """
        批量转换目录中的文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            direction: 转换方向 "csv2json" 或 "json2csv"
            
        Returns:
            {输入文件: 输出文件} 映射
        """
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if direction == "csv2json":
            files = input_path.glob("*.csv")
            for f in files:
                out_file = output_path / f.with_suffix('.json').name
                self.csv_to_json(str(f), str(out_file))
                results[str(f)] = str(out_file)
        
        elif direction == "json2csv":
            files = input_path.glob("*.json")
            for f in files:
                out_file = output_path / f.with_suffix('.csv').name
                self.json_to_csv(str(f), str(out_file))
                results[str(f)] = str(out_file)
        
        return results


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CSV/JSON 转换工具")
    parser.add_argument("direction", choices=["csv2json", "json2csv"])
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("output", help="输出文件或目录")
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--streaming", action="store_true")
    
    args = parser.parse_args()
    
    converter = CSVJSONConverter(
        encoding=args.encoding,
        delimiter=args.delimiter
    )
    
    if args.direction == "csv2json":
        if args.streaming:
            rows = converter.csv_to_json_streaming(args.input, args.output)
            print(f"转换完成: {rows} 行")
        else:
            data = converter.csv_to_json(args.input, args.output)
            print(f"转换完成: {len(data)} 条记录")
    else:
        if args.streaming:
            rows = converter.json_to_csv_streaming(args.input, args.output)
            print(f"转换完成: {rows} 行")
        else:
            data = converter.json_to_csv(args.input, args.output)
            print(f"转换完成: {len(data)} 条记录")
```

## 使用示例

```python
from csv_json_converter import CSVJSONConverter

converter = CSVJSONConverter(encoding="utf-8")

# CSV 转 JSON
data = converter.csv_to_json("data.csv", "data.json")
print(f"转换了 {len(data)} 条记录")

# 大文件流式转换
rows = converter.csv_to_json_streaming("large.csv", "large.json", chunk_size=5000)
print(f"流式转换了 {rows} 行")

# 批量转换
results = converter.convert_directory("./csv_files", "./json_files", "csv2json")
for src, dst in results.items():
    print(f"{src} -> {dst}")
```

## 故障排除

### 问题：编码错误
```
错误: 'utf-8' codec can't decode byte
```
**解决**: 指定正确的编码
```python
converter = CSVJSONConverter(encoding="gbk")
```

### 问题：CSV 格式错误
```
错误: Error: line contains N fields
```
**解决**: 检查 CSV 文件是否使用正确的分隔符
```python
converter = CSVJSONConverter(delimiter=";")
```

### 问题：内存不足
```
错误: MemoryError
```
**解决**: 使用流式处理
```python
converter.csv_to_json_streaming("large.csv", "output.json", chunk_size=1000)
```

## 参考链接

- [Python csv 模块文档](https://docs.python.org/3/library/csv.html)
- [Python json 模块文档](https://docs.python.org/3/library/json.html)
