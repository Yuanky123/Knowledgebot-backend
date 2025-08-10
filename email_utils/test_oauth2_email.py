#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for OAuth2 Email Authentication
This script demonstrates how to use OAuth2 authentication for different email providers.
"""

import os
from oauth2_email import OAuth2EmailSender, setup_gmail_oauth2, setup_outlook_oauth2

def test_gmail_oauth2():
    """Test Gmail OAuth2 authentication"""
    print("Testing Gmail OAuth2 Authentication...")
    print("-" * 40)
    
    sender = OAuth2EmailSender('gmail')
    
    # Check if client secrets file exists
    client_secrets_file = 'client_secrets.json'
    if not os.path.exists(client_secrets_file):
        print("❌ client_secrets.json not found!")
        print("Please follow these steps to set up Gmail OAuth2:")
        setup_gmail_oauth2()
        return False
    
    try:
        # Authenticate with Gmail
        print("🔐 Authenticating with Gmail...")
        sender.authenticate_gmail(client_secrets_file)
        print("✅ Gmail authentication successful!")
        
        # Test sending email
        print("📧 Testing email sending...")
        success = sender.send_email_gmail_api(
            to_email='xwangij@connect.ust.hk',  # Replace with your test email
            subject='Test Email via Gmail OAuth2',
            body='This is a test email sent using Gmail OAuth2 authentication.\n\nThis email was sent automatically to test the OAuth2 setup.'
        )
        
        if success:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_qq_app_password():
    """Test QQ email with app password"""
    print("\nTesting QQ App Password Authentication...")
    print("-" * 40)
    
    sender = OAuth2EmailSender('qq')
    
    # You need to replace these with your actual QQ email and app password
    qq_email = '1592744341@qq.com'  # Replace with your QQ email
    app_password = 'tyiogjsnepwphjha'  # Replace with your QQ app password
    
    try:
        print("🔐 Authenticating with QQ using app password...")
        success = sender.send_email_smtp(
            from_email=qq_email,
            to_email='xwangij@connect.ust.hk',  # Replace with your test email
            subject='Test Email via QQ App Password',
            body='This is a test email sent using QQ app password authentication.\n\nThis email was sent automatically to test the app password setup.',
            app_password=app_password
        )
        
        if success:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_outlook_oauth2():
    """Test Outlook OAuth2 authentication (placeholder)"""
    print("\nTesting Outlook OAuth2 Authentication...")
    print("-" * 40)
    
    print("⚠️  Outlook OAuth2 setup is more complex and requires Azure AD application setup.")
    print("For now, you can use the regular password authentication with STARTTLS.")
    setup_outlook_oauth2()
    return False

def test_outlook_password():
    """Test Outlook with regular password and STARTTLS"""
    print("\nTesting Outlook Password Authentication with STARTTLS...")
    print("-" * 40)
    
    sender = OAuth2EmailSender('outlook')
    
    # You need to replace these with your actual Outlook credentials
    outlook_email = 'xwangij@connect.ust.hk'  # Replace with your Outlook email
    password = 'Wxy201515wxy'  # Replace with your password
    
    try:
        print("🔐 Authenticating with Outlook using password...")
        success = sender.send_email_smtp(
            from_email=outlook_email,
            to_email='xwangij@connect.ust.hk',  # Replace with your test email
            subject='Test Email via Outlook STARTTLS',
            body='This is a test email sent using Outlook with STARTTLS.\n\nThis email was sent automatically to test the STARTTLS setup.',
            password=password
        )
        
        if success:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Email OAuth2 Authentication Test Suite")
    print("=" * 50)
    
    # Test different email providers
    results = {}
    
    # Test Gmail OAuth2
    results['Gmail OAuth2'] = test_gmail_oauth2()
    
    # Test QQ App Password
    results['QQ App Password'] = test_qq_app_password()
    
    # Test Outlook OAuth2 (placeholder)
    results['Outlook OAuth2'] = test_outlook_oauth2()
    
    # Test Outlook Password
    results['Outlook Password'] = test_outlook_password()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for provider, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{provider}: {status}")
    
    print("\n💡 Recommendations:")
    print("- For Gmail: Use OAuth2 for better security")
    print("- For QQ: Use app password (not regular password)")
    print("- For Outlook: Use OAuth2 if possible, otherwise use STARTTLS with password")
    print("- Always enable 2-factor authentication on your email accounts")

if __name__ == "__main__":
    main() 