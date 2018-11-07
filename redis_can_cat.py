from redis import StrictRedis
from panda import Panda
import time
import binascii

panda = Panda()
r = StrictRedis()
messages = 0
last = time.time()
seen = set()

while True:
    can_recv = panda.can_recv()
    for can_message in can_recv:
        can_id = can_message[0]
        if can_id in [
            # g sensors
            145,
            146
        ]:
            continue
        if bytes(can_message[2]) in seen:
            continue

        if r.sismember("can:%s" % (can_message[0]), bytes(can_message[2])):
            continue

        print(can_message[0], ''.join(format(ord(byte), '08b') for byte in str(can_message[2])))
        seen.add(bytes(can_message[2]))

    if (time.time() - last) > 1:
        print("Got {messages} in a second.".format(
            messages=messages
        ))
        messages = 0
        last = time.time()
    messages += len(can_recv)
