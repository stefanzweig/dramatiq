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

@dramatiq.actor(max_retries=5, throws=(ValueError,))
def add(x, y):
    print(">>> {}".format(CurrentMessage.get_current_message()))
    add.logger.info("The sum of %d and %d is %d.", x, y, x + y)
    if ( x + y ) % 2:
        # dramatiq.get_broker().enqueue(CurrentMessage.get_current_message())
        raise ValueError('odd number!')


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, help="the number of messages to enqueue")
    args = parser.parse_args()
    for _ in range(args.count):
        add.send(random.randint(0, 1000), random.randint(0, 1000))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
