#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Working Email Example
This demonstrates the QQ email authentication that's already working.
"""

from .oauth2_email import OAuth2EmailSender

# def send_test_email():
#     """Send a test email using QQ app password (already working)"""
    
#     # Initialize QQ email sender
#     sender = OAuth2EmailSender('qq')
    
#     # Your QQ email configuration (already working)
#     qq_email = '1592744341@qq.com'
#     app_password = 'tyiogjsnepwphjha'
    
#     # Send test email
#     success = sender.send_email_smtp(
#         from_email=qq_email,
#         to_email='xwangij@connect.ust.hk',  # You can change this to any email
#         subject='Test Email - OAuth2 Setup Working!',
#         body='''
#         Hello!

#         This email confirms that your OAuth2 email setup is working correctly.

#         ✅ QQ App Password authentication is working
#         ✅ STARTTLS connection is established
#         ✅ Email is being sent successfully

#         You can now use this configuration in your applications.

#         Best regards,
#         Your Email System
#         ''',
#         app_password=app_password
#     )
    
#     if success:
#         print("✅ Email sent successfully!")
#         print("📧 Check your inbox for the test email")
#         return True
#     else:
#         print("❌ Failed to send email")
#         return False

def send_custom_email(to_email, subject, body):
    """Send a custom email using QQ"""
    
    sender = OAuth2EmailSender('qq')
    qq_email = '1592744341@qq.com'
    app_password = 'tyiogjsnepwphjha'
    
    success = sender.send_email_smtp(
        from_email=qq_email,
        to_email=to_email,
        subject=subject,
        body=body,
        app_password=app_password
    )
    
    if success:
        print(f"✅ Email sent successfully to {to_email}")
        return True
    else:
        print(f"❌ Failed to send email to {to_email}")
        return False

if __name__ == "__main__":
    print("🚀 Working Email Example")
    print("=" * 30)
    
    # # Send test email
    # print("📧 Sending test email...")
    # send_test_email()
    
    # Example of sending custom email
    print("\n📧 Example of sending custom email...")
    send_custom_email(
        to_email='2013654968@qq.com', # '1592744341@qq.com', #'yzhangiy@connect.ust.hk'
        subject='Custom Email Test',
        body='This is a custom email sent using the working QQ configuration.'
    )