# Email OAuth2 Authentication Setup Guide

This guide will help you set up OAuth2 authentication for different email providers to resolve the authentication issues you're experiencing.

## Overview

Your email provider requires **OAuth2 authentication with STARTTLS**, but you're currently trying to use password-based authentication. This guide provides solutions for:

- **Gmail**: OAuth2 authentication (recommended) or App Password
- **Outlook/Office365**: OAuth2 authentication or STARTTLS with password
- **QQ**: App Password (QQ doesn't support OAuth2)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_oauth2.txt
```

### 2. Choose Your Email Provider

Based on your notebook, you have several email accounts. Choose the one you want to use:

#### Option A: Gmail OAuth2 (Recommended)
- **Email**: `this.is.wangxiaoyu@gmail.com`
- **Method**: OAuth2 (most secure)

#### Option B: QQ App Password
- **Email**: `1592744341@qq.com`
- **Method**: App Password (already configured)

#### Option C: Outlook STARTTLS
- **Email**: `xwangij@connect.ust.hk`
- **Method**: STARTTLS with password

### 3. Test Your Setup

```bash
python test_oauth2_email.py
```

## Detailed Setup Instructions

### Gmail OAuth2 Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the JSON file

4. **Save Client Secrets**
   - Rename the downloaded file to `client_secrets.json`
   - Place it in the same directory as your Python scripts

5. **Test Gmail OAuth2**
   ```python
   from oauth2_email import OAuth2EmailSender
   
   sender = OAuth2EmailSender('gmail')
   sender.authenticate_gmail('client_secrets.json')
   sender.send_email_gmail_api(
       to_email='xwangij@connect.ust.hk',
       subject='Test Email',
       body='This is a test email via Gmail OAuth2'
   )
   ```

### QQ App Password Setup

QQ is already configured in your notebook. The app password approach is working:

```python
from oauth2_email import OAuth2EmailSender

sender = OAuth2EmailSender('qq')
sender.send_email_smtp(
    from_email='1592744341@qq.com',
    to_email='xwangij@connect.ust.hk',
    subject='Test Email',
    body='This is a test email via QQ app password',
    app_password='tyiogjsnepwphjha'
)
```

### Outlook STARTTLS Setup

For your Outlook account, you can use STARTTLS with your password:

```python
from oauth2_email import OAuth2EmailSender

sender = OAuth2EmailSender('outlook')
sender.send_email_smtp(
    from_email='xwangij@connect.ust.hk',
    to_email='xwangij@connect.ust.hk',
    subject='Test Email',
    body='This is a test email via Outlook STARTTLS',
    password='Wxy201515wxy'
)
```

## Troubleshooting

### Common Issues

1. **"SMTP AUTH extension not supported"**
   - **Solution**: Use OAuth2 or app password instead of regular password

2. **"Username and Password not accepted"**
   - **Solution**: Enable 2FA and use app password, or use OAuth2

3. **"Connection timeout"**
   - **Solution**: Check firewall settings and try different ports

### Gmail OAuth2 Issues

1. **"client_secrets.json not found"**
   - Download the file from Google Cloud Console
   - Make sure it's in the correct directory

2. **"Invalid client"**
   - Check that you've enabled Gmail API
   - Verify the client secrets file is correct

3. **"Access denied"**
   - Make sure you've granted the necessary permissions
   - Check that the OAuth consent screen is configured

### QQ App Password Issues

1. **"Authentication failed"**
   - Generate a new app password
   - Make sure you're using the app password, not your regular password

2. **"Connection refused"**
   - Check that port 587 is not blocked
   - Try using port 465 with SSL instead

### Outlook Issues

1. **"SMTP authentication failed"**
   - Enable "Less secure app access" (if available)
   - Or use an app password if 2FA is enabled

2. **"STARTTLS not supported"**
   - Try using port 465 with SSL instead of STARTTLS

## Security Best Practices

1. **Never commit credentials to version control**
   - Use environment variables for sensitive data
   - Add `*.json`, `*.pickle` to `.gitignore`

2. **Use OAuth2 when possible**
   - More secure than password-based authentication
   - Tokens can be revoked without changing passwords

3. **Enable 2-Factor Authentication**
   - Required for app passwords
   - Provides additional security

4. **Use App Passwords**
   - Generate unique passwords for each application
   - Can be revoked individually

## File Structure

```
Knowledgebot-backend/
├── oauth2_email.py          # Main OAuth2 email sender class
├── email_config.py          # Configuration management
├── test_oauth2_email.py     # Test script
├── requirements_oauth2.txt   # Dependencies
├── README_EMAIL_OAUTH2.md   # This file
├── client_secrets.json      # Gmail OAuth2 credentials (download)
└── *.pickle                 # OAuth2 tokens (auto-generated)
```

## Environment Variables

For production use, set these environment variables:

```bash
# Gmail OAuth2
export GMAIL_CLIENT_SECRETS_FILE="path/to/client_secrets.json"

# QQ App Password
export QQ_EMAIL="your_qq_email@qq.com"
export QQ_APP_PASSWORD="your_app_password"

# Outlook
export OUTLOOK_EMAIL="your_outlook_email@outlook.com"
export OUTLOOK_PASSWORD="your_password_or_app_password"
```

## Next Steps

1. **Choose your preferred email provider**
2. **Follow the setup instructions for that provider**
3. **Test the authentication**
4. **Integrate into your application**

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your email provider's settings
3. Test with the provided test scripts
4. Check the error messages for specific guidance

## Files Created

- `oauth2_email.py`: Main OAuth2 email authentication class
- `email_config.py`: Configuration management
- `test_oauth2_email.py`: Comprehensive test suite
- `requirements_oauth2.txt`: Required dependencies
- `README_EMAIL_OAUTH2.md`: This comprehensive guide 