import pygame
import random
import sys
import pathlib
import itertools as ite
from collections import namedtuple
import os

WIDTH = 700
HEIGHT = 50*18
TITLE = "tetris"
FRAME_RATE = 10

# Define colours:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BEIGE = (250, 175, 0)
AQUA = (128, 206, 207)
DARK_GREY = (64,64,64)

BG_COLOUR = BLACK

# Setting game assets:

# classes
class Board:
    # height and width are measured in cubes
    HEIGHT = 18
    WIDTH = 10
    CUBE_WIDTH = 50
    BORDER_WIDTH = 5
    BORDER_COLOUR = AQUA
    ACTUAL_WIDTH = WIDTH*CUBE_WIDTH
    def __init__(self, screen, colour):
        self.screen = screen
        self.colour = colour
        Cube = namedtuple("Cube", "x,y,tetro")
        self.cubes = list(map(Cube._make, self.make_cubes()))
        print(self.cubes)

    def draw(self):
        for cube in self.cubes:
            curLine = cube.x // self.CUBE_WIDTH # current line is an ordinal number, start at 0
            if not isinstance(cube.tetro, Tetromino):
                pygame.draw.rect(self.screen, self.colour, pygame.Rect(cube[0], cube[1], self.CUBE_WIDTH, self.CUBE_WIDTH) )
            else:
                # draw cube with the colour of the tetrp's cube at that position:
                pass

            # draw right border
            if curLine == self.WIDTH-1:
                pygame.draw.rect(self.screen, self.BORDER_COLOUR, pygame.Rect(cube[0]+self.CUBE_WIDTH, cube[1],self.BORDER_WIDTH, self.CUBE_WIDTH))

    def make_cubes(self):
        return [(a,b,0) for a in [x*self.CUBE_WIDTH for x in range(self.WIDTH)] for b in [y*self.CUBE_WIDTH for y in range(self.HEIGHT)]]



class Tetromino:
    MAX_WIDTH = 4
    GAP = 5
    MAX_HEIGHT = 4
    # 4 numbers are the cords in an array of 15 elements
    I = 0,1,2,3

    O = 0,1,4,5
    T = 1,4,5,6
    S = 1,2,4,5
    Z = 0,1,5,6
    J = 0,4,5,6
    L = 2,4,5,6
    shapes = [I, O, T, S, Z, J, L]
    def __init__(self,x,y, colour):
        self.x = x
        self.y = y
        self.colour = colour
        self.shape = self.L
        self.array = [0]*self.MAX_WIDTH*self.MAX_HEIGHT
        # creating shape of tetro using arrays:
        max_width = 1 #
        max_height = 1 # in cubes
        for i in range(len(self.array)):
            current_width = i - (i//4)*4 # find maximum width at i, starts at 0
            current_height = i//4
            if i in self.shape:
                self.array[i] = 1
                ## try to find max_width (in cubes) so we can calcute width of tetro
                if current_width > max_width:
                    max_width = current_width
                if current_height > max_height:
                    max_height = current_height


        self.height = Board.CUBE_WIDTH*(max_height+1)
        self.width = Board.CUBE_WIDTH*(max_width+1)

        print("tetro's heigth", max_height)
        print(self.array)

    def update(self):
        keys = pygame.key.get_pressed()
        curx = self.x
        cury = self.y
        if keys[pygame.K_DOWN]:
            cury += board.CUBE_WIDTH
        if keys[pygame.K_LEFT]:
            curx -= board.CUBE_WIDTH
        if keys[pygame.K_RIGHT]:
            curx += board.CUBE_WIDTH
        if keys[pygame.K_UP]:
            cury -= board.CUBE_WIDTH

        if curx >= 0 and curx <= board.CUBE_WIDTH*board.WIDTH-self.width:
            self.x = curx

        if cury+self.height <= board.CUBE_WIDTH*board.HEIGHT:
            self.y = cury

    def draw(self):
        currentx = self.x
        currenty = self.y
        counter = 0
        for i in self.array:
            if counter > self.MAX_WIDTH-1:
                counter = 0
                currentx = self.x
                currenty += Board.CUBE_WIDTH


            if i == 1:
                pygame.draw.rect(screen, self.colour, pygame.Rect(currentx, currenty, Board.CUBE_WIDTH-self.GAP, Board.CUBE_WIDTH-self.GAP))

            currentx += Board.CUBE_WIDTH
            counter += 1



# Initialise game and create window:
os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(600,0)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(BLACK)
pygame.display.flip()
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

running = True

# Game Objects
board = Board(screen, DARK_GREY)
cur_tetro = Tetromino(board.CUBE_WIDTH*(board.WIDTH//2-1),0,WHITE)
all_sprites = pygame.sprite.Group()


# Main Game loop
while running:
    clock.tick(FRAME_RATE)
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False

    # Update
    cur_tetro.update()

    # Draw & render
    screen.fill(BG_COLOUR)
    board.draw()
    cur_tetro.draw()

    # flip when done with drawing/updating
    pygame.display.flip()

pygame.quit()


