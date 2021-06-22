import argparse
import os
import random
import sys

import dramatiq
from dramatiq.actor import Actor
from node_info import my_hostname
print(f'hostname is {my_hostname}')

broker = dramatiq.broker.get_broker()

queue_name = 'mytest'
priority = 0
options = {}

def dumb_actor():
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-queue", type=str, help="queue's name", default=my_hostname)
    # parser.add_argument("id", type=int, help="the args")
    args = parser.parse_args()
    actor_name = 'dumb_private' if my_hostname == args.queue else 'dumb'

    sender = Actor(dumb_actor, actor_name=actor_name, queue_name=args.queue,
            priority=priority, broker=broker, options=options)
    msg = sender.send()
    print(msg.message_id)

if __name__ == '__main__':
    main()