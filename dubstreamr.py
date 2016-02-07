#!/usr/bin/python3

import collections
import random
import math

Arrow = collections.namedtuple("Arrow", ['index', 'x', 'y'])

ARROWS = [
    Arrow(0, 0, 1),
    Arrow(1, 1, 2),
    Arrow(2, 1, 0),
    Arrow(3, 2, 1),
    Arrow(4, 3, 1),
    Arrow(5, 4, 2),
    Arrow(6, 4, 0),
    Arrow(7, 5, 1),
]

ROWS = [
    "|<      :       |",
    "|  v    :       |",
    "|    ^  :       |",
    "|      >:       |",
    "|       :<      |",
    "|       :  v    |",
    "|       :    ^  |",
    "|       :      >|",
]

def dist(a1, a2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

class Player:
    def __init__(self):
        # Player parameters
        #self.stride = stride

        # Chart
        self.chart = []

        # Starting position
        self.feet = [ARROWS[3], ARROWS[4]]
        self.weight = 0
        self.momentum = [0, 0]
        self.rotation = 0

    def randomstart(self):
        #self.weight = random.randrange(2)
        #foot1 = random.choice(ARROWS)
        #foot2 = random.choice(filter(lambda a: a.x != foot1.x, ARROWS))
        #if foot1.x < foot2.x:
        #    self.feet = [foot2, foot1]
        #else:
        #    self.feet = [foot1, foot2]
        self.weight = 1
        self.step(ARROWS[3])
        self.step(ARROWS[4])

    def isvalidstep(self, arrow):
        # Don't step on your other foot
        if arrow == self.feet[self.weight]:
            return False
        return True

    def step(self, arrow):
        # Shift weight, place foot, and remember the step
        self.weight ^= 1
        self.feet[self.weight] = arrow
        self.chart.append(arrow.index)

    def randomstep(self):
        # Figure out where we can step
        valid = list(filter(self.isvalidstep, ARROWS))
        self.step(random.choice(valid))

    def printchart(self):
        for n in self.chart:
            print(ROWS[n])

p = Player()
p.randomstart()
p.randomstep()
p.randomstep()
p.randomstep()
p.randomstep()
p.randomstep()
p.printchart()
