from celery import shared_task
from order.services.mails.mail_sms_handler import handle_order_completed
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_order_completion(self, data):
    logger.info(f"Processing order completion task: {data}")
    try:
        return handle_order_completed(data)
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)