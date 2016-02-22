#!/usr/bin/python3

import sys
import collections
import random
import math

Arrow = collections.namedtuple("Arrow", ['index', 'x', 'y'])
Rows = collections.namedtuple("Rows", ['none', 'measure', 'arrows'])

# Parameters
# Eighths
#BEAT, MAXMOVE, MAXSTRETCH, MAXCROSS, ADVCROSS, MAXSTAND = 8, 2.6, 2.6, 1.5, False, 3
## Advanced eighths
#BEAT, MAXMOVE, MAXSTRETCH, ADVCROSS = 8, 2.6, 2.6, True
## Twelfths
#BEAT, MAXMOVE, MAXSTRETCH, ADVCROSS = 12, 2.1, 2.6, False
## Advanced twelfths
#BEAT, MAXMOVE, MAXSTRETCH, ADVCROSS = 12, 2.1, 2.6, True
## Sixteenths, no candles
#BEAT, MAXMOVE, MAXSTRETCH, ADVCROSS = 16, 1.9, 2.6, False
## Sixteenths, candles allowed
#BEAT, MAXMOVE, MAXSTRETCH, ADVCROSS = 16, 2.1, 2.6, False

MEASURES = int(sys.argv[1])
BEAT = int(sys.argv[2])
MAXMOVE = float(sys.argv[3])
MAXSTRETCH = float(sys.argv[4])
MAXCROSS = float(sys.argv[5])
ADVCROSS = bool(int(sys.argv[6]))
MAXSTAND = int(sys.argv[7])


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
        self.stand = 0

    def randomstart(self):
        foot1 = random.choice(ARROWS)
        foot2 = random.choice(list(filter(
            lambda a: a.x != foot1.x and
                not isabove(dist(a, foot1), MAXSTRETCH),
            ARROWS)))
        if foot1.x < foot2.x:
            self.weight = 1
        else:
            self.weight = 0
        self.step(foot1)
        self.step(foot2)
        #self.weight = 1
        #self.step(ARROWS[0])
        #self.step(ARROWS[1])

    def isvalidstep(self, arrow):
        # Set up proposed new position
        newfeet = self.feet.copy()
        newfeet[self.weight ^ 1] = arrow

        # Going nowhere is an option if not for too long
        if newfeet == self.feet:
            return self.stand < MAXSTAND

        # Don't step on your other foot (no footswitches)
        if arrow == self.feet[self.weight]:
            return False
        # Don't move foot too quickly
        if isabove(dist(self.feet[self.weight ^ 1], arrow), MAXMOVE):
            return False
        # Don't stretch too far
        if isabove(dist(*newfeet), MAXSTRETCH):
            return False

        # Calculate angle for least twisting
        newangle = angle(*newfeet, self.rotation)

        # Don't turn past 180 degrees, and if we are crossed over (past 90) be
        # sure feet are a bit closer together
        if isabove(abs(newangle), math.pi) or (isabove(abs(newangle), math.pi / 2) and isabove(dist(*newfeet), MAXCROSS)):
            return False
        # Don't force a quick twist
        if isabove(abs(newangle - self.rotation), math.pi):
            return False

        # If we have our feet crossed in the center, any moving foot must uncross
        if self.feet == [ARROWS[4], ARROWS[3]] and isabove(abs(newangle), math.pi / 2):
            return False

        # For advanced crossovers, leave out the following rules
        if ADVCROSS:
            return True

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
        if self.feet[self.weight] == arrow:
            self.stand += 1
        else:
            self.stand = 0
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
        self.chart.append((arrow.index, self.weight, self.rotation, self.planted, self.crossed, self.stand))

    def randomstep(self):
        # Figure out where we can step
        valid = list(filter(self.isvalidstep, ARROWS))
        if valid:
            self.step(random.choice(valid))
        else:
            self.step(self.feet[self.weight ^ 1])

    def printchart(self, note, offset=0, rows=ROWS):
        i = 0
        # Offset in the first measure
        while i < offset:
            print(rows.none)
            i += 1
        # Print actual chart
        #lr = 0
        for n, w, rot, p, x, stand in self.chart:
            if i > 0 and i % note == 0:
                print(rows.measure)
            print(rows.arrows[n])
            #print("%s %s%s%s\t%4d\t%+4d\t%s" % (rows.arrows[n], "LR"[w], "P" if p else " ", "X" if x >= 0 else " ",
            #    int(math.degrees(rot)), int(math.degrees(rot - lr)), str(stand) if stand else ""))
            #lr = rot
            i += 1
        # Fill out remainder of last measure
        while i % note != 0:
            print(rows.none)
            i += 1

p = Player()
p.randomstart()
# Calculate number of steps, minus two automatic ones from randomstart
for n in range(MEASURES * BEAT - 2):
    p.randomstep()
p.printchart(BEAT, rows=SMROWS)
