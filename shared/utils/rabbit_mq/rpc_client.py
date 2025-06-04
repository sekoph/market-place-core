
import pika
import uuid
import json
import os
import time
import logging

logger = logging.getLogger(__name__)

class RPCClient:
    def __init__(self, queue_name='default_queue', max_retries=5, retry_delay=2):
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None
        
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
                logger.info(f"RPC Client attempting to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries})")
                self.connection = pika.BlockingConnection(self._connection_params)
                self.channel = self.connection.channel()
                
                # Set up callback queue
                result = self.channel.queue_declare(queue='', exclusive=True)
                self.callback_queue = result.method.queue
                
                self.channel.basic_consume(
                    queue=self.callback_queue,
                    on_message_callback=self.on_response,
                    auto_ack=True
                )
                
                logger.info("RPC Client successfully connected to RabbitMQ")
                return
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"RPC Client failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries exceeded. Could not connect to RabbitMQ")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
                raise

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, payload: dict, timeout=30):
        """Make RPC call with timeout"""
        try:
            self._ensure_connection()
            
            self.response = None
            self.corr_id = str(uuid.uuid4())
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(payload),
            )
            
            # Wait for response with timeout
            start_time = time.time()
            while self.response is None:
                if time.time() - start_time > timeout:
                    logger.error(f"RPC call timeout after {timeout} seconds")
                    raise TimeoutError(f"RPC call timeout after {timeout} seconds")
                
                self.connection.process_data_events(time_limit=1)
            
            return self.response
            
        except Exception as e:
            logger.error(f"RPC call failed: {e}")
            # Reset connection on error
            self.connection = None
            self.channel = None
            raise

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("RPC Client connection closed")
            except Exception as e:
                logger.warning(f"Error closing RPC Client connection: {e}")
