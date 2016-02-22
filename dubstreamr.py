#!/usr/bin/python3

import sys
import collections
import random
import math

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
        self.planted = False
        self.crossed = -1

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
        newfeet[self.weight ^ 1] = arrow

        # Going nowhere is always an option
        if newfeet == self.feet:
            return True

        # Don't step on your other foot (no footswitches)
        if arrow == self.feet[self.weight]:
            return False
        # Don't move foot too quickly
        if dist(self.feet[self.weight ^ 1], arrow) > 2.6:
            return False
        # Don't stretch too far
        if dist(*newfeet) > 2.6:
            return False

        # Calculate angle for least twisting
        newangle = angle(*newfeet, self.rotation)

        # Don't turn backwards (never place feet more than 180 degrees rotated,
        # and only allow exactly 180 when the feet are next to each other, as
        # in the middle of a staircase)
        if isabove(abs(newangle), math.pi) or (math.isclose(newangle, math.pi) and isabove(dist(*newfeet), 1)):
            return False
        # Don't force a quick twist
        if isabove(abs(newangle - self.rotation), math.pi):
            return False

        # If we have our feet crossed in the center, any moving foot must uncross
        if self.feet == [ARROWS[4], ARROWS[3]] and isabove(abs(newangle), math.pi / 2):
            return False

        # If we are crossed over, the anchor foot if moved needs to help us uncross
        if self.crossed == self.weight and not isbelow(abs(newangle), abs(self.rotation)):
            return False
        # The crossed foot may only cross further if the anchor has not moved
        if self.crossed == self.weight ^ 1 and not isbelow(abs(newangle), abs(self.rotation)) and not self.planted:
            return False

        # If we are crossed over, allow a step (1) if the uncrossed foot has remained planted, (2)
        return True

    def step(self, arrow):
        # Shift weight and place foot
        self.weight ^= 1
        if self.crossed != self.weight and self.feet[self.weight] != arrow:
            self.planted = False
        self.feet[self.weight] = arrow

        # Update rotation angle
        newrot = angle(*self.feet, self.rotation)
        if self.crossed < 0 and isabove(abs(newrot), math.pi / 2):
            self.crossed = self.weight
            self.planted = True
        elif isbelow(abs(newrot), math.pi / 2):
            self.crossed = -1
        self.rotation = newrot

        # Save to chart
        self.chart.append((arrow.index, self.weight, self.rotation, self.planted, self.crossed))

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
        for n, w, rot, p, x in self.chart:
            if i > 0 and i % note == 0:
                print(rows.measure)
            print("%s %s%s%s\t%4d\t%+4d" % (rows.arrows[n], "LR"[w], "P" if p else " ", "X" if x >= 0 else " ",
                int(math.degrees(rot)), int(math.degrees(rot - lr))))
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
