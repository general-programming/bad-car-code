import time
import struct
import threading
import json

import pyautogui

from panda import Panda
from redis import StrictRedis

from cangaming.packets import PACKET_HANDLERS
from cangaming.enums import KeyboardBinds, CurrentBinds

# Enable failsafe and set pyautogui pause to zero. #YOLO
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

class CarController(object):
    def __init__(self):
        self.running = True
        self.start = time.time()
        self.threads = []

        self.redis = StrictRedis()
        self.panda = Panda()

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
        self.redis.hset("can:gamebus", "wheel:neutral", value)

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
            can_recv = self.panda.can_recv()
            for can_message in can_recv:
                can_id = can_message[0]
                can_data = can_message[2]
                can_bus = can_message[3]

                # We only care about messages on bus 0
                if can_bus != 0:
                    continue

                # Send the packet data to the respective handlers.
                if can_id in PACKET_HANDLERS:
                    PACKET_HANDLERS[can_id](can_data, self)

                # Update state codes when changed.
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

        self.redis.publish("can:gamebus", json.dumps(log))
