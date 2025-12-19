import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    """
    Send an email using SMTP configuration from environment variables.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
    """
    try:
        # Get SMTP configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", smtp_username)
        
        # If no SMTP configuration, just log the email (for development)
        if not smtp_server or not smtp_username or not smtp_password:
            logger.info(f"EMAIL SIMULATION: To: {to_email}, Subject: {subject}")
            logger.info(f"Body: {body}")
            return True
            
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        server.login(smtp_username, smtp_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_otp_email(to_email: str, otp_code: str):
    """
    Send OTP code email to user.
    
    Args:
        to_email (str): Recipient email address
        otp_code (str): 6-digit OTP code
    """
    subject = "MugShot Studio - Email Verification Code"
    body = f"""
Hello,

Thank you for signing up with MugShot Studio!

Your verification code is: {otp_code}

Please enter this code in the app to verify your email address.

If you didn't sign up for MugShot Studio, please ignore this email.

Best regards,
The MugShot Studio Team
    """.strip()
    
    return send_email(to_email, subject, body)