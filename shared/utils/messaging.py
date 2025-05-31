import json
import os
import django
import pika
import logging
import time
from typing import Dict, Any, Callable
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')

django.setup()

from django.conf import settings

class MessageBroker:
    def __init__(self):
        self.connection = None
        self.channel = None
        # Don't connect immediately - wait until first use
        self._connection_params = pika.ConnectionParameters(
            host=os.environ.get('RABBITMQ_HOST', 'rabbitmq'),
            port=int(os.environ.get('RABBITMQ_PORT', 5672)),
            virtual_host=os.environ.get('RABBITMQ_VHOST', '/'),
            credentials=pika.PlainCredentials(
                os.environ.get('RABBITMQ_DEFAULT_USER', 'myuser'),
                os.environ.get('RABBITMQ_DEFAULT_PASS', 'mypassword')
            ),
            heartbeat=600,
            blocked_connection_timeout=300,
        )
    
    def _ensure_connection(self, max_retries=5, retry_delay=2):
        """Ensure we have a valid connection, create one if needed"""
        if self.connection is None or self.connection.is_closed:
            self._connect(max_retries, retry_delay)
    
    def _connect(self, max_retries=5, retry_delay=2):
        """Establish connection to RabbitMQ with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{max_retries})")
                self.connection = pika.BlockingConnection(self._connection_params)
                self.channel = self.connection.channel()
                logger.info("Successfully connected to RabbitMQ")
                return
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries exceeded. Could not connect to RabbitMQ")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
                raise
    
    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to RabbitMQ"""
        try:
            # Ensure connection before publishing
            self._ensure_connection()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange='microservices_events',
                exchange_type='topic',
                durable=True
            )
            
            message = {
                'event_type': event_type,
                'data': data,
                'timestamp': timezone.now().isoformat(),
                'service': settings.SERVICE_NAME
            }
            
            self.channel.basic_publish(
                exchange='microservices_events',
                routing_key=event_type,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published event: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            # Reset connection on error
            self.connection = None
            self.channel = None
            raise
    
    def consume_events(self, event_types: list, callback: Callable):
        """Consume events from RabbitMQ"""
        try:
            # Ensure connection before consuming
            self._ensure_connection()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange='microservices_events',
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue
            queue_name = f"{settings.SERVICE_NAME}_events"
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queue to exchange for each event type
            for event_type in event_types:
                self.channel.queue_bind(
                    exchange='microservices_events',
                    queue=queue_name,
                    routing_key=event_type
                )
            
            def wrapper(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=wrapper
            )
            
            logger.info(f"Started consuming events: {event_types}")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Failed to consume events: {e}")
            # Reset connection on error
            self.connection = None
            self.channel = None
            raise
    
    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
            except Exception as e:
                logger.warning(f"Error closing RabbitMQ connection: {e}")

# Singleton pattern - create instance but don't connect yet
_broker_instance = None

def get_broker():
    """Get the singleton MessageBroker instance"""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = MessageBroker()
    return _broker_instance

def publish_event(event_type: str, data: Dict[str, Any]):
    """Convenience function to publish events"""
    broker = get_broker()
    broker.publish_event(event_type, data)

def consume_event(event_types: list, callback: Callable):
    """Convenience function to consume events"""
    broker = get_broker()
    broker.consume_events(event_types, callback)

# For backward compatibility, if you have code that directly uses broker
# This will now be lazily initialized
@property
def broker():
    return get_broker()

# Make broker available as module attribute for backward compatibility
import sys
sys.modules[__name__].broker = property(lambda self: get_broker())