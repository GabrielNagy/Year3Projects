class Army:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.joined = 0

    def get_total_power(self):
        total_power = 0
        for soldier in self.list():
            total_power += soldier.get_power()
        return total_power

    def add_member(self, soldier):
        self.members.append(soldier)

    def get_name(self):
        return self.name

    def has_leader(self):
        return self.joined

    def make_leader(self):
        if self.joined == 0:
            self.joined = 1
            print("Assigned a leader to army " + self.name)
        else:
            print("Army " + self.name + " already has a leader")

    def list(self):
        return self.members

    def fight(self, other_army):
        self_power = self.get_total_power()
        other_army_power = other_army.get_total_power()
        print(self.name + ' power is ' + str(self_power))
        print('' + other_army.name + ' power is ' + str(other_army_power))
        if self_power < other_army_power:
            print(self.name + ' has lost')
            return
        print(other_army.name + ' has lost')
