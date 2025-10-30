"""Email service for sending notifications and digests via SMTP."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.event import Event
from app.models.client import Client
from app.models.email_log import EmailLog

logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service using SMTP."""

    # SMTP Configuration (should come from environment variables)
    SMTP_HOST = "smtp.gmail.com"  # Default, override with env
    SMTP_PORT = 587
    SMTP_USE_TLS = True
    SMTP_USERNAME = None  # Set from env
    SMTP_PASSWORD = None  # Set from env
    FROM_EMAIL = "noreply@clientmonitor.com"
    FROM_NAME = "Client Monitor"

    @classmethod
    def configure(
        cls,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "Client Monitor",
        use_tls: bool = True
    ):
        """Configure SMTP settings."""
        cls.SMTP_HOST = smtp_host
        cls.SMTP_PORT = smtp_port
        cls.SMTP_USERNAME = smtp_username
        cls.SMTP_PASSWORD = smtp_password
        cls.FROM_EMAIL = from_email
        cls.FROM_NAME = from_name
        cls.SMTP_USE_TLS = use_tls

    @staticmethod
    async def send_event_notification(
        db: Session,
        user: User,
        event: Event,
        client: Client,
        insights: Optional[Dict[str, Any]] = None,
        crm_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send email notification for a single event.

        Args:
            db: Database session
            user: User to notify
            event: Event instance
            client: Client instance
            insights: Optional AI-generated insights
            crm_data: Optional CRM enrichment data

        Returns:
            True if email sent successfully
        """
        try:
            # Build email subject
            subject = f"🔔 New Event: {event.title}"

            # Build HTML email body
            html_body = EmailService._build_event_email_html(
                event=event,
                client=client,
                insights=insights,
                crm_data=crm_data,
                user=user
            )

            # Send email
            success = EmailService._send_via_smtp(
                to_email=user.email,
                to_name=user.full_name or user.username,
                subject=subject,
                html_body=html_body
            )

            # Log email
            EmailService._log_email(
                db=db,
                business_id=user.business_id,
                user_id=user.id,
                event_id=event.id,
                email_type="event_notification",
                recipient_email=user.email,
                subject=subject,
                status="sent" if success else "failed",
                error_message=None if success else "SMTP send failed"
            )

            return success

        except Exception as e:
            logger.error(f"Failed to send event notification to {user.email}: {str(e)}")
            EmailService._log_email(
                db=db,
                business_id=user.business_id,
                user_id=user.id,
                event_id=event.id,
                email_type="event_notification",
                recipient_email=user.email,
                subject=f"Event: {event.title}",
                status="failed",
                error_message=str(e)
            )
            return False

    @staticmethod
    async def send_digest_email(
        db: Session,
        user: User,
        events: List[Event],
        period: str = "daily"
    ) -> bool:
        """
        Send digest email with multiple events.

        Args:
            db: Database session
            user: User to notify
            events: List of Event instances
            period: "daily" or "weekly"

        Returns:
            True if email sent successfully
        """
        try:
            # Build subject
            subject = f"📊 Your {period.capitalize()} Client Monitor Digest - {len(events)} Events"

            # Build HTML body
            html_body = EmailService._build_digest_email_html(
                events=events,
                period=period,
                user=user
            )

            # Send email
            success = EmailService._send_via_smtp(
                to_email=user.email,
                to_name=user.full_name or user.username,
                subject=subject,
                html_body=html_body
            )

            # Log email
            EmailService._log_email(
                db=db,
                business_id=user.business_id,
                user_id=user.id,
                event_id=None,
                email_type="digest",
                recipient_email=user.email,
                subject=subject,
                status="sent" if success else "failed",
                error_message=None if success else "SMTP send failed"
            )

            return success

        except Exception as e:
            logger.error(f"Failed to send digest to {user.email}: {str(e)}")
            return False

    @staticmethod
    def _send_via_smtp(
        to_email: str,
        to_name: str,
        subject: str,
        html_body: str
    ) -> bool:
        """
        Send email via SMTP.

        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            html_body: HTML email body

        Returns:
            True if sent successfully
        """
        if not EmailService.SMTP_USERNAME or not EmailService.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{EmailService.FROM_NAME} <{EmailService.FROM_EMAIL}>"
            msg["To"] = f"{to_name} <{to_email}>"

            # Add HTML body
            html_part = MIMEText(html_body, "html")
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(EmailService.SMTP_HOST, EmailService.SMTP_PORT) as server:
                if EmailService.SMTP_USE_TLS:
                    server.starttls()

                server.login(EmailService.SMTP_USERNAME, EmailService.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP send failed to {to_email}: {str(e)}")
            return False

    @staticmethod
    def _build_event_email_html(
        event: Event,
        client: Client,
        insights: Optional[Dict[str, Any]],
        crm_data: Optional[Dict[str, Any]],
        user: User
    ) -> str:
        """Build HTML template for event notification."""

        # Sentiment emoji
        sentiment_emoji = "😐"
        if event.sentiment_score:
            if event.sentiment_score > 0.3:
                sentiment_emoji = "😊"
            elif event.sentiment_score < -0.3:
                sentiment_emoji = "😟"

        # Relevance color
        relevance_color = "#22c55e"  # green
        if event.relevance_score < 0.5:
            relevance_color = "#eab308"  # yellow
        elif event.relevance_score >= 0.8:
            relevance_color = "#dc2626"  # red (high importance)

        # Build insights section
        insights_html = ""
        if insights:
            insights_html = f"""
            <div style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                <h3 style="color: #1e40af; margin-top: 0;">🤖 AI Insights</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    {''.join([f'<li style="margin: 8px 0;">{insight}</li>' for insight in insights.get('insights', [])])}
                </ul>

                <h4 style="color: #1e40af; margin-top: 15px;">Recommended Actions:</h4>
                <ol style="margin: 10px 0; padding-left: 20px;">
                    {''.join([f'<li style="margin: 8px 0;">{action}</li>' for action in insights.get('recommended_actions', [])])}
                </ol>

                <p style="margin-top: 15px;">
                    <strong>Risk Assessment:</strong> {insights.get('risk_assessment', 'N/A')}<br>
                    <strong>Urgency:</strong> {insights.get('urgency_level', 'N/A')}
                </p>
            </div>
            """

        # Build CRM section
        crm_html = ""
        if crm_data and crm_data.get("success"):
            health_score = crm_data.get("health_score")
            health_html = ""
            if health_score:
                health_color = "#22c55e" if health_score >= 70 else "#eab308" if health_score >= 50 else "#dc2626"
                health_html = f'<strong>Health Score:</strong> <span style="color: {health_color};">{health_score}/100</span><br>'

            crm_html = f"""
            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                <h3 style="color: #92400e; margin-top: 0;">📊 CRM Context</h3>
                {health_html}
                {f'<strong>Annual Revenue:</strong> {crm_data.get("annual_revenue_formatted", "N/A")}<br>' if crm_data.get("annual_revenue") else ''}
                {f'<strong>Open Opportunities:</strong> {crm_data.get("open_opportunities", 0)}<br>' if crm_data.get("open_opportunities") else ''}
                {f'<strong>Open Cases:</strong> {crm_data.get("open_cases", 0)}<br>' if crm_data.get("open_cases") else ''}
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">Client Monitor</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">New Event Detected</p>
            </div>

            <div style="background-color: #ffffff; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #111827;">{event.title}</h2>
                    <p style="margin: 5px 0; color: #6b7280;">
                        <strong>Client:</strong> {client.name}<br>
                        <strong>Category:</strong> {event.category.replace('_', ' ').title()}<br>
                        <strong>Date:</strong> {event.event_date.strftime('%B %d, %Y') if event.event_date else 'Unknown'}
                    </p>
                </div>

                <div style="margin: 20px 0;">
                    <p><strong>Description:</strong></p>
                    <p style="color: #4b5563;">{event.description or 'No description available.'}</p>
                    {f'<p><a href="{event.url}" style="color: #3b82f6; text-decoration: none;">View Source →</a></p>' if event.url else ''}
                </div>

                <div style="margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; background-color: #f9fafb; border-radius: 5px; margin-right: 10px;">
                                <strong>Relevance:</strong><br>
                                <span style="color: {relevance_color}; font-size: 24px; font-weight: bold;">{int(event.relevance_score * 100)}%</span>
                            </td>
                            <td style="padding: 10px; background-color: #f9fafb; border-radius: 5px;">
                                <strong>Sentiment:</strong><br>
                                <span style="font-size: 24px;">{sentiment_emoji}</span>
                            </td>
                        </tr>
                    </table>
                </div>

                {insights_html}
                {crm_html}

                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
                    <p style="margin: 10px 0;">
                        <a href="http://localhost:5173/events?event_id={event.id}"
                           style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View in Dashboard
                        </a>
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px;">
                    <p>You're receiving this email because you have notifications enabled for {client.name}.</p>
                    <p><a href="http://localhost:5173/settings" style="color: #3b82f6;">Manage Notification Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _build_digest_email_html(
        events: List[Event],
        period: str,
        user: User
    ) -> str:
        """Build HTML template for digest email."""

        # Build events list
        events_html = ""
        for event in events[:10]:  # Limit to 10 events in digest
            relevance_color = "#22c55e" if event.relevance_score >= 0.7 else "#eab308"

            events_html += f"""
            <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {relevance_color};">
                <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #111827;">{event.title}</h3>
                <p style="margin: 5px 0; color: #6b7280; font-size: 14px;">
                    <strong>{event.client.name}</strong> • {event.category.replace('_', ' ').title()} • Relevance: {int(event.relevance_score * 100)}%
                </p>
                <p style="margin: 8px 0 0 0; color: #4b5563; font-size: 14px;">{(event.description or '')[:150]}...</p>
                <p style="margin: 8px 0 0 0;">
                    <a href="http://localhost:5173/events?event_id={event.id}" style="color: #3b82f6; text-decoration: none; font-size: 14px;">View Details →</a>
                </p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">📊 Your {period.capitalize()} Digest</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">{len(events)} New Events</p>
            </div>

            <div style="background-color: #ffffff; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
                <p style="color: #4b5563;">Hi {user.full_name or user.username},</p>
                <p style="color: #4b5563;">Here's your {period} summary of client events:</p>

                <div style="margin: 20px 0;">
                    {events_html}
                </div>

                {f'<p style="color: #6b7280; font-size: 14px; font-style: italic;">Showing 10 of {len(events)} events. <a href="http://localhost:5173/events" style="color: #3b82f6;">View all in dashboard</a></p>' if len(events) > 10 else ''}

                <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
                    <p>
                        <a href="http://localhost:5173/events"
                           style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View All Events
                        </a>
                    </p>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px;">
                    <p>You're receiving this {period} digest based on your notification preferences.</p>
                    <p><a href="http://localhost:5173/settings" style="color: #3b82f6;">Manage Notification Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    @staticmethod
    def _log_email(
        db: Session,
        business_id: UUID,
        user_id: int,
        event_id: Optional[UUID],
        email_type: str,
        recipient_email: str,
        subject: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """Log email to database."""
        try:
            email_log = EmailLog(
                business_id=business_id,
                user_id=user_id,
                event_id=event_id,
                email_type=email_type,
                recipient_email=recipient_email,
                subject=subject,
                body_preview=subject[:500],
                status=status,
                error_message=error_message,
                provider="smtp"
            )
            db.add(email_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log email: {str(e)}")
