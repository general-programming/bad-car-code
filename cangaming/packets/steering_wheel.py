import struct
import time

from cangaming.enums import CurrentBinds
from cangaming.packets import packet

@packet(packet_id=0x76)
def steering_wheel(can_data, controller):
    wheel_pos, _ = struct.unpack(">h6s", can_data)
    controller.wheel_pos = wheel_pos

    # Set the neutral wheel position after a second.
    if controller.neutral_wheel != 0:
        controller.wheel_offset = wheel_pos - controller.neutral_wheel
    elif (controller.neutral_wheel == 0) and (time.time() - controller.start) > 1:
        controller.neutral_wheel = wheel_pos

    if controller.wheel_offset > 15:
        controller.trigger_flag(CurrentBinds.KEY_LEFT, CurrentBinds.KEY_RIGHT)
    elif controller.wheel_offset < -15:
        controller.trigger_flag(CurrentBinds.KEY_RIGHT, CurrentBinds.KEY_LEFT)
    else:
        controller.unset_flags(CurrentBinds.KEY_LEFT, CurrentBinds.KEY_RIGHT)