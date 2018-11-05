import time
import struct
import threading
import time

from panda import Panda
import pyautogui

panda = Panda()
start = time.time()

# https://stackoverflow.com/questions/46736652/pyautogui-press-causing-lag-when-called
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

class CarController:
    def __init__(self):
        self.running = True
        self.threads = []

        self.keyboard_state = {
            "w": False,
            "a": False,
            "S": False,
            "d": False,
            "shift": False,
            "mouseLeft": False,
            "mouseRight": False,
        }
        self.set_keyboard_state = self.keyboard_state.copy()
        self.neutral_wheel = 0
        self.wheel_offset = 0
        self.wheel_pos = 0
        self.braking = 0

    def mouse_thread(self):
        while self.running:
            if self.keyboard_state["mouseLeft"] or self.keyboard_state["mouseRight"]:
                if self.keyboard_state["mouseLeft"]:
                    drag_offset = -35
                else:
                    drag_offset = 35

                pyautogui.moveRel(drag_offset, 0, duration=0)
            time.sleep(0.15)

    def loop(self):
        while self.running:
            can_recv = panda.can_recv()
            for can_message in can_recv:
                can_id = can_message[0]
                can_data = can_message[2]
                can_bus = can_message[3]
                recv_time = time.time()

                if can_bus != 0:
                    continue

                # left/right wheel packets (engine needs to be on)
                if can_id == 0x76:
                    wheel_pos, junk = struct.unpack(">h6s", can_data)
                    self.wheel_pos = wheel_pos

                    if not self.neutral_wheel and (recv_time - start) > 1:
                        self.neutral_wheel = wheel_pos
                    elif self.neutral_wheel:
                        self.wheel_offset = wheel_pos - self.neutral_wheel

                    if self.wheel_offset > 50:
                        self.set_keyboard_state["a"] = True
                        self.set_keyboard_state["d"] = False
                    elif self.wheel_offset < -50:
                        self.set_keyboard_state["a"] = False
                        self.set_keyboard_state["d"] = True
                    else:
                        self.set_keyboard_state["a"] = False
                        self.set_keyboard_state["d"] = False

                # backwards cruise control packet (todo: don't use cruise control)
                elif can_id == 0x165:
                    braking, junk = struct.unpack(">B7s", can_data)
                    if braking != 0x28:
                        self.braking = False
                        self.set_keyboard_state["S"] = False
                    else:
                        self.braking = True
                        self.set_keyboard_state["S"] = True

                # forward pedal data
                elif can_id == 0x204:
                    junk, pedal, junk = struct.unpack(">BH5s", can_data)
                    if pedal > 1500:
                        self.set_keyboard_state["w"] = True
                    else:
                        self.set_keyboard_state["w"] = False

                elif can_id == 0x3c3:
                    highbeam, junk = struct.unpack(">B7s", can_data)
                    if highbeam != 0x5e:
                        self.set_keyboard_state["shift"] = False
                    else:
                        self.set_keyboard_state["shift"] = True

                elif can_id == 0x83:
                    current_signal, junk = struct.unpack(">B7s", can_data)
                    if current_signal == 0x10:
                        self.set_keyboard_state["mouseLeft"] = True
                        self.set_keyboard_state["mouseRight"] = False
                    elif current_signal == 0x20:
                        self.set_keyboard_state["mouseLeft"] = False
                        self.set_keyboard_state["mouseRight"] = True
                    else:
                        self.set_keyboard_state["mouseLeft"] = False
                        self.set_keyboard_state["mouseRight"] = False

                # Set state codes
                if self.set_keyboard_state != self.keyboard_state:
                    for key, press in self.set_keyboard_state.items():
                        if self.keyboard_state[key] == press:
                            continue

                        print(key, press)
                        if key in ("mouseLeft" or "mouseRight"):
                            continue
                        else:
                            if press:
                                pyautogui.keyDown(key)
                            else:
                                pyautogui.keyUp(key)
                    self.keyboard_state = self.set_keyboard_state.copy()

            # Log state once done.
            self.log()

    def main(self):
        # Thread startup
        self.threads.append(threading.Thread(target=self.mouse_thread).start())

        # Main loop
        try:
            self.loop()
        except KeyboardInterrupt:
            self.running = False

    def log(self):
        print("neutral: %s; wheel: %s; offset: %s; braking: %s; actions: %s" % (
            self.neutral_wheel,
            self.wheel_pos,
            self.wheel_offset,
            self.braking,
            self.keyboard_state
        ))

if __name__ == "__main__":
    controller = CarController()
    controller.main()
