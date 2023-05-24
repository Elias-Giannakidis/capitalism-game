import pygame
import random
import math

TEAL = (0, 171, 169)
INDIGO = (106, 0, 255)
AMBER = (240, 163, 10)
ORANGE = (250, 104, 0)
RED = (229, 20, 0)
BLACK = (255, 255, 255)

class HireMe:
    def __init__(self, value):
        self.width = 130
        self.heigh = 30
        self.value = value
        self.pos = [0, 0]

    def action(self):
        self.progress = random.randint(2, 10)
        oldValue = self.value
        self.value = math.ceil(self.value + self.value/self.progress)
        return oldValue

    def getImage(self, win, pos):
        self.pos = pos
        t = 5
        pygame.draw.rect(win, INDIGO, [pos[0], pos[1], self.width, self.heigh])
        pygame.draw.rect(win, TEAL, [pos[0] + t, pos[1] + t, self.width - 2*t, self.heigh - 2*t])
        textfont = pygame.font.SysFont("monospace", size=17, bold=True)
        text = textfont.render("Hire me!" + str(self.value) + "$", 3, (0, 0, 0))
        win.blit(text, (pos[0] + 2*t, pos[1] + t))
        return win

    def onIt(self, pos):
        if (pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.width):
            if (pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.heigh):
                self.startPos = pos
                return True
        return False


class Action:
    def __init__(self):
        self.width = 130
        self.heigh = 30
        self.pos = [0, 0]

    def getImage(self, win, pos):
        self.pos = pos
        t = 5
        pygame.draw.rect(win, ORANGE, [pos[0], pos[1], self.width, self.heigh])
        pygame.draw.rect(win, AMBER, [pos[0] + t, pos[1] + t, self.width - 2 * t, self.heigh - 2 * t])
        textfont = pygame.font.SysFont("monospace", size=17, bold=True)
        text = textfont.render("Work slave!", 3, (0, 0, 0))
        win.blit(text, (pos[0] + 2 * t, pos[1] + t))
        return win

    def onIt(self, pos):
        if (pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.width):
            if (pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.heigh):
                self.startPos = pos
                return True
        return False

class Fire:
    def __init__(self):
        self.width = 50
        self.heigh = 50
        self.pos = [0, 0]

    def getImage(self, win, pos):
        self.pos = pos
        imageSize = (self.width, self.heigh)
        img = pygame.image.load("images/elements/fired.png")
        img.set_colorkey((255, 255, 255))
        img = pygame.transform.scale(img, imageSize)
        radius = self.width/2 + 2
        pygame.draw.circle(win, color=BLACK, center=(self.pos[0] + self.width / 2, self.pos[1] + self.heigh / 2), radius=radius + 1)
        pygame.draw.circle(win, color=RED, center=(self.pos[0] + self.width/2, self.pos[1] + self.heigh/2), radius=radius)
        win.blit(img, self.pos)
        return win

    def onIt(self, pos):
        if self.pos[0] < pos[0] < self.pos[0] + self.width:
            if self.pos[1] < pos[1] < self.pos[1] + self.heigh:
                self.startPos = pos
                return True
        return False


