#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pygame

import pygame
import math
import sys
import json
import random
from pprint import pp
import os


# thank you chatgpt for the stub but its all gone now
# (I made it worse)

pygame.init()

screen_width = 700
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("nerd bee")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
LIGHT_GREY = (140, 140, 140)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

clock = pygame.time.Clock()

if "SPELLINGBEE_ETC" in os.environ:
    ETC_PREFIX = os.environ["SPELLINGBEE_ETC"]
else:
    ETC_PREFIX = ""

fontloc = ETC_PREFIX + "NotoSerif-Regular.ttf"
font = pygame.font.Font(fontloc, 80)
fontmedium = pygame.font.Font(fontloc, 40)
SMALL_FONT_SIZE = 19
fontsmall = pygame.font.Font(fontloc, SMALL_FONT_SIZE)

num_sides = 6
radius = 200
angle = (2 * math.pi / num_sides)
center_x, center_y = screen_width // 2, screen_height // 2 - 120



def make_gold_gradient():
    GOLD = [(185, 133, 13)]
    def f():
        color = GOLD[0]
        GOLD[0] = (min(int(color[0] * 1.20), 255), 
                min(int(color[1] * 1.20), 255),
                min(int(color[2] * 0.8), 255))
        return color

    return f


games = json.loads(open(ETC_PREFIX + "games.json").read())
alph = random.choice(list(games.keys()))

points = []
game = games[alph]

for i, c in enumerate(alph[1:]):
    x = center_x + int(radius * math.cos((1.5 * math.pi) - angle * i))
    y = center_y + int(radius * math.sin((1.5 * math.pi) - angle * i))
    points.append((c, (x, y)))

points.append((alph[0], (center_x, center_y)))



letters = list(alph.upper())
path = []
guess = []
running = True
guessed = set()

score = 0


mostrecent_real = ""
mostrecent = ""


def render_lines(w, left, top):
    for line in w.split("\n"):
        text = fontsmall.render(line, True, BLACK)
        text_rect = text.get_rect(left=left, top=top)
        screen.blit(text, text_rect)
        top += SMALL_FONT_SIZE

def breaklines(w):
    l = ""
    acc = ""
    i = 0
    ws = w.split(" ")
    while i < len(ws):
        candidate = l + " " + ws[i]
        if len(candidate) < 65:
            l = candidate
            i += 1
            continue
        acc += l + "\n"
        l = ""
    return acc + l


submitted = False

def clicked_word(event):
    global mostrecent, mostrecent_real, path, guess, score, submitted
    mx, my = pygame.mouse.get_pos()
    for c, point in points:
        px, py = point
        if math.sqrt((px - mx) ** 2 + (py - my) ** 2) <= 55:
            # clear everything once we start overwriting the submission
            if submitted:
                submitted = False
                path = []
                guess = []

            path.append((px, py))
            guess.append(c)

            sg = "".join(guess)

            if not (sg not in guessed and sg in game):
                continue

            # we got a word!
            submitted = True
            guessed.add(sg)

            mostrecent_real = game[sg][0]

            mostrecent = game[sg][1]
            mostrecent += "\n"
            if len(sg) == 4:
                score += 1
            else:
                if len(set(sg)) == 7:
                    score += 15
                score += len(sg)

            mostrecent += "\n\n".join(map(breaklines, game[sg][2]))

            return True

text = fontmedium.render("hint", True, BLACK)
HINT = text.get_rect(left=550, top=120)



print("Press escape to reset entry")
# Main loop
while running:
    if len(game) == len(guessed):
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if clicked_word(event):
                continue
            if HINT.collidepoint(event.pos):
                mostrecent_real = \
                        game[random.choice(list(set(game.keys()) - guessed))][0]
                continue
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not guess:
                    running = False
                guess = []
                path = []

    screen.fill(GREY)

    # draw connecting line
    GOLDf = make_gold_gradient()
    for i in range(1, len(path)):
        pygame.draw.line(screen, GOLDf(), path[i-1], path[i], 15)

    # draw circles on top of everything

    GOLDf = make_gold_gradient()
    for p in path:
        pygame.draw.circle(screen, GOLDf(), p, 55)

    for _, p in points:
        if p not in path:
            pygame.draw.circle(screen, LIGHT_GREY, p, 55)

    for c, point in points:
        text = font.render(c, True, BLACK)
        text_rect = text.get_rect(center=point)
        screen.blit(text, text_rect)

    # show current word
    text = font.render("".join(guess), True, BLACK)
    text_rect = text.get_rect(left=50, top=0)
    screen.blit(text, text_rect)

    text = font.render(str(score), True, BLACK)
    text_rect = text.get_rect(left=540, top=0)
    screen.blit(text, text_rect)


    text = fontmedium.render(mostrecent_real, True, BLACK)
    text_rect = text.get_rect(left=50, top=600)
    screen.blit(text, text_rect)

    render_lines(mostrecent, 50, 650)

    text = fontmedium.render('hint', True, BLACK)
    pygame.draw.rect(screen, LIGHT_GREY, HINT)
    screen.blit(text,HINT)
    pygame.display.flip()

    clock.tick(60)

# Quit Pygame
pygame.quit()

print("good game! your score:", score)
print("answers:")
pp(list(game.keys()), compact=True)
print("ur guesses:")
pp(list(guessed), compact=True)
