from panda import Panda
import time

panda = Panda()
messages = 0
last = time.time()

while True:
    can_recv = panda.can_recv()
    if (time.time() - last) > 1:
        print("Got {messages} in a second.".format(
            messages=messages
        ))
        messages = 0
        last = time.time()
    messages += len(can_recv)
    # print(can_recv)