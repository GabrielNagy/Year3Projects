from random import randint


class Dice:
    faces = {1: 'one.txt', 2: 'two.txt', 3: 'three.txt', 4: 'four.txt', 5: 'five.txt', 6: 'six.txt'}

    def print_dice(self):
        print(self.face)

    def assign_face(self, value):
        with open("dice/%s" % Dice.faces[value]) as face:
            self.face = face.read()
        self.print_dice()

    def roll_dice(self):
        value = randint(1, 6)
        self.assign_face(value)


if __name__ == "__main__":
    Dice_one = Dice()
    Dice_two = Dice()

    Dice_one.roll_dice()
    Dice_two.roll_dice()
