"""Email notification system for client monitoring."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from src.notifiers.digest import DigestGenerator

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications and digests."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: bool = True
    ):
        """
        Initialize email notifier.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (default: 587 for TLS, 465 for SSL)
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
            use_tls: Use TLS encryption (default: True)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port or (587 if use_tls else 465)
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user
        self.use_tls = use_tls
        self.configured = all([smtp_host, smtp_user, smtp_password])

    def send_digest(
        self,
        to_emails: List[str],
        digest_html: str,
        subject: Optional[str] = None,
        digest_text: Optional[str] = None
    ) -> bool:
        """
        Send digest email.

        Args:
            to_emails: List of recipient email addresses
            digest_html: HTML content of the digest
            subject: Email subject line (optional)
            digest_text: Plain text version of digest (optional, falls back to HTML)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.configured:
            logger.warning("Email notifier not configured. Cannot send digest.")
            return False

        if subject is None:
            subject = f"Client Intelligence Digest - {datetime.now().strftime('%Y-%m-%d')}"

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)

            # Attach plain text version
            if digest_text:
                part1 = MIMEText(digest_text, 'plain')
                msg.attach(part1)

            # Attach HTML version
            part2 = MIMEText(digest_html, 'html')
            msg.attach(part2)

            # Send email
            self._send_email(to_emails, msg)

            logger.info(f"Digest email sent to {len(to_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send digest email: {e}")
            return False

    def send_alert(
        self,
        to_emails: List[str],
        alert_title: str,
        alert_body: str,
        priority: str = "normal",
        event_url: Optional[str] = None
    ) -> bool:
        """
        Send alert email for high-priority events.

        Args:
            to_emails: List of recipient email addresses
            alert_title: Alert title/subject
            alert_body: Alert body content
            priority: Email priority ("low", "normal", "high")
            event_url: Optional URL to the event source

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.configured:
            logger.warning("Email notifier not configured. Cannot send alert.")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Alert: {alert_title}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)

            # Set priority header
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'
            elif priority == "low":
                msg['X-Priority'] = '5'
                msg['Importance'] = 'low'

            # Create plain text version
            text_body = f"""ALERT: {alert_title}

{alert_body}
"""
            if event_url:
                text_body += f"\nView event: {event_url}\n"

            # Create HTML version
            html_body = self._create_alert_html(alert_title, alert_body, event_url, priority)

            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            self._send_email(to_emails, msg)

            logger.info(f"Alert email sent to {len(to_emails)} recipients: {alert_title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
            return False

    def _send_email(self, to_emails: List[str], msg: MIMEMultipart):
        """Internal method to send email via SMTP."""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()

            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            server.sendmail(self.from_email, to_emails, msg.as_string())

    def _create_alert_html(
        self,
        title: str,
        body: str,
        url: Optional[str],
        priority: str
    ) -> str:
        """Create HTML template for alert emails."""
        priority_colors = {
            "high": "#dc3545",
            "normal": "#ffc107",
            "low": "#28a745"
        }
        color = priority_colors.get(priority, "#ffc107")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .alert-container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .alert-header {{
            border-left: 4px solid {color};
            padding-left: 20px;
            margin-bottom: 20px;
        }}
        .alert-title {{
            color: {color};
            font-size: 24px;
            font-weight: bold;
            margin: 0;
        }}
        .alert-body {{
            color: #333;
            line-height: 1.6;
            margin: 20px 0;
        }}
        .alert-button {{
            display: inline-block;
            background-color: {color};
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 20px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="alert-container">
        <div class="alert-header">
            <h1 class="alert-title">🚨 {title}</h1>
        </div>
        <div class="alert-body">
            {body.replace(chr(10), '<br>')}
        </div>
"""
        if url:
            html += f"""
        <a href="{url}" class="alert-button">View Event Details</a>
"""

        html += f"""
        <div class="footer">
            <p>This is an automated alert from Client Intelligence Monitor.</p>
            <p>Sent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def test_connection(self) -> tuple[bool, str]:
        """
        Test SMTP connection.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.configured:
            return False, "Email notifier not configured. Missing SMTP credentials."

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                return True, "SMTP connection successful"

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed. Check username and password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
