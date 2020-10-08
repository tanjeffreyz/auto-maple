import csv

from os import listdir
from os.path import isfile, join

sequence = []

class Point:
    def __init__(self, x, y, frequency=1, attack=True, n=1, extras=[]):
        self.location = (x, y)
        self.frequency = frequency
        self.counter = 0
        self.attack = attack
        self.n = n
        self.extras = extras

    def execute(self):
        if self.counter == 0:
            move(self.location)
            for e in self.extras:
                exec(f'commands.{e}()')
            if self.attack:
                commands.shikigami('left', self.n)
                commands.shikigami('right', self.n)
        self.counter = (self.counter + 1) % self.frequency

frequency, attack, n, extras = 1, True, 1, []

def load():
    global sequence, frequency, attack, n, extras
    sequence = []

    path = './bots'
    csv_files = [f for f in listdir(path) if isfile(join(path, f)) and '.csv' in f]
    if not csv_files:
        print('Unable to find .csv bot file.')
    else:
        with open(join(path, csv_files[0])) as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                assert len(row) > 1, 'A Point must at least have an x and y position'
                frequency, attack, n, extras = 1, True, 1, []
                for a in row[2:]:
                    exec('global frequency, attack, n, extras; ' + str(a))        # If you don't use global, the variables are assigned LOCALLY INSIDE exec's frame!!!
                print(frequency, attack, n, extras)
                sequence.append(Point(float(row[0]), float(row[1]), frequency, attack, n, extras))
            

# extras=[]
# string = "extras=['fox']"
# exec(string)
# print(extras)
# print([exec(a) for a in row[2:]])
load()

# print(csv_files)