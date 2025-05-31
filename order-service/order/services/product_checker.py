from shared.utils.rabbit_mq.rpc_client import RPCClient


""" Function to check if product is available at with product service """

def check_product_availability(product_id, quantity):
    client = RPCClient(queue_name='product_availability_queue')
    response = client.call({'product_id': str(product_id), 'quantity': quantity})
    return response