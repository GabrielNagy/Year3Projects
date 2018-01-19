from army import Army


class Player:
    def __init__(self, coins, army):
        self.coins = coins
        if type(army) is Army:
            army.make_leader()

    def has_enough_coins(self, cost):
        if self.coins - cost <= 0:
            return False
        return True

    def subtract_coins(self, cost):
        self.coins = self.coins - cost
        print("Subtracted " + str(cost) + " coins. Current coins: " + str(self.coins))
