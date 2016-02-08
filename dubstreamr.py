#!/usr/bin/python3

import sys
import collections
import random
import math

# Problems still to solve
#
# Advanced crossovers:
# |       :<      | L  -45     +90
# |       :  v    | R   45     +90
# |       :      >| L  135     +90
# |       :  v    | R  135      +0
# |       :    ^  | L   90     -45 <- not quite uncrossed
# |      >:       | R  153     +63 <- before starting a new crossover
# |       :    ^  | L  153      +0
# |      >:       | R  153      +0
# |       :    ^  | L  153      +0
# |      >:       | R  153      +0
# |       :    ^  | L  153      +0
# |       :  v    | R   90     -63
# |       :      >| L  135     +45
# |       :  v    | R  135      +0
# |       :    ^  | L   90     -45
# |       :      >| R   45     -45
#
# Thoughts: after crossing over, it is not enough just to bring it back to
# level (+/- pi) but must get abs below pi to feel natural.
#
# However, it is also natural to stay crossed over, or even get further
# crossed, when the other foot is repeating the same arrow.

Arrow = collections.namedtuple("Arrow", ['index', 'x', 'y'])
Rows = collections.namedtuple("Rows", ['none', 'measure', 'arrows'])

# Arrow data (id, location on pad)
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

# Rows for a semi-readable text chart
ROWS = Rows(
    "|       :       |",
    "| - - - : - - - |",
    [
        "|<      :       |",
        "|  v    :       |",
        "|    ^  :       |",
        "|      >:       |",
        "|       :<      |",
        "|       :  v    |",
        "|       :    ^  |",
        "|       :      >|",
    ]
)

# Rows for a SM file
SMROWS = Rows(
    "00000000",
    ",",
    [
        "10000000",
        "01000000",
        "00100000",
        "00010000",
        "00001000",
        "00000100",
        "00000010",
        "00000001",
    ]
)

def dist(a1, a2):
    return math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)

def angle(a1, a2, oldangle=0.0):
    r = math.atan2(a2.y - a1.y, a2.x - a1.x)
    # Minimize twisting if a previous angle is given
    return oldangle + math.fmod(r - oldangle, 2 * math.pi)

def isabove(x, y):
    return x > y and not math.isclose(x, y)

def isbelow(x, y):
    return x < y and not math.isclose(x, y)

class Player:
    def __init__(self):
        # Player parameters
        #self.stride = stride

        # Chart
        self.chart = []

        # Starting position
        self.feet = [ARROWS[3], ARROWS[4]]
        self.weight = 0
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
        # Set up proposed new position
        newfeet = self.feet.copy()
        newfeet[1 - self.weight] = arrow

        # Going nowhere is always an option
        if newfeet == self.feet:
            return True

        # Don't step on your other foot (no footswitches)
        if arrow == self.feet[self.weight]:
            return False
        # Don't move foot too quickly
        if dist(self.feet[1 - self.weight], arrow) > 2.6:
            return False
        # Don't stretch too far
        if dist(*newfeet) > 2.6:
            return False

        # Calculate angle for least twisting
        newangle = angle(*newfeet, self.rotation)

        # Don't turn backwards (never place feet more than 180 degrees rotated, and only allow
        # exactly 180 when the feet are next to each other, as in the middle of a staircase)
        if isabove(abs(newangle), math.pi) or (math.isclose(newangle, math.pi) and isabove(dist(*newfeet), 1)):
            return False
        # Don't force a quick twist
        if isabove(abs(newangle - self.rotation), math.pi):
            return False
        # If we are crossed over, we need to uncross
        if isabove(abs(self.rotation), math.pi / 2) and not isbelow(abs(newangle), abs(self.rotation)):
            return False
        return True

    def step(self, arrow):
        # Shift weight, place foot, and update angle
        self.weight ^= 1
        self.feet[self.weight] = arrow
        self.rotation = angle(*self.feet, self.rotation)

        # Save to chart
        self.chart.append((arrow.index, self.weight, self.rotation))

    def randomstep(self):
        # Figure out where we can step
        valid = list(filter(self.isvalidstep, ARROWS))
        self.step(random.choice(valid))

    def printchart(self, note, offset=0, rows=ROWS):
        i = 0
        # Offset in the first measure
        while i < offset:
            print(rows.none)
            i += 1
        # Print actual chart
        lr = 0
        for n, w, rot in self.chart:
            if i > 0 and i % note == 0:
                print(rows.measure)
            print("%s %s\t%4d\t%+4d" % (rows.arrows[n], "LR"[w], int(math.degrees(rot)), int(math.degrees(rot - lr))))
            lr = rot
            i += 1
        # Fill out remainder of last measure
        while i % note != 0:
            print(rows.none)
            i += 1

p = Player()
p.randomstart()
for n in range(int(sys.argv[2])):
    p.randomstep()
p.printchart(int(sys.argv[1]))
