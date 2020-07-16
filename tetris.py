import pygame
import random
import sys
from pathlib import Path
from collections import namedtuple
import os
from collections import deque
import time
import pickle

CUBE_WIDTH = 50
FIELD_WIDTH = 12
FIELD_HEIGHT = 19
SCREEN_WIDTH = 16 * CUBE_WIDTH
SCREEN_HEIGHT = FIELD_HEIGHT * CUBE_WIDTH
FIELD_BORDER_WIDTH = 1

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
DARK_GREY = (64, 64, 64)
YELLOW = (255, 255, 0)
PURPLE = (148,0,211)

BG_COLOUR = BLACK


def draw_cube(screen, colour, x, y, width=CUBE_WIDTH):
    pygame.draw.rect(screen, colour, pygame.Rect(x, y, width, width))


def draw_rec(screen,  x, y, pic):
    screen.blit(pic, (x,y))


# classes
class Button:

    def __init__(self, x, y, width=100, height=100, pic = None, func = None):
        self.func = func
        self.rect = pygame.Rect(x, y, width, height)
        self.pic = pic
        self.click = False
        self.tick = 0

    def func(self):
        if self.func != None:
            self.func()


class PauseButton(Button):

    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self):
        pass

    def draw(self):
        global paused
        if paused:
            # pygame.draw.rect(screen, GREEN, self.rect)
            # draw_rec(screen, self.rect.x, self.rect.y, pic=pressed_button)
            self.pic = pressed_button
        else:
            # pygame.draw.rect(screen, YELLOW, self.rect) # not paused
            # draw_rec(screen, self.rect.x, self.rect.y, pic=unpressed_button)
            self.pic = unpressed_button

        draw_rec(screen, self.rect.x, self.rect.y, self.pic)

    def pause_game(self):
        global paused
        paused = not paused


class ResetButton(Button):

    global unpressed_button
    global pressed_button

    def update(self):
        if self.click:
            self.tick += 1
            if self.tick > FRAME_RATE/10:
                self.click = False
                self.tick = 0

    def draw(self):
        if self.pic == None:
            self.pic = unpressed_button
            # pygame.draw.rect(screen, RED, self.rect)
        draw_rec(screen, self.rect.x, self.rect.y, self.pic)

    def reset_game(self):
        field.__init__()
        tetro.__init__()
        next_tetro.__init__()
        global score
        global paused
        save_score()
        score = 0
        global game_over
        game_over = False
        if not paused:
            paused = not paused

    def click_animate(self):
        self.pic = pressed_button
        self.draw()
        pygame.display.flip()

        time.sleep(0.1)

        self.pic = unpressed_button
        self.draw()
        pygame.display.flip()


class Cube:
    def __init__(self, pos, type):
        self.pos = pos
        self.type = type


class Field:
    # basically just a list
    def __init__(self):
        self.array = [None] * FIELD_WIDTH * FIELD_HEIGHT
        self.dissapears = []
        # make border
        for x in range(FIELD_WIDTH):
            for y in range(FIELD_HEIGHT):
                if x == FIELD_WIDTH - FIELD_BORDER_WIDTH or y == FIELD_HEIGHT - FIELD_BORDER_WIDTH or x == 0:
                    self.array[y * FIELD_WIDTH + x] = "border"

    def draw(self):

        for x in range(FIELD_WIDTH):
            for y in range(FIELD_HEIGHT):
                # if x == FIELD_WIDTH-FIELD_BORDER_WIDTH or y==FIELD_HEIGHT-FIELD_BORDER_WIDTH or x == 0:
                if self.array[y * FIELD_WIDTH + x] == 'border':
                    # draw_cube(screen, BLUE, (x) * CUBE_WIDTH, y * CUBE_WIDTH)
                    draw_rec(screen, x*CUBE_WIDTH,y*CUBE_WIDTH, pic=blocks["grey"])
                elif self.array[y * FIELD_WIDTH + x] == None:
                    draw_cube(screen, BLACK, (x) * CUBE_WIDTH, y * CUBE_WIDTH)
                else:
                    # draw_cube(screen, pygame.Color(self.array[y * FIELD_WIDTH + x]), x * CUBE_WIDTH, y * CUBE_WIDTH)
                    draw_rec(screen, x * CUBE_WIDTH, y * CUBE_WIDTH, pic=blocks[self.array[y*FIELD_WIDTH+x]])
        # do line animation:
        self.line_dissapearing()

    def is_empty(self, x, y):
        return self.array[y * FIELD_WIDTH + x] == None

    def update(self):
        for y in range(FIELD_HEIGHT):
            count = 0
            for x in range(FIELD_WIDTH):
                cur_cube = self.array[y * FIELD_WIDTH + x]
                if cur_cube != None and cur_cube != "border":
                    count += 1
                    if count >= FIELD_WIDTH - 2:  # for borders:
                        # animation:
                        self.dissapears.append(y)
                        # self.shift(y)

    def shift(self, ly):
        for x in range(FIELD_WIDTH):
            for y in range(ly, 0, -1):
                self.array[y * FIELD_WIDTH + x] = self.array[(y - 1) * FIELD_WIDTH + x]

    # this method both draws and updates
    def line_dissapearing(self):
        if self.dissapears == []:
            return
        else:
            #sounds:
            dissapear_sound.play()
            # animation, flip the board first
            pygame.display.flip()
            x1 = FIELD_WIDTH // 2 - 1
            x2 = FIELD_WIDTH // 2

            # some clever animation, start from the middle
            for i in range(
                    FIELD_WIDTH // 2 - 1):  # moving from x1, x2 to the end of their side: " 0 <- x1, x2 -> WIDTH "
                for y in self.dissapears:
                    draw_cube(screen, pygame.Color("black"), (x2 + i) * CUBE_WIDTH, y * CUBE_WIDTH)
                    draw_cube(screen, pygame.Color("black"), (x1 - i) * CUBE_WIDTH, y * CUBE_WIDTH)

                pygame.display.flip()
                time.sleep(0.08)

            # deleting - updating the board
            for i in self.dissapears:
                self.shift(i)
            global score
            score += len(self.dissapears)
            self.dissapears = []


class Tetromino:
    MAX_WIDTH = 4
    GAP = 5
    MAX_HEIGHT = 4
    # 4 numbers are the cords in an array of 16 elements
    Tetro = namedtuple('Tetro', 'shape, colour, name')
    I = Tetro((4, 5, 6, 7), colour= "cyan", name="T")
    O = Tetro((5, 6, 9, 10), colour="yellow", name="O")
    T = Tetro((6, 9, 10, 11), colour="purple", name="T")
    S = Tetro((9, 10, 6, 7), colour="green", name="S")
    Z = Tetro((5, 6, 10, 11), colour="red", name="Z")
    J = Tetro((5, 9, 10, 11), colour="blue", name="J")
    L = Tetro((7, 9, 10, 11), colour="orange", name="L")
    tetros = [I, O, T, S, Z, J, L]

    # tetros = [I, O]

    def __init__(self, fx=FIELD_WIDTH // 2 - 2, fy=-1):
        self.fx = fx
        self.fy = fy
        self.movable = False
        self.down_held = False
        self.time = time.time()
        self.tetro = random.choice(self.tetros)
        self.colour = self.tetro.colour
        self.rotation_circle = deque([0, 90, 180, 270])
        self.array = [1 if x in self.tetro.shape else 0 for x in range(self.MAX_WIDTH * self.MAX_HEIGHT)]
        self.original_array = self.array
        self.falling_speed = 1
        self.tick_alterable = True
        self.width = 0
        for px in range(self.MAX_WIDTH):
            for py in range(self.MAX_HEIGHT):
                if self.array[py*self.MAX_WIDTH + px] == 1:
                    if px > self.width:
                        self.width = px


    def update(self):
        global key_up_held
        global ticks
        newx = self.fx
        newy = self.fy
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if not key_up_held:
                rotate_sound.play()
                self.rotate()
            key_up_held = True
        if not keys[pygame.K_UP]:
            key_up_held = False

        if not self.movable:
            if (time.time() - self.time) >= 0.5:
                self.movable = True
            else:
                return

        if keys[pygame.K_RIGHT]:
            newx += 1
        if keys[pygame.K_LEFT]:
            newx += -1
        if keys[pygame.K_DOWN]:
            newy += 1
            self.falling_speed = 0
            self.down_held = True

        if not keys[pygame.K_DOWN]:
            self.falling_speed = 1
            self.down_held = False

        if self.check_valid(self.array, newx, self.fy):
            self.fx = newx

        if self.check_valid(self.array, self.fx, newy):
            self.fy = newy
        else:
            if self.tick_alterable:
                ticks = FRAME_RATE//2
            self.tick_alterable = False

    def draw(self):
        for px in range(self.MAX_WIDTH):
            for py in range(self.MAX_HEIGHT):
                if self.array[py * self.MAX_WIDTH + px] == 1:
                    # draw_cube(screen, colour=pygame.Color(self.colour), x=(self.fx + px) * CUBE_WIDTH,
                    #           y=(self.fy + py) * CUBE_WIDTH,
                    #           width=CUBE_WIDTH - self.GAP)
                    draw_rec(screen, x=(self.fx+px)*CUBE_WIDTH, y=(self.fy+py)*CUBE_WIDTH, pic=blocks[self.colour])

    def draw_outside(self, x, y):

        if self.tetro != self.I and self.tetro != self.O:
            x = x - CUBE_WIDTH // 4
        for px in range(self.MAX_WIDTH):
            for py in range(self.MAX_HEIGHT):
                if self.array[py * self.MAX_WIDTH + px] == 1:
                    # draw_cube(screen, colour=pygame.Color(self.colour), x=x+(px*CUBE_WIDTH//2),
                    #           y=y+py*(CUBE_WIDTH//2),
                    #           width=CUBE_WIDTH//2 - self.GAP)

                    draw_rec(screen, x=x+(px*CUBE_WIDTH//2), y=y+(py*CUBE_WIDTH//2),
                             pic=pygame.transform.scale(blocks[self.colour],(CUBE_WIDTH//2, CUBE_WIDTH//2)))


    def rotate(self):

        self.rotation_circle.rotate(-1)
        new_shape_array = [0] * self.MAX_WIDTH * self.MAX_HEIGHT
        for px in range(self.MAX_WIDTH):
            for py in range(self.MAX_HEIGHT):
                if self.original_array[py * self.MAX_WIDTH + px] == 1:
                    if self.rotation_circle[0] == 0:
                        new_shape_array = self.original_array
                        break
                    elif self.rotation_circle[0] == 90:
                        new_shape_array[12 + py + px * (-self.MAX_WIDTH)] = 1
                    elif self.rotation_circle[0] == 180:
                        new_shape_array[15 - (py * self.MAX_WIDTH) - px] = 1
                    elif self.rotation_circle[0] == 270:
                        new_shape_array[3 - py + (px * self.MAX_WIDTH)] = 1
        if self.check_valid(new_shape_array, self.fx, self.fy):
            self.array = new_shape_array
        else:
            offset = [-2, -1, 1, 2]
            for i in offset:
                if self.check_valid(new_shape_array, self.fx + i, self.fy):
                    self.fx += i
                    self.array = new_shape_array
                    # print(self.rotation_circle[0])
                    return
            if self.fy == -1:
                for i in [1,2]:
                    if self.check_valid(new_shape_array, self.fx, self.fy + i):
                        self.fy += i
                        self.array = new_shape_array
                        return

            # if not possbile:
            self.rotation_circle.rotate(1)


    def check_valid(self, array, fx, fy):
        for px in range(self.MAX_WIDTH):
            for py in range(self.MAX_HEIGHT):
                if array[py * self.MAX_WIDTH + px] == 1:
                    x = fx + px
                    y = fy + py
                    if not field.is_empty(x, y):
                        return False
                    # if x <= 0 or x >= FIELD_WIDTH - FIELD_BORDER_WIDTH or y >= FIELD_HEIGHT - FIELD_BORDER_WIDTH:
                    #     return False

        return True

    def fallable(self):
        newfy = self.fy + 1
        if self.check_valid(self.array, self.fx, newfy):
            return True
        return False


def lock(board, tetro):
    x = tetro.fx
    y = tetro.fy
    for tx in range(tetro.MAX_WIDTH):
        for ty in range(tetro.MAX_HEIGHT):
            if tetro.array[ty * tetro.MAX_WIDTH + tx] == 1:
                board.array[(y + ty) * FIELD_WIDTH + (x + tx)] = tetro.colour


def lock_and_respawn():
    global paused
    global tetro

def display_text(surface, x, y, text,
                 font,
                 colour=pygame.Color("white"), bg=None ):
    text_w, text_h = font.size(text)
    text_sur = font.render(text, False, colour,bg)
    surface.blit(text_sur,(x-text_w//2, y-text_h//2))

def save_score():
    global score
    global best_score
    if score > best_score:
        best_score = score
    with open("best_score.pickle", "wb") as score_data:
        pickle.dump(best_score, score_data)

# Initialise game and create window:
os.environ['SDL_VIDEO_WINDOW_POS'] = '{},{}'.format(600, 0)
pygame.mixer.pre_init(frequency=32000, buffer=12, channels=1)
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BG_COLOUR)
pygame.display.flip()
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

font_name = 'ubuntumono'

# assets and game states:
current_folder = Path().resolve()
font_f = current_folder / 'font'
image_f = current_folder / 'images'
sound_f = current_folder / 'sounds' / 'General Sounds'

unpressed_button = pygame.image.load(str(image_f / 'unpressed_button.png')).convert_alpha()
pressed_button = pygame.image.load(str(image_f / 'pressed_button.png')).convert_alpha()
unpressed_button = pygame.transform.scale(unpressed_button, (100, 100))
pressed_button = pygame.transform.scale(pressed_button, ( 100, 100 ))

    # blocks:
blue_block = pygame.image.load(str(image_f / 'BlueBlockFX.png')).convert()
blue_block = pygame.transform.scale(blue_block, (CUBE_WIDTH, CUBE_WIDTH))
orange_block = pygame.image.load(str(image_f / 'OrangeBlockFX.png')).convert()
orange_block = pygame.transform.scale(orange_block, (CUBE_WIDTH, CUBE_WIDTH))
icy_block = pygame.image.load(str(image_f / 'IcyBlueBlockFX.png')).convert()
icy_block = pygame.transform.scale(icy_block, (CUBE_WIDTH, CUBE_WIDTH))
green_block = pygame.image.load(str(image_f / 'GreenBlockFX.png')).convert()
green_block = pygame.transform.scale(green_block, (CUBE_WIDTH, CUBE_WIDTH))
red_block = pygame.image.load(str(image_f / 'RedBlockFX.png')).convert()
red_block = pygame.transform.scale(red_block, (CUBE_WIDTH, CUBE_WIDTH))
yellow_block = pygame.image.load(str(image_f / 'YellowBlockFX.png')).convert()
yellow_block = pygame.transform.scale(yellow_block, (CUBE_WIDTH, CUBE_WIDTH))
grey_block = pygame.image.load(str(image_f / 'GrayBlockFX.png')).convert()
grey_block = pygame.transform.scale(grey_block, (CUBE_WIDTH, CUBE_WIDTH))
purple_block = pygame.image.load(str(image_f / 'PurpleBlockFX.png')).convert()
purple_block = pygame.transform.scale(purple_block, (CUBE_WIDTH, CUBE_WIDTH))


blocks = {"blue": blue_block, "cyan": icy_block, "red": red_block, "yellow": yellow_block, "grey": grey_block, "green": green_block
          ,"purple": purple_block, "orange": orange_block
          }

# sounds:
dissapear_sound = pygame.mixer.Sound(str(sound_f / "se_game_match.wav"))
dissapear_sound.set_volume(0.4)

rotate_sound = pygame.mixer.Sound(str(sound_f / "se_game_rotate.wav"))
rotate_sound.set_volume(0.4)

landing_sound = pygame.mixer.Sound(str(sound_f / "se_game_landing.wav"))
landing_sound.set_volume(0.4)

hard_drop = pygame.mixer.Sound(str(sound_f / "se_game_harddrop.wav"))
hard_drop.set_volume(0.4)

soft_drop = pygame.mixer.Sound(str(sound_f / "se_game_softdrop.wav"))
soft_drop.set_volume(0.4)

move_sound = pygame.mixer.Sound(str(sound_f / "se_game_move.wav"))
move_sound.set_volume(0.4)

pause_button = PauseButton(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 400)
reset_button = ResetButton(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 200)
field = Field()
tetro = Tetromino()
next_tetro = Tetromino()
key_up_held = False
ticks = 0
paused = False
score = 0
best_score = 0
game_over = False

if Path("./best_score.pickle").resolve().exists():
    with open("best_score.pickle", "rb") as score_data:
         best_score = pickle.load(score_data)

# Main Game loop
dropping = soft_drop
running = True
while running:

    # GAME TIMING --------------
    clock.tick(FRAME_RATE)
    ticks += 1

    # INPUT AND UPDATE ----------

    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            # bind K to pause
            if e.key == pygame.K_p:
                paused = not paused
            # bind R to reset game:
            elif e.key == pygame.K_r:
                reset_button.click_animate()
                reset_button.reset_game()

        # check mouse clicks
        if e.type == pygame.MOUSEBUTTONDOWN:
            if pause_button.rect.collidepoint(e.pos):
                pause_button.pause_game()

            elif reset_button.rect.collidepoint(e.pos):
                reset_button.click_animate()
                reset_button.reset_game()

        # update game objects (includes some input and game logic)
    if not paused:
        tetro.update()
        pause_button.update()
        reset_button.update()

        if ticks >= FRAME_RATE:
            ticks = 0
            if tetro.fallable():
                tetro.fy += tetro.falling_speed
            else:
                dropping.play()
                lock(field, tetro)
                field.update()
                tetro = next_tetro
                next_tetro = Tetromino()
                if not tetro.check_valid(tetro.array, tetro.fx, tetro.fy):
                    game_over = True
                    paused = True


    # DRAW AND RENDER -----------
    screen.fill(DARK_GREY)
    pause_button.draw()
    reset_button.draw()


        # draw the score:
    display_text(screen, SCREEN_WIDTH-100, 50, "SCORE:", font=pygame.font.Font("font/Helvetica-Bold.ttf", 25), colour=WHITE, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, 100, str(score), font=pygame.font.Font("font/helvetica-rounded-bold.otf", 40), colour=RED, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, 150, "HIGH SCORE:", font=pygame.font.Font("font/Helvetica-Bold.ttf", 25), colour=WHITE, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, 200, str(best_score), font=pygame.font.Font("font/helvetica-rounded-bold.otf", 40), colour=RED, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, SCREEN_HEIGHT- 230, "RESET GAME:", font=pygame.font.Font("font/Helvetica-Bold.ttf", 20), colour=WHITE, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, SCREEN_HEIGHT- 430, "PAUSE GAME:", font=pygame.font.Font("font/Helvetica-Bold.ttf", 20), colour=WHITE, bg=DARK_GREY)
    display_text(screen, SCREEN_WIDTH-100, 280, "NEXT:", font=pygame.font.Font("font/Helvetica-Bold.ttf", 25), colour=PURPLE, bg=DARK_GREY)

    if game_over:
        display_text(screen, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 500, "GAME OVER!!!",
                     font=pygame.font.Font("font/Helvetica-Bold.ttf", 25), colour=RED, bg=DARK_GREY)

        # draw the field and tetromin
    field.draw()
    tetro.draw()
    next_tetro.draw_outside(SCREEN_WIDTH-150, 320)
    # flip when done with drawing/updating
    pygame.display.flip()

pygame.quit()

save_score()





