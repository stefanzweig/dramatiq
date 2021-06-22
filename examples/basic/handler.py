import argparse
import os
import random
import sys

import dramatiq
from node_info import my_hostname

if os.getenv("REDIS") == "1":
    from dramatiq.brokers.redis import RedisBroker
    broker = RedisBroker()
    dramatiq.set_broker(broker)

from dramatiq.middleware import CurrentMessage

dramatiq.get_broker().add_middleware(CurrentMessage())

@dramatiq.actor(queue_name=my_hostname)
def dumb_private():
    message = CurrentMessage.get_current_message()
    print(">>> Special {}".format(message.message_id))
    print(">>> Special {}".format(message.queue_name))

@dramatiq.actor(queue_name='danfeng')
def dumb():
    message = CurrentMessage.get_current_message()
    print(">>> Common {}".format(message.message_id))
    print(">>> Common {}".format(message.queue_name))
