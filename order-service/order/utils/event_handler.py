from shared.utils.messaging import consume_event
from .tasks import process_order_completion


EVENT_HANDLERS = {
    'order.created': process_order_completion
}

def handle_event(message):
    event_type = message.get('event_type')
    data = message.get('data')
    
    task = EVENT_HANDLERS.get(event_type)
    
    
    if task:
        task.delay(data)
    else:
        print("no task defined for the event: {event_type}")
        
def start_event_listener():
    consume_event(event_types=list(EVENT_HANDLERS.keys()), callback=handle_event)