
class Power:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def power(self):
        return self.a ** self.b

    def __str__(self):
        return str(self.power())

    def __repr__(self):
        return str(self.power())

# Slight changes!