import os

from panda import Panda

panda = Panda()
panda.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

while True:
    for bus in range(0, 2):
        panda.can_send(0x0, os.urandom(8), bus)

