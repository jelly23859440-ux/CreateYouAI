---
name: 邮件发送
layer: action
category: device
description: >
  发送文本和 HTML 邮件，支持附件功能。
  当用户需要发送邮件、通知、报告、自动化邮件、批量发送时触发。
  关键词：邮件发送、email、SMTP、发送通知、邮件附件、批量邮件。
---

# 邮件发送

发送文本和 HTML 邮件，支持单发、群发和附件功能。

## 能力概览

| 能力 | 说明 |
|------|------|
| 文本邮件 | 发送纯文本邮件 |
| HTML 邮件 | 发送富文本邮件 |
| 附件支持 | 支持单个/多个附件 |
| 批量发送 | 支持群发邮件 |
| SMTP 支持 | 支持主流邮件服务商 |

## 前置条件

- Python 3.8+
- 无第三方依赖（使用内置 smtplib + email）
- SMTP 服务器账号（如 Gmail、QQ邮箱、163邮箱等）

## 安装步骤

无额外安装。使用 Python 内置模块。

### SMTP 服务器配置

| 服务商 | SMTP 服务器 | 端口 |
|--------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| QQ邮箱 | smtp.qq.com | 587 |
| 163邮箱 | smtp.163.com | 465 |
| Outlook | smtp.office365.com | 587 |
| 自建 | 你的服务器地址 | 465/587 |

## 使用方法

### 基础邮件发送

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from typing import List, Optional, Dict
import os

class EmailSender:
    """邮件发送器"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
    
    def send_text(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        cc: Optional[str | List[str]] = None
    ) -> Dict:
        """
        发送文本邮件。
        
        Returns:
            {"success": bool, "message": str}
        """
        if isinstance(to, str):
            to = [to]
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        
        if cc:
            if isinstance(cc, str):
                cc = [cc]
            msg['Cc'] = ', '.join(cc)
        
        return self._send(msg, to + (cc or []))
    
    def send_html(
        self,
        to: str | List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[str | List[str]] = None
    ) -> Dict:
        """
        发送 HTML 邮件。
        
        Args:
            to: 收件人（字符串或列表）
            subject: 主题
            html_body: HTML 内容
            text_body: 纯文本备用（可选）
            cc: 抄送（可选）
        """
        if isinstance(to, str):
            to = [to]
        
        msg = MIMEMultipart('alternative')
        msg['From'] = self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        
        if cc:
            if isinstance(cc, str):
                cc = [cc]
            msg['Cc'] = ', '.join(cc)
        
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        return self._send(msg, to + (cc or []))
    
    def send_with_attachments(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        attachments: List[str],
        is_html: bool = False
    ) -> Dict:
        """
        发送带附件的邮件。
        
        Args:
            to: 收件人
            subject: 主题
            body: 邮件正文
            attachments: 附件文件路径列表
            is_html: 正文是否为 HTML
        """
        if isinstance(to, str):
            to = [to]
        
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        
        content_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))
        
        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    part = MIMEApplication(f.read())
                    filename = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition', 
                        f'attachment; filename="{filename}"'
                    )
                    msg.attach(part)
            else:
                print(f"警告: 附件不存在 - {file_path}")
        
        return self._send(msg, to)
    
    def _send(self, msg: MIMEMultipart, recipients: List[str]) -> Dict:
        """实际发送邮件"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.username, self.password)
                server.send_message(msg, self.username, recipients)
                
                return {
                    "success": True,
                    "message": f"邮件已发送至: {', '.join(recipients)}"
                }
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "SMTP 认证失败，请检查用户名和密码"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message": f"SMTP 错误: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"发送失败: {str(e)}"
            }

# 使用示例
if __name__ == "__main__":
    sender = EmailSender(
        smtp_server="smtp.qq.com",
        smtp_port=587,
        username="your_email@qq.com",
        password="your_smtp_password"
    )
    
    result = sender.send_text(
        to="recipient@example.com",
        subject="测试邮件",
        body="这是一封测试邮件"
    )
    print(result["message"])
```

### HTML 模板邮件

```python
def send_html_report(
    sender: EmailSender,
    to: str,
    title: str,
    data: Dict
) -> Dict:
    """发送 HTML 报告邮件"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 15px; border-radius: 5px; }}
            .content {{ padding: 20px; background: #f9f9f9; margin: 15px 0; border-radius: 5px; }}
            .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            <h2>报告摘要</h2>
            <table>
                <tr><th>指标</th><th>数值</th></tr>
                {" ".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in data.items())}
            </table>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送</p>
        </div>
    </body>
    </html>
    """
    
    return sender.send_html(
        to=to,
        subject=f"{title} - {data.get('date', '')}",
        html_body=html_template
    )

# 使用示例
if __name__ == "__main__":
    sender = EmailSender(
        smtp_server="smtp.qq.com",
        smtp_port=587,
        username="your_email@qq.com",
        password="your_smtp_password"
    )
    
    report_data = {
        "date": "2024-03-15",
        "total_users": "1,234",
        "active_users": "567",
        "revenue": "$89,012"
    }
    
    result = send_html_report(sender, "admin@example.com", "周报", report_data)
    print(result["message"])
```

### 批量邮件发送

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

class BulkEmailSender:
    """批量邮件发送器"""
    
    def __init__(self, sender: EmailSender, max_workers: int = 5):
        self.sender = sender
        self.max_workers = max_workers
    
    def send_bulk(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = False
    ) -> List[Dict]:
        """
        批量发送邮件。
        
        Returns:
            [{"email": str, "success": bool, "message": str}, ...]
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for email in recipients:
                future = executor.submit(
                    self._send_one, email, subject, body, is_html
                )
                futures[future] = email
            
            for future in as_completed(futures):
                email = futures[future]
                result = future.result()
                results.append({"email": email, **result})
        
        return results
    
    def _send_one(
        self, 
        email: str, 
        subject: str, 
        body: str, 
        is_html: bool
    ) -> Dict:
        """发送单封邮件"""
        if is_html:
            return self.sender.send_html(email, subject, body)
        else:
            return self.sender.send_text(email, subject, body)

# 使用示例
if __name__ == "__main__":
    sender = EmailSender(
        smtp_server="smtp.qq.com",
        smtp_port=587,
        username="your_email@qq.com",
        password="your_smtp_password"
    )
    
    bulk = BulkEmailSender(sender, max_workers=10)
    
    recipients = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
    ]
    
    results = bulk.send_bulk(
        recipients=recipients,
        subject="系统通知",
        body="这是一封系统通知邮件"
    )
    
    success_count = sum(1 for r in results if r["success"])
    print(f"发送完成: {success_count}/{len(results)} 成功")
```

### 预设邮件服务配置

```python
class EmailProviders:
    """邮件服务商预设配置"""
    
    PROVIDERS = {
        "qq": {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "use_tls": True
        },
        "163": {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "use_tls": False
        },
        "gmail": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "use_tls": True
        },
        "outlook": {
            "smtp_server": "smtp.office365.com",
            "smtp_port": 587,
            "use_tls": True
        }
    }
    
    @classmethod
    def get_sender(
        cls, 
        provider: str, 
        username: str, 
        password: str
    ) -> EmailSender:
        """获取预配置的发送器"""
        if provider not in cls.PROVIDERS:
            raise ValueError(f"不支持的服务商: {provider}，可选: {list(cls.PROVIDERS.keys())}")
        
        config = cls.PROVIDERS[provider]
        return EmailSender(
            smtp_server=config["smtp_server"],
            smtp_port=config["smtp_port"],
            username=username,
            password=password,
            use_tls=config["use_tls"]
        )

# 使用示例
if __name__ == "__main__":
    sender = EmailProviders.get_sender(
        provider="qq",
        username="your_email@qq.com",
        password="your_smtp_password"
    )
    
    result = sender.send_text(
        to="recipient@example.com",
        subject="测试",
        body="QQ邮箱发送测试"
    )
    print(result["message"])
```

### 命令行用法

```bash
# 发送文本邮件
python email_sender.py --to user@example.com --subject "测试" --body "邮件内容"

# 发送 HTML 邮件
python email_sender.py --to user@example.com --subject "报告" --html "<h1>报告</h1>"

# 发送带附件邮件
python email_sender.py --to user@example.com --subject "文件" --body "请查收附件" --attach file.pdf

# 批量发送
python email_sender.py --recipients list.txt --subject "通知" --body "系统通知"
```

## 问题排查

### 问题 1：SMTP 认证失败

**原因**：密码错误或需要应用专用密码。

**解决**：
- QQ邮箱：开启 SMTP 服务，获取授权码
- Gmail：启用"应用专用密码"
- 163邮箱：开启 SMTP 服务并设置授权码

### 问题 2：邮件被标记为垃圾邮件

**原因**：发送频率过高或内容触发规则。

**解决**：
- 降低发送频率
- 避免敏感关键词
- 设置正确的 SPF/DKIM 记录

### 问题 3：附件发送失败

**原因**：文件路径错误或文件过大。

**解决**：
- 检查文件路径是否存在
- 压缩大文件或分卷发送
- 检查邮件服务商附件大小限制

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| smtplib | 内置 | 必需 |
| email | 内置 | 必需 |

## Agent 执行规范

### 核心约束
- **密码安全**：使用环境变量存储 SMTP 密码，不要硬编码
- **发送确认**：批量发送前先测试单封
- **错误记录**：记录所有发送失败的邮件
- **频率限制**：遵守邮件服务商的发送限制