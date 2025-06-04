import os
import django
import logging
import sys

sys.path.append('/app')
sys.path.append('/app/product-service')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings') 
django.setup()

from shared.utils.rabbit_mq.rpc_server import RPCServer
from product.models import Product

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def product_handler(request_data):
    """Handle product availability requests"""
    product_id = request_data.get('product_id')
    quantity = request_data.get('quantity')
    
    logger.info(f"Checking product {product_id}, quantity {quantity}")

    try:
        product = Product.objects.get(id=product_id)

        if not product.available:
            return {'available': False, 'message': 'Product is not available'}
        # print(f"[Quantity] {quantity}")
        print(f"[Product Id] {product_id}")
        if product.stock_quantity < quantity:
            return {'available': False, 'message': 'Insufficient stock'}

        print("i'm here now")
        try:
            product.stock_quantity -= quantity
            product.save()
        except Exception as e:
            print(f"[Save Error] {e}")
            
        return {'available': True, 'price': str(product.price), 'name': product.name}

    except Product.DoesNotExist:
        logger.warning(f"Product {product_id} not found")
        return {'available': False, 'message': 'Product not found'}
    except Exception as e:
        logger.error(f"Error in product_handler: {e}")
        return {'available': False, 'message': 'Internal server error'}

def main():
    """Start the RPC server"""
    try:
        logger.info("Starting Product Availability RPC Server...")
        
        server = RPCServer(queue_name='product_availability_queue')
        logger.info("RPC Server started, waiting for requests...")
        
        server.serve(product_handler)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()