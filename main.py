import pygame
import random
from card import Card, Capitalism, Worker, Material, Customer, Shit, Money
from action import HireMe
from read import readConfiguration, getPlayers, getProducts
from helper import getNewCards, getMoney, getAllMoney, removeCards
import copy
import math
from value import Cursoras

# Read configuration
config = readConfiguration()

# players
players = 2
PLAYERS = getPlayers(players)

products = getProducts()

# Define the colors of the game
UNIQ = (109, 135, 100)
COLORS = config["colors"]
random.shuffle(COLORS)

# Window initialize
pygame.init()
WIDTH = config["window_size"][0]
HEIGHT = config["window_size"][1]
win = pygame.display.set_mode((WIDTH, HEIGHT))
BACKGROUND = pygame.image.load("images/background.png")
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH - 20, HEIGHT - 20))

# Board limits
BOARDLIMITS = config['board_limits']

# Define the capitalism
capitalisms = []
colorIndex = 0
budget = config["capitalism"]["budget"]
for player in PLAYERS:
    path = str(player)
    color = COLORS[colorIndex]
    capitalism = Capitalism(path)
    capitalism.setColor(color)
    capitalism.setValue(budget)
    capitalism.id = colorIndex + 1
    capitalisms.append(capitalism)
    colorIndex = colorIndex + 1

# init deck
deck = []
missRounds = config["skip_turns"]
for _ in range(missRounds):
    deck = getNewCards(deck)

# run the game!
run = True
newTurn = True
turn = 0
somebody_moving = False
cursoras = Cursoras()
while run:

    # define the capitalism turn
    player = capitalisms[turn]
    color = player.color

    # player moved out of limits
    if(newTurn):

        # get Cards into limits
        for card in deck:
            card.getIntoLimits()

        # player pays
        deck.append(player)
        player.payTax()
        player.payWorkers()

        # remove cards
        deck = removeCards(deck)

        # Add new cards
        deck = getNewCards(deck)

        # Workers didn't work this turn
        for card in deck:
            if card.type == 'worker':
                card.workable = player.id == card.belong
                card.worked = False

        # Update last value of the workers
        for card in deck:
            if card.type == "worker":
                card.value.lastValue = card.value.value

        # Move player in the board
        player.getInBoard(BOARDLIMITS)
        newTurn = False

    # Get mouse position
    pos = pygame.mouse.get_pos()
    x = pos[0]
    y = pos[1]
    mousePos = [x, y]

    # Refresh cursora
    noCursor = True
    for card in deck:
        noCursor = noCursor and not card.onIt(mousePos)
    if noCursor:
        cursoras.cursor = 0

    # event handler
    for event in pygame.event.get():

        # Get mouse position
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        mousePos = [x, y]

        # quit the game
        if event.type == pygame.QUIT:
            run = False

        # key events
        if event.type == pygame.KEYDOWN:

            cursoras.getkey(event.key)

            if event.key == 13:
                for card in deck:
                    if card.onIt(mousePos):
                        if card.type == 'material' and card.belong == player.id:
                            card.value = cursoras.cursor
                            cursoras.cursor = 0
                        if card.type == 'worker' and card.belong == player.id:
                            raiseValue = cursoras.cursor - card.value.value
                            card.value.raiseValue(raiseValue)
                            card.hireme = HireMe(card.value.value)
                            card.hireme.action()
                            cursoras.cursor = 0


        # scroll events
        if event.type == pygame.MOUSEWHEEL:
            scroll = event.y
            scroll_array = [1, 5, 10, 40, 80, 100, 250, 500, 1000]
            scroll = math.ceil(scroll_array[abs(scroll - 1)] * scroll/abs(scroll))
            for card in deck:
                # Increase salary of worker
                if card.type == 'worker':
                    if(card.belong == player.id):
                        if(card.value.onIt(mousePos)):
                            card.value.raiseValue(scroll)
                            card.hireme = HireMe(card.value.value)
                            card.hireme.action()

                # Change the price of the material
                if card.type == 'material':
                    if(card.belong == player.id and card.onIt(mousePos)):
                        card.value = max(0, card.value + scroll)

        # mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for card in deck:
                    # Move cards
                    if not somebody_moving:
                        somebody_moving = card.startMoving(mousePos)

                    # Workers actions
                    if card.type == 'worker':
                        if(card.belong == player.id):
                            # If action button (work slave!) has pressed
                            if(card.action.onIt(mousePos) and not card.worked):
                                product = card.getProduct()
                                player.materials.append(product)
                                deck.append(product)
                                card.worked = True

                            # If fired button has pressed (kick)
                            if(card.fire.onIt(mousePos)):
                                player.value.value = player.value.value - 3 * card.value.value
                                player.workers.remove(card)
                                card.refreshHire()

                        # Hire the customer (Hire me!)
                        if card.belong != player.id:
                            if card.hireme.onIt(mousePos):
                                player.hire(card)
                                card.workable = True

            # Split materials
            if event.button == 3:
                for card in deck:
                    if card.type == 'material' and card.amount > 1 and card.onIt(mousePos):
                        card1 = copy.deepcopy(card)
                        card2 = copy.deepcopy(card)

                        card1.pos[0] = card1.pos[0] + random.randint(10, 60)
                        card1.pos[1] = card1.pos[1] + random.randint(-60, -10)
                        card2.pos[0] = card2.pos[0] + random.randint(-60, -10)
                        card2.pos[1] = card2.pos[1] + random.randint(10, 60)

                        card1.amount = math.ceil(card1.amount/2)
                        card2.amount = math.floor(card2.amount/2)

                        deck.remove(card)
                        deck.append(card1)
                        deck.append(card2)

        if event.type == pygame.MOUSEBUTTONUP:
            somebody_moving = False

            # Player moved out of board
            if player.turnOver(BOARDLIMITS):
                turn = turn + 1
                newTurn = True

                # Customer Buying
                for card in deck:
                    if card.type == 'customer':
                        while card.buy() and not card.first_turn:
                            card.buyTimeout = random.randint(2, 7)
                            budget = card.wallet.value
                            product = card.path
                            possibleProducts = []
                            minValue = 10000000
                            for material in deck:
                                if material.type == 'material' and material.path == product:
                                    minValue = min(minValue, material.value)
                                    possibleProducts.append(material)
                            random.shuffle(possibleProducts)
                            buy = card.max_price >= minValue and budget >= minValue
                            if buy:
                                for material in possibleProducts:
                                    if material.value == minValue and buy:
                                        belong = material.belong
                                        card.wallet.value = card.wallet.value - minValue
                                        deck = getMoney(deck, material)
                                        if material.amount <= 1:
                                            deck.remove(material)
                                        else:
                                            material.amount = material.amount - 1
                                        buy = False

                # Remove player
                if player.value.value <= 0:
                    for worker in player.workers:
                        worker.refresh()
                    pos = player.pos
                    shit1 = Shit("")
                    shit1.pos = pos
                    deck.append(shit1)
                    shit2 = Shit("")
                    shit2.pos = [pos[0] + 20, pos[1] - 10]
                    deck.append(shit2)
                    shit3 = Shit("")
                    shit3.pos = [pos[0] - 10, pos[1] + 10]
                    deck.append(shit3)
                    shit4 = Shit("")
                    shit4.pos = [pos[0] - 10, pos[1] - 10]
                    deck.append(shit4)
                    capitalisms.remove(player)
                    players = players - 1

                if (turn > players - 1):
                    turn = 0

            # Material collision:
            collision = []
            for card in deck:
                if card.type == 'material' and card.belong == player.id and card.onIt(mousePos):
                    collision.append(card)
                while len(collision) > 1:
                    newMaterial = copy.copy(collision[0])
                    newMaterial.amount = 0
                    newMaterial.value = 0
                    for mat in copy.copy(collision):
                        if mat.path == newMaterial.path:
                            newMaterial.amount = newMaterial.amount + mat.amount
                            newMaterial.value = newMaterial.value + mat.value
                            deck.remove(mat)
                            collision.remove(mat)
                    newMaterial.value = math.ceil(newMaterial.value/newMaterial.amount)
                    deck.append(newMaterial)

            # Money collision
            collision = []
            for card in deck:
                if card.type == "money" and card.onIt(mousePos) and card.belong == player.id:
                    collision.append(card)
                while len(collision) > 1:
                    newMoney = copy.copy(collision[0])
                    newMoney.value = 0
                    for mon in copy.copy(collision):
                        if mon.belong == newMoney.belong:
                            newMoney.value = newMoney.value + mon.value
                            deck.remove(mon)
                            collision.remove(mon)
                    deck.append(newMoney)

            # Players buy material or earn money
            if player.onIt(mousePos):
                for card in deck:
                    # Define the collision cards
                    if card.onIt(mousePos):
                        # earn money
                        if card.type == 'money' and card.belong == player.id:
                            player.value.value = player.value.value + card.value
                            deck.remove(card)

                        # buy material
                        if card.type == 'material' and card.belong != player.id:
                            card.pos[0] = card.pos[0] + 60
                            card.pos[1] = card.pos[1] + 50
                            deck = getAllMoney(deck, card)
                            card.pos[1] = card.pos[1] - 100
                            card.belong = player.id
                            card.color = player.color
                            player.value.value = player.value.value - card.value * card.amount

            # gift money
            for capitalism in capitalisms:
                if capitalism.id != player.id and capitalism.onIt(mousePos):
                    for card in deck:
                        if card.type == "money" and card.onIt(mousePos) and card.belong == player.id:
                            capitalism.value.value = capitalism.value.value + card.value
                            deck.remove(card)

            # gift materials
            for capitalism in capitalisms:
                if capitalism.id != player.id and capitalism.onIt(mousePos):
                    for card in deck:
                        if card.type == "material" and card.onIt(mousePos) and card.belong == player.id:
                            card.belong = capitalism.id
                            card.color = capitalism.color
                            card.pos[0] = card.pos[0] + 60
                            card.pos[1] = card.pos[1] + 60


            for card in deck:
               card.moving = False

            if(newTurn):
                deck.remove(player)

        if event.type == pygame.MOUSEMOTION:
            for card in deck:
                card.move(mousePos)

    # windows refresh
    pygame.draw.rect(surface=win, color=player.color, rect=(0, 0, WIDTH, HEIGHT))
    win.blit(BACKGROUND, (10, 10))
    for card in deck:
        win = card.getImage(win, mousePos)
    for card in capitalisms:
        win = card.getImage(win, mousePos)
    win = cursoras.draw(win, mousePos)
    pygame.display.update()

pygame.quit()
