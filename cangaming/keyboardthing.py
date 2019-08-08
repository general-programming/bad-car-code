import sys

specialMaps = {
    "CAPS": "capslock",
    "ENTER": "enter",
    "BACKSPACE": "backspace",
    "UP": "up",
    "DOWN": "down",
    "LEFT": "left",
    "RIGHT": "right",
    "ENTER": "enter",
    "^C": "",
    "^Z": "",
    "SPACEBAR": "space"
}

class Controller:
    def __init__(self):
        self.state = [
            "~ ! @ # $ % ^ & * ( ) _ +",
            "` 1 2 3 4 5 6 7 8 9 0 - =",
            "q w e r t y u i o p [ ] \\",
            "CAPS a s d f g h j k l ; ' ENTER",
            "z x c v b n m , . / < > BACKSPACE",
            "? : \" { } | SPACEBAR UP DOWN LEFT RIGHT ^C ^Z",
        ]

        self.keyRow = 0
        self.keyColumn = 0

        for index, row in enumerate(self.state):
            self.state[index] = row.split(" ")

        self.printKeyboard()

    @property
    def currentKey(self):
        return self.state[self.keyRow][self.keyColumn]

    def printKeyboard(self):
        currentKey = self.currentKey

        for row in self.state:
            for key in row:
                if key == currentKey:
                    sys.stdout.write("[" + key + "]" + " ")
                else:
                    sys.stdout.write(key + " ")
            sys.stdout.write("\n")
        sys.stdout.write("-" * 30 + "\n")
        sys.stdout.flush()

    def changeRow(self, shift):
        newRow = self.keyRow + shift

        if newRow < 0:
            self.keyRow = len(self.state) + newRow
        elif newRow >= len(self.state):
            self.keyRow = newRow - len(self.state)
        else:
            self.keyRow = newRow

    def changeColumn(self, shift):
        newColumn = self.keyColumn + shift

        if newColumn < 0:
            self.keyColumn = len(self.state[0]) + newColumn
        elif newColumn >= len(self.state[0]):
            self.keyColumn = newColumn - len(self.state[0])
        else:
            self.keyColumn = newColumn

    def up(self):
        self.changeRow(-1)
        self.printKeyboard()

    def down(self):
        self.changeRow(1)
        self.printKeyboard()

    def left(self):
        self.changeColumn(1)
        self.printKeyboard()

    def right(self):
        self.changeColumn(-1)
        self.printKeyboard()

    def enter(self):
        result = self.currentKey

        if result in specialMaps:
            result = specialMaps[result]

        print("high beam (enter) triggered, returning " + result)
        self.printKeyboard()
        return result