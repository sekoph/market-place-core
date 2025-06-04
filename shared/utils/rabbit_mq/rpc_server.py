
import pika
import uuid
import json
import os
import time
import logging

logger = logging.getLogger(__name__)


class RPCServer:
    def __init__(self, queue_name='default_queue', max_retries=5, retry_delay=2):
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None
        
        # Connection parameters
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
        
        # Initialize connection
        self._ensure_connection()

    def _ensure_connection(self):
        """Ensure we have a valid connection, create one if needed"""
        if self.connection is None or self.connection.is_closed:
            self._connect()

    def _connect(self):
        """Establish connection to RabbitMQ with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"RPC Server attempting to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries})")
                self.connection = pika.BlockingConnection(self._connection_params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                
                logger.info("RPC Server successfully connected to RabbitMQ")
                return
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"RPC Server failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries exceeded. Could not connect to RabbitMQ")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
                raise

    def serve(self, handler_func):
        """Start serving RPC requests"""
        try:
            self._ensure_connection()
            
            def on_request(ch, method, props, body):
                try:
                    request_data = json.loads(body)
                    logger.info(f"Processing RPC request: {request_data}")
                    
                    response_data = handler_func(request_data)
                    
                    ch.basic_publish(
                        exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(
                            correlation_id=props.correlation_id
                        ),
                        body=json.dumps(response_data),
                    )
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    logger.error(f"Error processing RPC request: {e}")
                    # Send error response
                    error_response = {"error": str(e)}
                    ch.basic_publish(
                        exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(
                            correlation_id=props.correlation_id
                        ),
                        body=json.dumps(error_response),
                    )
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Set QoS to process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            print(f" [*] Waiting for RPC requests on queue: {self.queue_name}")
            logger.info(f"RPC Server listening on queue: {self.queue_name}")
            
            self.channel.basic_consume(
                queue=self.queue_name, 
                on_message_callback=on_request
            )
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("RPC Server shutting down...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"RPC Server error: {e}")
            # Reset connection on error
            self.connection = None
            self.channel = None
            raise

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("RPC Server connection closed")
            except Exception as e:
                logger.warning(f"Error closing RPC Server connection: {e}")