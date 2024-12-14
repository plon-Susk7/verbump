import numpy as np 

class Calculator:

    def __init__(a,b):
        self.a = a
        self.b = b
    
    def add(self)->int:
        return self.a + self.b

    def subtract(self)->int:
        return self.a - self.b

    def multiply(self)->int:
        return self.a * self.b

    def divide(self)->float:
        return self.a / self.b

    def power(self)->int:
        return self.a ** self.b

    def __str__(self):
        return str(self.power())

#More chnages to be mad lil bit 