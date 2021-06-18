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

@dramatiq.actor(queue_name='robot_ztp', max_retries=5, throws=(ValueError,))
def process(x, y, z, extra_options=None):
    print(">>> {}".format(CurrentMessage.get_current_message()))
    testbenches = []
    if extra_options is not None:
        if 'testbench' in extra_options:
            testbenches = extra_options['testbench']

    fake_hostname = 'DESKTOP-F076DIK'
    print(">>> the hostname is " + fake_hostname)
    print(" ".join(str(x) for x in testbenches if x != ""))
    if len(testbenches) > 0 and fake_hostname not in testbenches:
        print(">>> reschedule.")
        dramatiq.get_broker().enqueue(CurrentMessage.get_current_message())
        return

    # process.logger.info("The sum of %d and %d is %d.", x, y, x + y)
    # if ( x + y ) % 2:
        # dramatiq.get_broker().enqueue(CurrentMessage.get_current_message())
        # raise ValueError('odd number!')


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, help="the number of messages to enqueue")
    args = parser.parse_args()
    option = {}
    option['testbench'] = ['DESKTOP-F076DIK']
    for _ in range(args.count):
        process.send(1, 1, 0, option)
        # add.send(random.randint(0, 1000), random.randint(0, 1000))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
