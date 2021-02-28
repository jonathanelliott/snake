import time
import os
import sys
# import tty
# from random import randint, choice, random
import random
from itertools import product
import math

class Grid:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.grid = [ [ Cell(0) for _ in range(height) ] for _ in range(width) ]

  def __str__(self):
    return "\n".join(" ".join(map(str,row)) for row in self.grid)

  def __getitem__(self, index):
    x, y = index
    return self.grid[x][y]

  def __setitem__(self, index, value):
    x, y = index
    self.grid[x][y] = value

  def empty_cells(self):
    return [ (x,y) for x,y in product(range(self.width), range(self.height)) if self[x,y].value == 0 ]

  def cells(self):
    return [ cell for row in self.grid for cell in row ]

  def decrement_all(self):
    for cell in self.cells():
      cell.dec()
    
class Cell:
  def __init__(self, value):
    self.value = value
  
  def __str__(self):
    # Debugging representation
    return str(self.value % 10) if self.value > 0 else "*" if self.value < 0 else " "

  def draw(self, length):
    if self.value == length:
      # snake head
      return "O"
    elif self.value > 0:
      # snake body
      return "#"
    elif self.value < 0:
      # fruit
      return "*"
    else:
      # empty cell
      return " "

  def dec(self, d=1):
    if self.value >= d:
      self.value -= d

class Game:
  def __init__(self, width=25, height=25, direction=(0,1)):
    self.grid = Grid(width, height)

    self.length = 3
    self.head = width//2, height//2
    self.grid[self.head] = Cell(self.length)

    self.direction = direction
    self.active = True
    self.make_fruit(1)
    self.directions = [(0,1),(0,-1),(1,0),(-1,0)]
    self.all_directions = [(x,y) for x, y in product(range(-1,2),repeat=2)]
    # self.speed = None

  def __str__(self):
    # return str(self.grid)
    w = self.grid.width * 2 - 1
    return "+" + "-"*w + "+\n|" + \
      "|\n|".join(" ".join(cell.draw(self.length) for cell in row) for row in self.grid.grid) + \
      "|\n+" + "-"*w + "+"

  def reset(self):
    self.__init__(self.grid.width, self.grid.height)

  def rerun(self):
    self.reset()
    self.run()

  def make_fruit(self, weight):
    self.fruit_coords = random.choice(self.grid.empty_cells())
    self.grid[self.fruit_coords] = Cell(-weight)
    self.fruit = True

  def grow_snake(self):
    self.length += 1
    self.speed *= 0.99

  def add_direction(self, cell, d):
    x = (cell[0] + d[0]) % self.grid.width
    y = (cell[1] + d[1]) % self.grid.height
    return x, y

  def new_head(self, d):
    return self.add_direction(self.head, d)

  def valid_direction(self, d):
    # x, y = self.new_head(d)
    # next_cell = self.grid[x,y]
    return self.grid[self.new_head(d)].value <= 0
    # return next_cell.value <= 0 # and self.empty_neighbours((x,y))

  def empty_neighbours(self, cell):
    return [ d for d in self.directions if self.grid[self.add_direction(cell, d)].value <= 0 ]

  def neighbours_sum(self, cell):
    return sum(self.grid[self.add_direction(cell, d)].value for d in self.all_directions)

  def step(self, e=0):
    valid_directions = [ d for d in self.directions if self.valid_direction(d) ]
    if not valid_directions:
      print("Game Over!") # No possible direction!
      return False

    # dist = lambda p, q: math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2) # Euclidean metric
    dist = lambda p, q: abs(p[0] - q[0]) + abs(p[1] - q[1]) # L_1 "taxicab" metric
    def torus_dist(p,q):
      x, y = p
      w, h = self.grid.width, self.grid.height
      return min(dist(p,q), dist((x+w,y),q), dist((x,y+h),q), dist((x+w,y+h),q))
    dist_to_fruit = lambda d: torus_dist(self.new_head(d), self.fruit_coords)
    n_sum = lambda d: self.neighbours_sum(self.new_head(d))
    # utility = lambda p: self.length * dist_to_fruit(p) + self.neighbours_sum(self.new_head(p))
    # utility = lambda p: self.neighbours_sum(self.new_head(p))
    
    r = random.random()
    # Roughly speaking, e is a measure of how randomly the snake moves
    # If e = 0 the snake will always take the most direct route to the fruit
    if r < e / 4:
      d = random.choice(valid_directions)
    elif r < e and self.direction in valid_directions:
      d = self.direction
    else:
      # m = min(dist_to_fruit(d) for d in valid_directions)
      # print(m)
      # d = min([d for d in valid_directions if dist_to_fruit(d) == m], key=n_sum)
      # d = min(valid_directions, key=n_sum)
      d = min(valid_directions, key=dist_to_fruit)

    new_head = self.new_head(d)

    if self.grid[new_head].value < 0:
      self.grow_snake()
      self.fruit = False

    self.head = new_head
    self.direction = d
    self.grid.decrement_all()
    self.grid[self.head] = Cell(self.length)
    return True

  def run(self, e=0, g=0, speed=0.05):
    self.speed = speed
    i = 0
    os.system("clear")

    while True:
      # make fruit
      if not self.fruit:
        self.make_fruit(self.length)

      # grow snake in auto-grow mode
      if g > 0 and (i + 1) % g == 0:
        self.grow_snake()

      # print game
      print(self)
      print("Score: ", self.length)
      # print("Speed: ", self.speed)
      # print("Distance to fruit:")
      time.sleep(self.speed)
      if not self.step(e):
        break
      os.system("clear")
      i += 1

  def test(self, n=10):
    scores = []
    for _ in range(n):
      self.reset()
      self.run(speed=0)
      scores.append(self.length)
    print(scores)