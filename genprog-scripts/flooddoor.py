from panda import Panda
import os
import time

panda = Panda()
panda.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

bus = 0

while True:
    # 0x83 dash lights
    # panda.can_send(0x83, "\x50\x00\x00\x00\x00\x00\x00\x00", bus)

    # doors but it restarts the car when flooded?
    # panda.can_send(0x3b3, "\x44\x88\xb2\x0b\x00\x00\x00\x22", bus)

    # general random
    panda.can_send(0x3b3, os.urandom(8), bus)

    time.sleep(0.02)
