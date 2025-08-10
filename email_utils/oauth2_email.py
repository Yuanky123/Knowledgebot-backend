#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import json
from typing import Optional, Dict, Any

class OAuth2EmailSender:
    """OAuth2 Email Sender supporting multiple email providers"""
    
    def __init__(self, email_provider: str = "gmail"):
        """
        Initialize OAuth2 Email Sender
        
        Args:
            email_provider: Email provider ('gmail', 'outlook', 'qq')
        """
        self.email_provider = email_provider.lower()
        self.credentials = None
        self.service = None
        
        # OAuth2 scopes for different providers
        self.scopes = {
            'gmail': ['https://www.googleapis.com/auth/gmail.send'],
            'outlook': ['https://outlook.office.com/mail.send'],
            'qq': []  # QQ doesn't support OAuth2, uses app password
        }
        
        # SMTP settings for different providers
        self.smtp_settings = {
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_oauth2': True
            },
            'outlook': {
                'server': 'smtp.office365.com',
                'port': 587,
                'use_tls': True,
                'use_oauth2': True
            },
            'qq': {
                'server': 'smtp.qq.com',
                'port': 587,
                'use_tls': True,
                'use_oauth2': False
            }
        }
    
    def authenticate_gmail(self, client_secrets_file: str, token_file: str = 'token.pickle'):
        """
        Authenticate with Gmail using OAuth2
        
        Args:
            client_secrets_file: Path to client secrets JSON file
            token_file: Path to save/load token
        """
        if self.email_provider != 'gmail':
            raise ValueError("This method is only for Gmail authentication")
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, self.scopes['gmail'])
                self.credentials = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def authenticate_outlook(self, client_id: str, client_secret: str, tenant_id: str):
        """
        Authenticate with Outlook using OAuth2
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
        """
        if self.email_provider != 'outlook':
            raise ValueError("This method is only for Outlook authentication")
        
        # For Outlook, we'll use the Microsoft Graph API
        # This requires setting up an Azure AD application
        # For now, we'll use a simplified approach with username/password
        # In production, you should implement proper OAuth2 flow for Outlook
        pass
    
    def send_email_gmail_api(self, to_email: str, subject: str, body: str, from_email: str = None):
        """
        Send email using Gmail API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            from_email: Sender email (optional, uses authenticated user if not provided)
        """
        if not self.service:
            raise ValueError("Gmail service not initialized. Call authenticate_gmail() first.")
        
        if not from_email:
            # Get the authenticated user's email
            profile = self.service.users().getProfile(userId='me').execute()
            from_email = profile['emailAddress']
        
        # Create message
        message = MIMEMultipart()
        message['to'] = to_email
        message['from'] = from_email
        message['subject'] = subject
        
        # Add body
        text_part = MIMEText(body, 'plain', 'utf-8')
        message.attach(text_part)
        
        # Encode message
        raw_message = message.as_string()
        encoded_message = raw_message.encode('utf-8')
        
        # Send email
        try:
            sent_message = self.service.users().messages().send(
                userId='me', body={'raw': encoded_message.decode('utf-8')}
            ).execute()
            print(f"Email sent successfully. Message ID: {sent_message['id']}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_email_smtp(self, from_email: str, to_email: str, subject: str, body: str, 
                       password: str = None, app_password: str = None):
        """
        Send email using SMTP with OAuth2 or app password
        
        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            password: Regular password (for non-OAuth2 providers)
            app_password: App-specific password (for OAuth2 providers)
        """
        settings = self.smtp_settings[self.email_provider]
        
        # Create message
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add body
        text_part = MIMEText(body, 'plain', 'utf-8')
        message.attach(text_part)
        
        try:
            # Create SMTP connection
            if settings['use_tls']:
                server = smtplib.SMTP(settings['server'], settings['port'])
                server.starttls(context=ssl.create_default_context())
            else:
                server = smtplib.SMTP(settings['server'], settings['port'])
            
            # Login
            if settings['use_oauth2'] and self.credentials:
                # Use OAuth2 authentication
                auth_string = f'user={from_email}\1auth=Bearer {self.credentials.token}\1\1'
                server.ehlo()
                server.docmd('AUTH', 'XOAUTH2 ' + auth_string.encode('utf-8').decode('utf-8'))
            else:
                # Use password authentication
                password_to_use = app_password if app_password else password
                if not password_to_use:
                    raise ValueError("Password or app password is required")
                server.login(from_email, password_to_use)
            
            # Send email
            server.send_message(message)
            server.quit()
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   from_email: str = None, password: str = None, app_password: str = None):
        """
        Send email using the appropriate method for the provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            from_email: Sender email address
            password: Regular password
            app_password: App-specific password
        """
        if self.email_provider == 'gmail' and self.service:
            # Use Gmail API if available
            return self.send_email_gmail_api(to_email, subject, body, from_email)
        else:
            # Use SMTP
            if not from_email:
                raise ValueError("from_email is required for SMTP")
            return self.send_email_smtp(from_email, to_email, subject, body, password, app_password)


def setup_gmail_oauth2():
    """
    Setup instructions for Gmail OAuth2
    """
    print("""
Gmail OAuth2 Setup Instructions:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to Credentials
5. Create OAuth 2.0 Client ID
6. Download the client secrets JSON file
7. Use the file path in authenticate_gmail() method
    """)


def setup_outlook_oauth2():
    """
    Setup instructions for Outlook OAuth2
    """
    print("""
Outlook OAuth2 Setup Instructions:
1. Go to Azure Portal (https://portal.azure.com/)
2. Register a new application
3. Add Microsoft Graph API permissions
4. Grant admin consent
5. Create a client secret
6. Use the client ID, secret, and tenant ID in authenticate_outlook() method
    """)


# Example usage functions
def send_gmail_oauth2_example():
    """Example of sending email with Gmail OAuth2"""
    sender = OAuth2EmailSender('gmail')
    
    # You need to download client_secrets.json from Google Cloud Console
    client_secrets_file = 'client_secrets.json'  # Update this path
    
    if os.path.exists(client_secrets_file):
        sender.authenticate_gmail(client_secrets_file)
        sender.send_email_gmail_api(
            to_email='recipient@example.com',
            subject='Test Email via OAuth2',
            body='This is a test email sent using Gmail OAuth2 authentication.'
        )
    else:
        print("Please download client_secrets.json from Google Cloud Console")
        setup_gmail_oauth2()


def send_qq_app_password_example():
    """Example of sending email with QQ using app password"""
    sender = OAuth2EmailSender('qq')
    
    # QQ uses app password instead of OAuth2
    sender.send_email_smtp(
        from_email='your_qq_email@qq.com',  # Replace with your QQ email
        to_email='recipient@example.com',
        subject='Test Email via QQ',
        body='This is a test email sent using QQ app password.',
        app_password='your_app_password'  # Replace with your QQ app password
    )


if __name__ == "__main__":
    # Example usage
    print("Email OAuth2 Authentication Examples")
    print("=" * 40)
    
    # Gmail OAuth2 example
    print("\n1. Gmail OAuth2 Example:")
    send_gmail_oauth2_example()
    
    # QQ App Password example
    print("\n2. QQ App Password Example:")
    send_qq_app_password_example() 