import struct

from cangaming.enums import CurrentBinds
from cangaming.packets import packet

@packet(packet_id=0x83)
def turn_signal(can_data, controller):
    current_signal, _ = struct.unpack(">B7s", can_data)
    if current_signal == 0x10:
        controller.trigger_flag(CurrentBinds.MOUSE_LEFT, CurrentBinds.MOUSE_RIGHT)
    elif current_signal == 0x20:
        controller.trigger_flag(CurrentBinds.MOUSE_RIGHT, CurrentBinds.MOUSE_LEFT)
    else:
        controller.unset_flags(CurrentBinds.MOUSE_LEFT, CurrentBinds.MOUSE_RIGHT)