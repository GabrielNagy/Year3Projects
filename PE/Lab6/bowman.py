from soldier import Soldier


class Bowman(Soldier):
    def __init__(self, weapon):
        self.weapon = weapon
        super().__init__('Bowman', 110, 30, False, 30)

    def say_hurray(self):
        print('HURRAY')
