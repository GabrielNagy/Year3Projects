from soldier import Soldier


class Swordsman(Soldier):
    def __init__(self, weapon):
        self.weapon = weapon
        super().__init__('Swordsman', 100, 50, True, 20)

    def say_hurray(self):
        print('HURRAY')
