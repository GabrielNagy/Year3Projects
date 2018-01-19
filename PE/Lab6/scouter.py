from soldier import Soldier
from army import Army


class Scouter(Soldier):
    def __init__(self, weapon):
        self.weapon = weapon
        super().__init__('Scouter', 50, 20, False, 15)

    def inform_army(self, army):
        if type(army) is Army:
            for soldier in army.list():
                soldier.acknowledge()

    def say_hurray(self):
        print('HURRAY')
