import pygame
import math

class Value:
    def __init__(self, value, path):
        self.initValue = value
        self.value = value
        self.lastValue = value
        self.path = "images/elements/" + path + ".png"
        self.width = 50
        self.height = 50
        self.pos = [0, 0]

    def refreshValue(self):
        self.value = self.initValue
        self.lastValue = self.initValue

    def getImage(self, win, pos):
        self.pos = pos
        img = pygame.image.load(self.path)
        img.set_colorkey((255, 255, 255))
        img = pygame.transform.scale(img, (self.width, self.height))
        win.blit(img, pos)
        textfont = pygame.font.SysFont("monospace", size=25, bold=True)
        text = textfont.render(str(self.value) + "$", 4, (0, 0, 0))
        win.blit(text, (pos[0] + self.width, pos[1] + 6))
        return win

    def onIt(self, pos):
        if (pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.width):
            if (pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.height):
                self.startPos = pos
                return True
        return False

    def raiseValue(self, value):
        self.value = max(self.lastValue, self.value + value)


class Wallet:
    def __init__(self, budget):
        self.width = 50
        self.height = 50
        self.value = budget
        self.path = "images/elements/wallet.png"

    def getImage(self, win, pos):
        img = pygame.image.load(self.path)
        img.set_colorkey((255, 255, 255))
        img = pygame.transform.scale(img, (self.width, self.height))
        textfont = pygame.font.SysFont("monospace", size=25, bold=True)
        text = textfont.render(str(self.value) + "$", 4, (0, 0, 0))
        win.blit(img, pos)
        win.blit(text, (pos[0] + self.width + 1, pos[1] + self.height/4))
        return win

class Cursoras:
    def __init__(self):
        self.path = "images/elements/cursor.png"
        self.size = [50, 50]
        self.offset = [2, -40]
        self.cursor = 0

    def draw(self, win, pos):
        if self.cursor > 0:
            img = pygame.image.load(self.path)
            img = pygame.transform.scale(img, self.size)
            x0 = pos[0] + self.offset[0] - 20
            x1 = 100
            y0 = pos[1] + self.offset[1] - 20
            y1 = 20
            rect1 = [x0, y0, x1, y1]
            rect2 = [x0 - 2, y0, x1 + 4, y1 + 2]
            textFont = pygame.font.SysFont("monospace", size=20, bold=True)
            text = textFont.render(str(self.cursor), 4, (0, 0, 0))
            win.blit(img, (pos[0] + self.offset[0], pos[1] + self.offset[1]))
            pygame.draw.rect(surface=win, color=(0, 0, 0), rect=rect2)
            pygame.draw.rect(surface=win, color=(255, 255, 255), rect=rect1)
            win.blit(text, (x0 + 10, y0))
        return win

    def getkey(self, key):
        if 48 <= key <= 57:
            value_key = key - 48
            self.cursor = 10 * self.cursor + value_key
        if key == 8:
            self.cursor = math.floor(self.cursor / 10)
