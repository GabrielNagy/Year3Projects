from army import Army
from player import Player


class Soldier:
    def __init__(self, grade, attack, defense, armored, cost):
        self.grade = grade
        self.attack = attack
        self.defense = defense
        self.armored = armored
        self.cost = cost
        self.joined = 0
        print("Created a " + self.grade + ".")

    def acknowledge(self):
        print(self.grade + ': I was informed by the Scouter')

    def get_power(self):
        return self.attack

    def join(self, player, army):
        if type(army) is Army and self.joined == 0:
            if type(player) is Player and player.has_enough_coins(self.cost):
                army.add_member(self)
                player.subtract_coins(self.cost)
                self.joined = 1
                print("Soldier " + self.grade + " has joined army " + army.get_name())
            else:
                print("The player does not have enough coins.")
        else:
            print("Soldier " + self.grade + " already has an army")
