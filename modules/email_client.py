"""
邮件模块 - 支持收发邮件
"""
import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailClient:
    """邮件客户端"""
    
    def __init__(self, 
                 smtp_host: str = None,
                 smtp_port: int = None,
                 imap_host: str = None,
                 imap_port: int = None,
                 email_address: str = None,
                 email_password: str = None):
        self.smtp_host = smtp_host or os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.imap_host = imap_host or os.getenv("EMAIL_IMAP_HOST", "imap.gmail.com")
        self.imap_port = imap_port or int(os.getenv("EMAIL_IMAP_PORT", "993"))
        self.email_address = email_address or os.getenv("EMAIL_ADDRESS")
        self.email_password = email_password or os.getenv("EMAIL_PASSWORD")
    
    def _check_config(self):
        """检查配置"""
        if not self.email_address or not self.email_password:
            raise ValueError("请在 .env 中配置 EMAIL_ADDRESS 和 EMAIL_PASSWORD")
    
    def send_email(self,
                   to: str,
                   subject: str,
                   body: str,
                   cc: Optional[str] = None,
                   attachments: Optional[List[str]] = None,
                   html: bool = False) -> Dict:
        """
        发送邮件
        返回: {"status": "success", "message_id": "xxx"}
        """
        self._check_config()
        
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = cc
        
        # 正文
        if html:
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 附件
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    filename = os.path.basename(file_path)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)
        
        # 发送
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                
                recipients = [to]
                if cc:
                    recipients.extend(cc.split(','))
                
                server.sendmail(self.email_address, recipients, msg.as_string())
                
            return {"status": "success", "to": to, "subject": subject}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def fetch_emails(self, 
                     folder: str = "INBOX",
                     limit: int = 10,
                     unread_only: bool = False) -> List[Dict]:
        """
        获取邮件列表
        返回: [{"id": "1", "from": "xxx", "subject": "xxx", "date": "xxx", "preview": "xxx"}, ...]
        """
        self._check_config()
        
        emails = []
        
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port) as imap:
                imap.login(self.email_address, self.email_password)
                imap.select(folder)
                
                # 搜索邮件
                search_criteria = "UNSEEN" if unread_only else "ALL"
                _, message_numbers = imap.search(None, search_criteria)
                
                # 获取最新的N封
                msg_nums = message_numbers[0].split()[-limit:]
                msg_nums.reverse()  # 最新的在前
                
                for num in msg_nums:
                    _, msg_data = imap.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)
                    
                    # 解析标题
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    
                    # 解析发件人
                    from_addr = msg['From']
                    
                    # 解析日期
                    date_str = msg['Date']
                    
                    # 获取正文预览
                    preview = self._get_email_preview(msg)
                    
                    emails.append({
                        "id": num.decode(),
                        "from": from_addr,
                        "subject": subject,
                        "date": date_str,
                        "preview": preview
                    })
        
        except Exception as e:
            return [{"error": str(e)}]
        
        return emails
    
    def _get_email_preview(self, msg, max_length: int = 200) -> str:
        """获取邮件正文预览"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        return body[:max_length] + "..." if len(body) > max_length else body
    
    def get_email_content(self, email_id: str, folder: str = "INBOX") -> Dict:
        """获取完整邮件内容"""
        self._check_config()
        
        try:
            with imaplib.IMAP4_SSL(self.imap_host, self.imap_port) as imap:
                imap.login(self.email_address, self.email_password)
                imap.select(folder)
                
                _, msg_data = imap.fetch(email_id.encode(), '(RFC822)')
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)
                
                # 解析完整内容
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')
                
                body = ""
                html_body = ""
                attachments = []
                
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                        elif content_type == "text/html":
                            payload = part.get_payload(decode=True)
                            if payload:
                                html_body = payload.decode('utf-8', errors='ignore')
                        elif part.get_filename():
                            attachments.append(part.get_filename())
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                
                return {
                    "id": email_id,
                    "from": msg['From'],
                    "to": msg['To'],
                    "subject": subject,
                    "date": msg['Date'],
                    "body": body,
                    "html_body": html_body,
                    "attachments": attachments
                }
        
        except Exception as e:
            return {"error": str(e)}


def compose_email_with_llm(llm_client, 
                           purpose: str, 
                           context: str = "",
                           tone: str = "professional") -> Dict[str, str]:
    """
    使用LLM撰写邮件
    返回: {"subject": "xxx", "body": "xxx"}
    """
    prompt = f"""请根据以下要求撰写一封邮件：

目的：{purpose}
背景信息：{context}
语气：{tone}

请输出：
1. 邮件主题（一行）
2. 邮件正文

格式：
主题：xxx
正文：
xxx"""

    response = llm_client.simple_chat(prompt)
    
    # 解析响应
    lines = response.strip().split('\n')
    subject = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.startswith("主题：") or line.startswith("主题:"):
            subject = line.replace("主题：", "").replace("主题:", "").strip()
        elif line.startswith("正文：") or line.startswith("正文:"):
            in_body = True
        elif in_body:
            body_lines.append(line)
    
    return {
        "subject": subject,
        "body": "\n".join(body_lines).strip()
    }
