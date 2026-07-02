---
name: CSV/JSON 数据转换
layer: action
category: file
status: unverified
description: CSV 和 JSON 格式互相转换，支持大文件流式处理
version: 1.2
requirements:
  - name: ijson
    version: ">=3.0"
    optional: true
    description: "真正的流式 JSON 解析，未安装时 JSON→CSV 流式将无法使用"
---

# CSV/JSON 数据转换

CSV 和 JSON 格式互相转换，支持大文件流式处理，内存占用低。

## 功能特性

- CSV → JSON 转换
- JSON → CSV 转换
- 大文件流式处理（不加载全部到内存）
- 自定义分隔符
- 编码支持（UTF-8, GBK 等）
- 批量文件转换

## 安装依赖

基础功能使用 Python 标准库。流式 JSON→CSV 需要安装 ijson：

```bash
pip install ijson
```

## 使用方法

### Python 代码示例

```python
import csv
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class CSVJSONConverter:
    """CSV/JSON 转换器"""
    
    def __init__(self, encoding: str = "utf-8", delimiter: str = ","):
        self.encoding = encoding
        self.delimiter = delimiter
    
    def csv_to_json(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        indent: int = 2
    ) -> List[Dict[str, Any]]:
        """CSV 转 JSON"""
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
        """流式 CSV 转 JSON（适用于大文件）"""
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
        """JSON 转 CSV"""
        with open(input_file, 'r', encoding=self.encoding) as f:
            data = json.load(f)
        
        # 确保数据是列表格式
        if isinstance(data, dict):
            data = [data]
        
        if output_file:
            if not data:
                # 空数据时创建空文件（只有表头无法确定字段）
                with open(output_file, 'w', encoding=self.encoding) as f:
                    f.write('')
            else:
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
        
        要求输入为标准 JSON 数组格式: [{...}, {...}, ...]
        需要安装 ijson: pip install ijson
        """
        try:
            import ijson
        except ImportError:
            raise ImportError(
                "流式 JSON→CSV 需要安装 ijson：pip install ijson\n"
                "如果文件较小，可以使用 json_to_csv() 代替"
            )
        
        total_rows = 0
        
        with open(input_file, 'r', encoding=self.encoding) as infile, \
             open(output_file, 'w', encoding=self.encoding, newline='') as outfile:
            
            items = ijson.items(infile, 'item')
            
            # 获取第一个 item 确定字段名
            try:
                first_item = next(items)
            except StopIteration:
                # 空数组，创建空文件并返回
                return 0
            
            fieldnames = list(first_item.keys())
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=self.delimiter)
            writer.writeheader()
            writer.writerow(first_item)
            total_rows = 1
            
            # 继续同一个生成器，无需重新打开文件
            chunk = []
            for item in items:
                chunk.append(item)
                if len(chunk) >= chunk_size:
                    writer.writerows(chunk)
                    total_rows += len(chunk)
                    chunk = []
            if chunk:
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
            {输入文件: 输出文件} 映射，错误记录在 "_errors" 键中
        
        Raises:
            ValueError: direction 参数无效
        """
        if direction not in ("csv2json", "json2csv"):
            raise ValueError(f"direction 参数无效: {direction}，必须是 'csv2json' 或 'json2csv'")
        
        os.makedirs(output_dir, exist_ok=True)
        results = {}
        errors = []
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if direction == "csv2json":
            files = input_path.glob("*.csv")
            for f in files:
                try:
                    out_file = output_path / f.with_suffix('.json').name
                    self.csv_to_json(str(f), str(out_file))
                    results[str(f)] = str(out_file)
                except Exception as e:
                    errors.append({"file": str(f), "error": str(e)})
        
        elif direction == "json2csv":
            files = input_path.glob("*.json")
            for f in files:
                try:
                    out_file = output_path / f.with_suffix('.csv').name
                    self.json_to_csv(str(f), str(out_file))
                    results[str(f)] = str(out_file)
                except Exception as e:
                    errors.append({"file": str(f), "error": str(e)})
        
        if errors:
            results["_errors"] = errors
        
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
    parser.add_argument("--streaming", action="store_true", help="流式处理（需要 ijson）")
    
    args = parser.parse_args()
    
    converter = CSVJSONConverter(
        encoding=args.encoding,
        delimiter=args.delimiter
    )
    
    # 检测输入是文件还是目录
    if os.path.isdir(args.input):
        # 目录批量转换
        results = converter.convert_directory(args.input, args.output, args.direction)
        success_count = len([k for k in results if k != "_errors"])
        error_count = len(results.get("_errors", []))
        print(f"批量转换完成: {success_count} 个文件成功, {error_count} 个文件失败")
        if error_count > 0:
            for err in results["_errors"]:
                print(f"  失败: {err['file']} - {err['error']}")
    else:
        # 单文件转换
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
    if src != "_errors":
        print(f"{src} -> {dst}")
```

## 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| 编码错误 | 文件非 UTF-8 | 指定编码：`CSVJSONConverter(encoding="gbk")` |
| CSV 格式错误 | 分隔符不对 | 指定分隔符：`CSVJSONConverter(delimiter=";")` |
| 内存不足 | 大文件未流式处理 | 使用 `csv_to_json_streaming()` |
| direction 无效 | 传错值 | 必须是 `"csv2json"` 或 `"json2csv"` |
| 批量转换中断 | 单文件异常 | 检查返回的 `_errors` 字段 |

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| ijson | 3.0+ | 流式 JSON→CSV 必需（未安装时抛异常提示） |
