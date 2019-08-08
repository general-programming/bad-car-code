class KeyboardBinds:
    SILENCE_PRINTS = False

    KEY_FORWARD = "w"
    KEY_BACKWARD = "S"
    KEY_LEFT = "a"
    KEY_RIGHT = "d"
    SHIFT = "shift"
    MOUSE_LEFT = "mouseLeft"
    MOUSE_RIGHT = "mouseRight"

class UndertaleBinds(KeyboardBinds):
    KEY_FORWARD = "up"
    KEY_BACKWARD = "down"
    KEY_LEFT = "left"
    KEY_RIGHT = "right"
    SHIFT = "Z"
    MOUSE_RIGHT = "enter"

class HappyWheelsBinds(KeyboardBinds):
    KEY_FORWARD = "up"
    KEY_BACKWARD = "down"
    KEY_LEFT = "left"
    KEY_RIGHT = "right"
    SHIFT = "space"

class DoomBinds(KeyboardBinds):
    KEY_FORWARD = "up"
    KEY_BACKWARD = "down"
    KEY_LEFT = "left"
    KEY_RIGHT = "right"
    SHIFT = "ctrl"

class SourceBinds(KeyboardBinds):
    # bind [ +left
    # bind ] +right
    KEY_LEFT = "["
    KEY_RIGHT = "]"
    MOUSE_LEFT = "a"
    MOUSE_RIGHT = "d"

class TerminalKeyboard(KeyboardBinds):
    SILENCE_PRINTS = True
    import keyboardthing
    keyboard = keyboardthing.Controller()

    KEY_FORWARD = keyboard.up
    KEY_BACKWARD = keyboard.down
    KEY_LEFT = keyboard.right
    KEY_RIGHT = keyboard.left
    SHIFT = keyboard.enter
    MOUSE_LEFT = keyboard.right
    MOUSE_RIGHT = keyboard.left

CurrentBinds = TerminalKeyboard()
