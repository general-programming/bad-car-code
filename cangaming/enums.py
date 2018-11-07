class KeyboardBinds:
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

class SourceBinds(KeyboardBinds):
    # bind [ +left
    # bind ] +right
    KEY_LEFT = "["
    KEY_RIGHT = "]"
    MOUSE_LEFT = "a"
    MOUSE_RIGHT = "d"

CurrentBinds = HappyWheelsBinds()
