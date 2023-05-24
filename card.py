import pygame
from value import Value, Wallet
from action import HireMe, Action, Fire
import math
import random
from read import readConfiguration
import copy

UNIQ = (109, 135, 100)

conf = readConfiguration()
board_limits = conf["board_limits"]
min_tax = conf["capitalism"]["min_tax"]
tax = conf["capitalism"]["tax"]

class Card():
    def __init__(self, path):
        self.pos = random.sample(range(100, 600), 2)
        self.path = path
        self.imagePath = self.getPath(path)
        self.width = 150
        self.height = 150
        self.moving = False
        self.type = "general"
        self.first_turn = True

    def getIntoLimits(self):
        self.pos[0] = min(max(board_limits[0], self.pos[0]), board_limits[1])
        self.pos[1] = min(max(board_limits[2], self.pos[1]), board_limits[3])


    def getPath(self, path):
        return path

    def setColor(self, color):
        self.color = color

    def getImage(self, win, pos):
        imgSize = (self.width, self.height)
        imgPos = copy.deepcopy(self.pos)
        if (self.onIt(pos)):
            imgSize = (self.width + 10, self.height + 10)
            imgPos[0] = imgPos[0] - 5
            imgPos[1] = imgPos[1] - 5
        cardImage = pygame.image.load(self.imagePath)
        cardImage.set_colorkey((255, 255, 255))
        cardImage = pygame.transform.scale(cardImage, imgSize)

        win = self.drawBefore(win, pos)
        win = self.background(win)
        win.blit(cardImage, imgPos)
        win = self.drawAfter(win, pos)
        return win

    def drawBefore(self, win, pos):
        return win

    def drawAfter(self, win, pos):
        return win

    def background(self, win):
        return win

    def startMoving(self, pos):
        if self.onIt(pos):
            self.moving = True
        return self.moving

    def move(self, pos):
        if self.moving:
            self.pos[0] = self.pos[0] + pos[0] - self.startPos[0]
            self.pos[1] = self.pos[1] + pos[1] - self.startPos[1]
            self.startPos[0] = pos[0]
            self.startPos[1] = pos[1]
        self.moveAfter(pos)

    def moveAfter(self, pos):
        pass

    def onIt(self, pos):
        if self.pos[0] < pos[0] < self.pos[0] + self.width:
            if self.pos[1] < pos[1] < self.pos[1] + self.height:
                self.startPos = pos
                return True
        return False


class Capitalism(Card):

    def __init__(self, path):
        super().__init__(path)
        self.workers = []
        self.materials = []
        self.type = 'capitalism'

    def getInBoard(self, boardLimits):
        move = 100
        Xmin = boardLimits[0]
        Xmax = boardLimits[1]
        Ymin = boardLimits[2]
        Ymax = boardLimits[3]
        if(self.pos[0] < Xmin):
            self.pos[0] = Xmin + move
        if(self.pos[0] > Xmax):
            self.pos[0] = Xmax - move
        if(self.pos[1] < Ymin):
            self.pos[1] = Ymin + move
        if(self.pos[1] > Ymax):
            self.pos[1] = Ymax - move

    def getPath(self, path):
        return "images/capitalism/" + path + ".png"

    def background(self, win):
        x = self.pos[0] + self.width/2
        y = self.pos[1] + self.height/2
        pos = [x, y]
        radius = 50
        pygame.draw.circle(win, self.color, pos, radius)
        return win

    def payTax(self):
        tax_fee = math.ceil(max(int(min_tax), self.value.value * int(tax) / 100))
        self.value.value = self.value.value - tax_fee

    def payWorkers(self):
        for worker in self.workers:
            self.value.value = self.value.value - worker.value.value

    def hire(self, worker):
        worker.belong = self.id
        worker.color = self.color
        worker.hired()
        self.workers.append(worker)
        self.value.value = self.value.value - worker.value.value

    def drawAfter(self, win, pos):
        win = self.value.getImage(win, (self.pos[0], self.pos[1] - 25))
        return win

    def setValue(self, money):
        self.value = Value(money, "coin")

    def turnOver(self, boardLimits):
        Xmin = boardLimits[0]
        Xmax = boardLimits[1]
        Ymin = boardLimits[2]
        Ymax = boardLimits[3]
        return self.pos[0] < Xmin or self.pos[0] > Xmax or self.pos[1] < Ymin or self.pos[1] > Ymax

class Worker(Card):

    def __init__(self, path, conf):
        super().__init__(path)
        self.width = 120
        self.height = 120
        self.color = UNIQ
        self.belong = 0
        self.min_salary = conf["salary"][0]
        self.max_salary = conf["salary"][1]
        self.setValue(random.randint(self.min_salary, self.max_salary))
        self.workable = False
        self.worked = False
        self.action = Action()
        self.fire = Fire()
        self.type = "worker"
        self.possibility_appear = conf["possibility_appear"]
        self.no_work_possibility_leave = conf["no_work_possibility_leave"]
        self.work_possibility_leave = conf["work_possibility_leave"]

    def left(self):
        coin = random.randint(0, 100)
        if self.belong == 0:
            return coin <= self.no_work_possibility_leave
        else:
            return coin <= self.work_possibility_leave

    def refresh(self):
        self.pos[0] = random.randint(board_limits[0], board_limits[1])
        self.pos[1] = random.randint(board_limits[2], board_limits[3])
        self.setValue(random.randint(self.min_salary, self.max_salary))

    def getPath(self, path):
        return "images/workers/" + path + ".png"

    def getMaterialPath(self):
        return "images/materials/" + self.path + ".png"

    def background(self, win):
        x = self.pos[0]
        y = self.pos[1]
        pygame.draw.rect(surface=win, color=self.color, border_radius=15, width=8, rect=(x, y, self.width, self.height))
        return win

    def setValue(self, money):
        self.value = Value(money, "salary")
        self.hireme = HireMe(self.value.value)
        self.value.width = 75
        self.value.height = 75

    def refreshHire(self):
        self.color = UNIQ
        self.value.refreshValue()
        self.hireme = HireMe(self.value.value)
        self.belong = 0
        self.workable = False


    def drawAfter(self, win, pos):
        if self.workable:
            win = self.action.getImage(win, (self.pos[0] - 4, self.pos[1] + self.height - 22))
            win = self.fire.getImage(win, (self.pos[0] + self.width - 20, self.pos[1] - 20))
        else:
            win = self.hireme.getImage(win, (self.pos[0] - 4, self.pos[1] + self.height - 22))
        if self.onIt(pos):
            hand_img = pygame.image.load("images/elements/hand.png")
            hand_img = pygame.transform.scale(hand_img, (80, 80))
            material_img = pygame.image.load(self.getMaterialPath())
            material_img = pygame.transform.scale(material_img, (50, 50))
            win.blit(hand_img, (self.pos[0] - 80, self.pos[1] + self.height/4))
            win.blit(material_img, (self.pos[0] - 80, self.pos[1] + self.height/4))
        win = self.value.getImage(win, (self.pos[0], self.pos[1] - 40))
        return win

    def hired(self):
        self.value.value = self.hireme.action()
        self.value.lastValue = self.value.value

    def getProduct(self):
        product = Material(self.path)
        product.pos[0] = min(1100, self.pos[0] + random.randint(10, self.width + 20))
        product.pos[1] = min(900, self.pos[1] + self.height + random.randint(10, 60))
        product.color = self.color
        product.belong = self.belong
        return product


class Material(Card):
    def __init__(self, path):
        super().__init__(path)
        self.width = 60
        self.height = 60
        self.color = UNIQ
        self.type = "material"
        self.value = 50
        self.belong = 0
        self.amount = 1

    def drawAfter(self, win, pos):
        textfont = pygame.font.SysFont("monospace", size=17, bold=True)
        text = textfont.render(str(self.amount) + " X " + str(self.value) + "$", 3, (0, 0, 0))
        win.blit(text, (self.pos[0], self.pos[1] + self.height + 4))
        return win

    def getPath(self, path):
        return "images/materials/" + path + ".png"

    def background(self, win):
        x = self.pos[0] + self.width / 2
        y = self.pos[1] + self.height / 2
        pos = [x, y]
        radius = 30
        pygame.draw.circle(win, self.color, pos, radius)
        return win


class Customer(Card):
    def __init__(self, path, conf):
        super().__init__(path)
        self.type = 'customer'
        self.width = 120
        self.height = 120
        self.possibility_buy = conf["possibility_buy"]
        self.possibility_appear = conf["possibility_appear"]
        self.possibility_leave = conf["possibility_leave"]
        self.min_budget = conf["budget"][0]
        self.max_budget = conf["budget"][1]
        self.wallet = Wallet(random.randint(self.min_budget, self.max_budget))
        self.min_max_price = conf["max_price"][0]
        self.max_max_price = conf["max_price"][1]
        self.max_price = random.randint(self.min_max_price, self.max_max_price)

    def left(self):
        coin = random.randint(0, 100)
        return self.possibility_leave <= coin or self.wallet.value <= 0

    def buy(self):
        coin = random.randint(0, 100)
        return self.possibility_buy <= coin

    def refresh(self):
        self.pos[0] = random.randint(board_limits[0], board_limits[1])
        self.pos[1] = random.randint(board_limits[2], board_limits[3])
        self.wallet = Wallet(random.randint(self.min_budget, self.max_budget))
        self.max_price = random.randint(self.min_max_price, self.max_max_price)

    def getPath(self, path):
        return "images/customers/" + path + ".png"

    def getMaterialPath(self):
        return "images/materials/" + self.path + ".png"

    def drawAfter(self, win, pos):
        if self.onIt(pos):
            think_img = pygame.image.load("images/elements/think.png")
            think_img = pygame.transform.scale(think_img, (80, 80))
            material_img = pygame.image.load(self.getMaterialPath())
            material_img = pygame.transform.scale(material_img, (50, 50))
            win.blit(think_img, (self.pos[0] + self.width - 5, self.pos[1] + 5))
            win.blit(material_img, (self.pos[0] + self.width + 15, self.pos[1] + 15))
            textfont = pygame.font.SysFont("monospace", size=23, bold=True)
            text = textfont.render(str(self.max_price), 3, (0, 0, 0))
            win.blit(text, (self.pos[0] + self.width, self.pos[1] - 6))
        win = self.wallet.getImage(win, (self.pos[0], self.pos[1] + self.height - 10))
        return win

class Shit(Card):

    def __init__(self, path):
        super().__init__(path)
        self.timeout = 2
        self.width = 60
        self.height = 60
        self.pos = [0, 0]
        self.type = 'shit'

    def left(self):
        self.timeout = self.timeout - 1
        return self.timeout <= 0

    def getPath(self, path):
        return "images/elements/shit.png"

class Money(Card):
    def __init__(self, path):
        super().__init__(path)
        self.width = 50
        self.height = 50
        self.pos = [0, 0]
        self.type = 'money'
        self.color = UNIQ
        self.value = 0
        self.belong = 0

    def getPath(self, path):
        return "images/elements/money.png"

    def background(self, win):
        pygame.draw.circle(win, center=(self.pos[0] + self.width/2, self.pos[1] + self.height/2), radius=self.width/2 + 4, color=self.color)
        return win

    def drawAfter(self, win, pos):
        textfont = pygame.font.SysFont("monospace", size=17, bold=True)
        text = textfont.render(str(self.value) + "$", 3, (0, 0, 0))
        win.blit(text, (self.pos[0] + 2, self.pos[1] + self.height - 1))
        return win