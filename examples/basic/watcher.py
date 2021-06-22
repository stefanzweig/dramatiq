import argparse
import os
import random
import sys

import dramatiq

if os.getenv("REDIS") == "1":
    from dramatiq.brokers.redis import RedisBroker
    broker = RedisBroker()
    dramatiq.set_broker(broker)

from dramatiq.middleware import CurrentMessage

dramatiq.get_broker().add_middleware(CurrentMessage())

@dramatiq.actor(queue_name='workshop-demo')
def process_demo(id):
    print(">>> {}".format(CurrentMessage.get_current_message().message_id))
