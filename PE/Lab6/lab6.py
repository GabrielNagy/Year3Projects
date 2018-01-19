from army import Army
from player import Player
from bowman import Bowman
from scouter import Scouter
from swordsman import Swordsman


if __name__ == "__main__":
    army_1 = Army("Red Army")
    player_1 = Player(100, army_1)
    army_2 = Army("Black Army")
    player_2 = Player(100, army_2)

    scouter_1 = Scouter("Spear")
    scouter_1.join(player_2, army_2)
    scouter_1.say_hurray()

    swordsman_1 = Swordsman("Short sword")
    swordsman_1.join(player_1, army_1)
    swordsman_1.say_hurray()

    bowman_1 = Bowman("Long bow")
    bowman_1.join(player_2, army_2)
    bowman_1.say_hurray()

    swordsman_2 = Swordsman("Short sword")
    swordsman_2.join(player_1, army_1)
    swordsman_2.say_hurray()

    scouter_1.inform_army(army_2)

    print(army_1.list())
    print(army_2.list())

    army_1.fight(army_2)

    print(army_1.list())
    print(army_2.list())
