import struct

from cangaming.enums import CurrentBinds
from cangaming.packets import packet

@packet(packet_id=0x3c3)
def high_beam(can_data, controller):
    highbeam, _ = struct.unpack(">B7s", can_data)
    if highbeam != 0x5e:
        controller.set_keyboard_state[CurrentBinds.SHIFT] = False
    else:
        controller.set_keyboard_state[CurrentBinds.SHIFT] = True
