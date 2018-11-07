import time
import struct
import threading
import json

import pyautogui

from panda import Panda
from redis import StrictRedis

from enums import KeyboardBinds, CurrentBinds
from structs import gas_pedal_bitstruct

redis = StrictRedis()
panda = Panda()
start = time.time()


class CarController(object):
    def __init__(self):
        self.running = True
        self.threads = []

        self.keyboard_state = {
            CurrentBinds.KEY_FORWARD: False,
            CurrentBinds.KEY_LEFT: False,
            CurrentBinds.KEY_BACKWARD: False,
            CurrentBinds.KEY_RIGHT: False,
            CurrentBinds.SHIFT: False,
            CurrentBinds.MOUSE_LEFT: False,
            CurrentBinds.MOUSE_RIGHT: False,
        }
        self.set_keyboard_state = self.keyboard_state.copy()
        self._neutral_wheel = 0
        self.wheel_offset = 0
        self.wheel_pos = 0
        self.braking = False

    @property
    def neutral_wheel(self):
        return self._neutral_wheel

    @neutral_wheel.setter
    def neutral_wheel(self, value):
        self._neutral_wheel = value
        redis.hset("can:gamebus", "wheel:neutral", value)

    def mouse_thread(self):
        while self.running:
            if self.keyboard_state[CurrentBinds.MOUSE_LEFT] or self.keyboard_state[CurrentBinds.MOUSE_RIGHT]:
                if self.keyboard_state[CurrentBinds.MOUSE_LEFT] and CurrentBinds.MOUSE_LEFT == KeyboardBinds.MOUSE_LEFT:
                    drag_offset = -50
                elif CurrentBinds.MOUSE_RIGHT == KeyboardBinds.MOUSE_RIGHT:
                    drag_offset = 50
                else:
                    drag_offset = None

                if drag_offset:
                    pyautogui.moveRel(drag_offset, 0, duration=0)

            time.sleep(0.05)

    def trigger_flag(self, flag, *flags_to_unset):
        self.set_keyboard_state[flag] = True
        self.unset_flags(*flags_to_unset)

    def unset_flags(self, *flags):
        for flag in flags:
            self.set_keyboard_state[flag] = False

    def loop(self):
        while self.running:
            can_recv = panda.can_recv()
            for can_message in can_recv:
                can_id = can_message[0]
                can_data = can_message[2]
                can_bus = can_message[3]
                recv_time = time.time()

                # We only care about messages on bus 0
                if can_bus != 0:
                    continue

                # left/right wheel packets (engine needs to be on)
                if can_id == 0x76:
                    wheel_pos, _ = struct.unpack(">h6s", can_data)
                    self.wheel_pos = wheel_pos

                    # Set the neutral wheel position after a second.
                    if self.neutral_wheel != 0:
                        self.wheel_offset = wheel_pos - self.neutral_wheel
                    elif (self.neutral_wheel == 0) and (recv_time - start) > 1:
                        self.neutral_wheel = wheel_pos

                    if self.wheel_offset > 15:
                        self.trigger_flag(CurrentBinds.KEY_LEFT, CurrentBinds.KEY_RIGHT)
                    elif self.wheel_offset < -15:
                        self.trigger_flag(CurrentBinds.KEY_RIGHT, CurrentBinds.KEY_LEFT)
                    else:
                        self.unset_flags(CurrentBinds.KEY_LEFT, CurrentBinds.KEY_RIGHT)

                # backwards cruise control packet (todo: don't use cruise control)
                elif can_id == 0x165:
                    braking, _ = struct.unpack(">B7s", can_data)
                    if braking != 0x28:
                        self.braking = False
                        self.set_keyboard_state[CurrentBinds.KEY_BACKWARD] = False
                    else:
                        self.braking = True
                        self.set_keyboard_state[CurrentBinds.KEY_BACKWARD] = True

                # forward pedal data
                elif can_id == 0x204:
                    _, pedal, _ = gas_pedal_bitstruct.unpack(can_data)
                    if pedal > 150:
                        self.set_keyboard_state[CurrentBinds.KEY_FORWARD] = True
                    else:
                        self.set_keyboard_state[CurrentBinds.KEY_FORWARD] = False

                # Check high beam on bit
                elif can_id == 0x3c3:
                    highbeam, _ = struct.unpack(">B7s", can_data)
                    if highbeam != 0x5e:
                        self.set_keyboard_state[CurrentBinds.SHIFT] = False
                    else:
                        self.set_keyboard_state[CurrentBinds.SHIFT] = True

                elif can_id == 0x83:
                    current_signal, _ = struct.unpack(">B7s", can_data)
                    if current_signal == 0x10:
                        self.trigger_flag(CurrentBinds.MOUSE_LEFT, CurrentBinds.MOUSE_RIGHT)
                    elif current_signal == 0x20:
                        self.trigger_flag(CurrentBinds.MOUSE_RIGHT, CurrentBinds.MOUSE_LEFT)
                    else:
                        self.unset_flags(CurrentBinds.MOUSE_LEFT, CurrentBinds.MOUSE_RIGHT)

                # Set state codes
                if self.set_keyboard_state != self.keyboard_state:
                    for key, press in self.set_keyboard_state.items():
                        # No pressu or releaseu keys that have already been set.
                        if self.keyboard_state[key] == press:
                            continue

                        # Log press and do update stat.
                        print(key, press)
                        self.log()

                        # Skip mouse moving keys
                        if key == KeyboardBinds.MOUSE_LEFT or key == KeyboardBinds.MOUSE_RIGHT:
                            continue
                        else:
                            # #bongokey
                            if press:
                                pyautogui.keyDown(key)
                            else:
                                pyautogui.keyUp(key)
                    self.keyboard_state = self.set_keyboard_state.copy()

            # Log state once done.
            # self.log()

    def main(self):
        # Thread startup
        self.threads.append(threading.Thread(target=self.mouse_thread).start())

        # Main loop
        try:
            self.loop()
        except KeyboardInterrupt:
            self.running = False

    def log(self):
        log = {
            "wheel": {
                "current": self.wheel_pos,
                "offset": self.wheel_offset,
            },
            "braking": self.braking,
            "keys": self.keyboard_state,
        }

        redis.publish("can:gamebus", json.dumps(log))

if __name__ == "__main__":
    controller = CarController()
    controller.main()
