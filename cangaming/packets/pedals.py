import struct

from cangaming.enums import CurrentBinds
from cangaming.packets import packet
from cangaming.structs import gas_pedal_bitstruct

@packet(packet_id=0x165)
def brake_pedal(can_data, controller):
    braking, _ = struct.unpack(">B7s", can_data)

    if braking != 0x28:
        controller.braking = False
        controller.set_keyboard_state[CurrentBinds.KEY_BACKWARD] = False
    else:
        controller.braking = True
        controller.set_keyboard_state[CurrentBinds.KEY_BACKWARD] = True

@packet(packet_id=0x204)
def gas_pedal(can_data, controller):
    _, pedal, _ = gas_pedal_bitstruct.unpack(can_data)

    # Go forward if the pedal is pressed lightly.
    controller.set_keyboard_state[CurrentBinds.KEY_FORWARD] = pedal > 150
