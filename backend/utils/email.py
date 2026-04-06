"""
Email Service

提供 Email 發送功能，支援 Google Mail SMTP。
使用 aiosmtplib 進行非同步發送。
支援 HTML、純文字以及多個附件發送 (支援實體檔案路徑與 BytesIO / bytes)。
"""

import io
import logging
import mimetypes
import urllib.parse
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from typing import Optional, Union

import aiosmtplib
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MailSetting(BaseModel):
    host: str = Field(..., alias="smtp_host")
    port: int = Field(587, alias="smtp_port")
    user: str = Field(..., alias="smtp_user")
    password: str = Field(..., alias="smtp_password")
    use_tls: bool = Field(True, alias="smtp_use_tls")
    from_name: str = Field("復興高中系統通知", alias="smtp_from_name")

    @property
    def sender_format(self) -> str:
        """格式化寄件者名稱與信箱，例如: '復興高中系統通知 <test@example.com>'"""
        return formataddr((self.from_name, self.user))


class EmailService:
    """
    Email 發送服務
    
    使用方式:
    ```python
    email_service = EmailService(host="...", user="...", password="...", from_name="...")
    
    # 支援實體檔案與記憶體中的 bytes/BytesIO
    await email_service.send_email(
        to="user@example.com",
        subject="測試郵件",
        html_content="<h1>Hello</h1>",
        attachments=[
            "/path/to/file.pdf",                   # 實體檔案路徑
            ("report.pdf", pdf_bytes_or_bytesio)   # 記憶體中的檔案 (檔名, 內容)
        ]
    )
    ```
    """
    
    def __init__(self, **settings: str | int | bool):
        self.settings = MailSetting(**settings)

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[list[Union[str, Path, tuple[str, Union[bytes, io.BytesIO]]]]] = None,
    ) -> bool:
        """
        發送 Email
        
        Args:
            to: 收件者 email
            subject: 郵件主旨
            html_content: HTML 內容
            text_content: 純文字內容（可選，若無則自動從 HTML 提取）
            attachments: 附件列表，可包含檔案路徑(str/Path)或 (檔名, bytes/BytesIO) 的元組
        
        Returns:
            bool: 發送是否成功
        """
        current_settings = self.settings.model_copy()
        
        if attachments:
            message = MIMEMultipart("mixed")
            body_part = MIMEMultipart("alternative")
            if text_content:
                body_part.attach(MIMEText(text_content, "plain", "utf-8"))
            body_part.attach(MIMEText(html_content, "html", "utf-8"))
            message.attach(body_part)
        else:
            message = MIMEMultipart("alternative")
            if text_content:
                message.attach(MIMEText(text_content, "plain", "utf-8"))
            message.attach(MIMEText(html_content, "html", "utf-8"))

        message["Subject"] = subject
        message["From"] = current_settings.sender_format
        message["To"] = to
        
        # 處理附件
        if attachments:
            for item in attachments:
                file_content = b""
                filename = ""
                ctype = None
                
                try:
                    # 1. 處理實體檔案 (字串或 Path)
                    if isinstance(item, (str, Path)):
                        path = Path(item)
                        if not path.is_file():
                            logger.warning(f"附件檔案不存在，略過: {path}")
                            continue
                        filename = path.name
                        ctype, _ = mimetypes.guess_type(path)
                        with open(path, "rb") as f:
                            file_content = f.read()
                            
                    # 2. 處理記憶體中的檔案 (Tuple: (檔名, bytes 或 BytesIO))
                    elif isinstance(item, tuple) and len(item) == 2:
                        filename, content = item
                        ctype, _ = mimetypes.guess_type(filename)
                        if isinstance(content, bytes):
                            file_content = content
                        elif isinstance(content, io.BytesIO):
                            file_content = content.getvalue()
                        else:
                            logger.warning(f"不支援的附件內容型別，略過: {type(content)}")
                            continue
                    else:
                        logger.warning(f"不支援的附件參數格式，略過: {type(item)}")
                        continue
                        
                    # 預設 MIME Type
                    if ctype is None:
                        ctype = "application/octet-stream"
                    
                    maintype, subtype = ctype.split("/", 1)
                    
                    # 建立附件物件
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(file_content)
                    encoders.encode_base64(part)
                    
                    # 處理中文檔名
                    encoded_filename = urllib.parse.quote(filename)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename*=utf-8''{encoded_filename}"
                    )
                    
                    message.attach(part)
                except Exception as e:
                    logger.error(f"處理附件時發生錯誤 ({item}): {e}")
        
        try:
            await aiosmtplib.send(
                message,
                hostname=current_settings.host,
                port=current_settings.port,
                username=current_settings.user,
                password=current_settings.password,
                start_tls=current_settings.use_tls,
            )
            logger.info(f"Email 發送成功: {to}")
            return True
            
        except aiosmtplib.SMTPException as e:
            logger.error(f"Email 發送失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"Email 發送錯誤: {e}")
            return False


_email_service: Optional[EmailService] = None

def get_email_service(**settings) -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService(**settings)
    return _email_service