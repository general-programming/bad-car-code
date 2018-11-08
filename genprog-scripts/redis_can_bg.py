from redis import StrictRedis
from panda import Panda
import time

panda = Panda()
r = StrictRedis()
messages = 0
last = time.time()

while True:
    can_recv = panda.can_recv()
    for can_message in can_recv:
        r.sadd("can:%s" % (can_message[0]), bytes(can_message[2]))

    if (time.time() - last) > 1:
        print("Got {messages} in a second.".format(
            messages=messages
        ))
        messages = 0
        last = time.time()
    messages += len(can_recv)
