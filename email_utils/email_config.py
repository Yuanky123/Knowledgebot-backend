#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Email Configuration File
Store your email settings and credentials here.
IMPORTANT: Never commit this file to version control with real credentials!
"""

import os
from typing import Dict, Any

class EmailConfig:
    """Email configuration class"""
    
    # Gmail OAuth2 Configuration
    GMAIL_CONFIG = {
        'client_secrets_file': 'client_secrets.json',  # Download from Google Cloud Console
        'token_file': 'gmail_token.pickle',  # Will be created automatically
        'scopes': ['https://www.googleapis.com/auth/gmail.send']
    }
    
    # QQ Email Configuration (uses app password)
    QQ_CONFIG = {
        'email': '1592744341@qq.com',  # Replace with your QQ email
        'app_password': 'tyiogjsnepwphjha',  # Replace with your QQ app password
        'smtp_server': 'smtp.qq.com',
        'smtp_port': 587
    }
    
    # Outlook/Office365 Configuration
    OUTLOOK_CONFIG = {
        'email': 'xwangij@connect.ust.hk',  # Replace with your Outlook email
        'password': 'Wxy201515wxy',  # Replace with your password or app password
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'use_starttls': True
    }
    
    # Gmail Configuration (alternative to OAuth2)
    GMAIL_PASSWORD_CONFIG = {
        'email': 'this.is.wangxiaoyu@gmail.com',  # Replace with your Gmail
        'app_password': 'your_gmail_app_password',  # Replace with your Gmail app password
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_starttls': True
    }
    
    @classmethod
    def get_config(cls, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific email provider"""
        configs = {
            'gmail': cls.GMAIL_CONFIG,
            'gmail_password': cls.GMAIL_PASSWORD_CONFIG,
            'qq': cls.QQ_CONFIG,
            'outlook': cls.OUTLOOK_CONFIG
        }
        return configs.get(provider.lower(), {})
    
    @classmethod
    def validate_config(cls, provider: str) -> bool:
        """Validate if configuration is complete for a provider"""
        config = cls.get_config(provider)
        
        if provider == 'gmail':
            # Check if client secrets file exists
            return os.path.exists(config.get('client_secrets_file', ''))
        elif provider == 'qq':
            # Check if email and app password are set
            return bool(config.get('email') and config.get('app_password'))
        elif provider in ['outlook', 'gmail_password']:
            # Check if email and password are set
            return bool(config.get('email') and config.get('password'))
        else:
            return False
    
    @classmethod
    def print_setup_instructions(cls, provider: str):
        """Print setup instructions for a specific provider"""
        if provider == 'gmail':
            print("""
Gmail OAuth2 Setup Instructions:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Choose "Desktop application" as application type
6. Download the client secrets JSON file
7. Save it as 'client_secrets.json' in this directory
8. Run the authentication flow
            """)
        elif provider == 'qq':
            print("""
QQ App Password Setup Instructions:
1. Log in to your QQ email account
2. Go to Settings → Account → Security
3. Enable "App Password" or "授权码"
4. Generate an app password for "Mail"
5. Use this app password instead of your regular password
6. Update the QQ_CONFIG in this file
            """)
        elif provider == 'outlook':
            print("""
Outlook/Office365 Setup Instructions:
1. For regular password authentication:
   - Use your regular password (if 2FA is disabled)
   - Or use an app password (if 2FA is enabled)
2. For OAuth2 authentication:
   - Set up Azure AD application
   - Configure Microsoft Graph API permissions
   - Use client ID, secret, and tenant ID
3. Update the OUTLOOK_CONFIG in this file
            """)
        elif provider == 'gmail_password':
            print("""
Gmail App Password Setup Instructions:
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account settings → Security
3. Generate an App Password for "Mail"
4. Use this app password instead of your regular password
5. Update the GMAIL_PASSWORD_CONFIG in this file
            """)

# Environment variable overrides (for security)
def get_email_config_from_env(provider: str) -> Dict[str, Any]:
    """Get email configuration from environment variables"""
    env_config = {}
    
    if provider == 'gmail':
        env_config['client_secrets_file'] = os.getenv('GMAIL_CLIENT_SECRETS_FILE', 'client_secrets.json')
    elif provider == 'qq':
        env_config['email'] = os.getenv('QQ_EMAIL')
        env_config['app_password'] = os.getenv('QQ_APP_PASSWORD')
    elif provider == 'outlook':
        env_config['email'] = os.getenv('OUTLOOK_EMAIL')
        env_config['password'] = os.getenv('OUTLOOK_PASSWORD')
    elif provider == 'gmail_password':
        env_config['email'] = os.getenv('GMAIL_EMAIL')
        env_config['app_password'] = os.getenv('GMAIL_APP_PASSWORD')
    
    return env_config

# Example usage
if __name__ == "__main__":
    print("Email Configuration Check")
    print("=" * 30)
    
    providers = ['gmail', 'qq', 'outlook', 'gmail_password']
    
    for provider in providers:
        print(f"\n{provider.upper()}:")
        if EmailConfig.validate_config(provider):
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration is incomplete")
            EmailConfig.print_setup_instructions(provider) 