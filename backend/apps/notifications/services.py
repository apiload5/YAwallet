from django.core.mail import send_mail
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

class NotificationService:
    """Notification service for sending alerts"""
    
    @staticmethod
    def send_transfer_notification(user, recipient, amount, fee, transaction_id):
        """Send transfer notifications"""
        # Send email notification
        if user.email:
            try:
                send_mail(
                    subject='Transfer Confirmation',
                    message=f"""
                    Dear {user.full_name},
                    
                    Your transfer of {amount} PKR has been completed.
                    
                    Transaction ID: {transaction_id}
                    Recipient: {recipient.full_name} ({recipient.phone})
                    Amount: {amount} PKR
                    Fee: {fee} PKR
                    Total: {amount + fee} PKR
                    
                    New Balance: {user.wallet.balance} PKR
                    
                    Thank you for using YaWallet!
                    """,
                    from_email='noreply@yawallet.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
        
        # Send SMS notification (mock)
        # In production, integrate with a real SMS service
        try:
            # Mock SMS
            logger.info(f"SMS to {user.phone}: Transfer of {amount} PKR completed")
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
    
    @staticmethod
    def send_kyc_notification(user, status, reason=None):
        """Send KYC status notification"""
        if user.email:
            try:
                subject = f"KYC Status Update - {status}"
                message = f"""
                Dear {user.full_name},
                
                Your KYC verification status has been updated to: {status}
                """
                
                if reason:
                    message += f"\nReason: {reason}"
                
                message += "\n\nThank you for using YaWallet!"
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='noreply@yawallet.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send KYC notification: {e}")
