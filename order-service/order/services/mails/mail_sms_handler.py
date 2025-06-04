import logging
import os
import re
import africastalking
from dotenv import load_dotenv
from django.core.mail import send_mail
from django.conf import settings

load_dotenv()

"""handler to send messages and emails when order created"""


# Initialize Africa's Talking
username = os.getenv('SANDBOX_USERNAME')
api_key = os.getenv('SANDBOX_API_KEY')
africastalking.initialize(username,api_key)

sms = africastalking.SMS
logger = logging.getLogger(__name__)


def format_phone_number(phone):
    """
    Format phone number for Africa's Talking API
    Converts various formats to the expected format
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Handle different input formats
    if phone.startswith('254'):
        # ensure it starts with +
        phone = '+' + phone  # now: +254708099999
        
    elif phone.startswith('0'):
        # Convert 0708063310 to +254708099999
        phone = '+254' + phone[1:]
        
    elif phone.startswith('+254'):
        # Already in correct format: +254708099999
        pass
        
    elif len(phone) == 9:
        # Assume it's missing country code: 708099999-> +254708099999
        phone = '+254' + phone
    
    # Validate final format
    if not re.match(r'^\+254[17]\d{8}$', phone):
        logger.error(f"Invalid phone number format after processing: {phone}")
        return None
        
    return phone


""" function to send email to admin"""
def send_admin_email(data):
    """
    Send simple email notification to admin with improved error handling
    """
    try:
        # Validate required email settings
        if not all([
            hasattr(settings, 'EMAIL_HOST_USER'),
            hasattr(settings, 'EMAIL_HOST_PASSWORD'),
            hasattr(settings, 'DEFAULT_FROM_EMAIL')
        ]):
            logger.error("Email configuration is incomplete in settings")
            return {"status": "failed", "reason": "Email configuration incomplete"}

        order_number = data.get('order_number', 'N/A')
        customer_username = data.get('username', 'Anonymous')
        customer_phone = data.get('customer_phone', 'Not provided')
        product_price = data.get('product_price')
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', os.getenv('ADMIN_EMAIL'))
        if not admin_email:
            logger.error("No admin email address configured")
            return {"status": "failed", "reason": "No admin email configured"}
        
        subject = f'New Order #{order_number} Received'
        message = f"""
            New Order Alert!

            Order Details:
            - Order Number: #{order_number}
            - Product Name: {data.get('product_name', 'N/A')}
            - Product Price Per Unit: {data.get('product_price', 'N/A')}
            - Customer: {customer_username}
            - Customer Phone: {customer_phone}
            - Quantity: {data.get('quantity', 'N/A')}

            Please check the admin panel for full order details.
            """
                    
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
                    
        logger.info(f"Admin email sent successfully for order #{order_number}")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Failed to send admin email: {e}", exc_info=True)
        return {"status": "failed", "reason": str(e)}
    
def send_user_sms(data):
    try:
        customer_phone = data.get('customer_phone')
        customer_username = data.get('username')
        order_number = data.get('order_number')
        
        formatted_phone = format_phone_number(customer_phone)
        
        message = f"Hello {customer_username}, your order #{order_number} has been sucessfully placed. Thank you for shopping with us"
        response = sms.send(message, [formatted_phone])
        logger.info(f"sms sent to {formatted_phone}: {response}")
        return {"status": "Success"}
    
    except Exception as e:
        logger.error(f"Failed to send sms to {customer_username} : {e}")
        return {"status" : "failed"}



def handle_order_completed(data):
    try:
        admin_email = send_admin_email(data)
        user_sms = send_user_sms(data)
        logger.info(f"admin message response : {admin_email}, customer notification sms : {user_sms}")
            

    except Exception as e:
        logger.error(f"Failed to send notification : {e}")

