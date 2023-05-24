from read import readConfiguration
from card import Worker, Customer, Money, Shit
import copy
import random

def getWorkers():
    conf = readConfiguration()
    workers = []
    for material in conf["materials"]:
        path = material['path']
        conf = material["worker"]
        newWorker = Worker(path, conf)
        workers.append(newWorker)
    return workers

def getCustomers():
    conf = readConfiguration()
    customers = []
    for material in conf["materials"]:
        path = material["path"]
        conf = material["customer"]
        newCustomer = Customer(path, conf)
        customers.append(newCustomer)
    return customers

def getCards():
    cards = getWorkers()
    customers = getCustomers()
    for customer in customers:
        cards.append(customer)
    return cards

cards = getCards()

def getNewCards(deck):
    for card in deck:
        card.first_turn = False
    for card in cards:
        coin = random.randint(0, 100)
        if coin <= card.possibility_appear:
            newCard = copy.deepcopy(card)
            newCard.refresh()
            deck.append(newCard)
    return deck

def removeCards(deck):
    for card in deck:
        if card.type == 'worker' or card.type == "customer":
            if card.left() and not card.first_turn:
                pos = card.pos
                shit = Shit("")
                shit.pos = pos
                deck.remove(card)
                deck.append(shit)
        if card.type == 'shit':
            if card.left() and not card.first_turn:
                deck.remove(card)
    return deck


def getMoney(deck, material):
    money = Money("")
    money.pos = copy.deepcopy(material.pos)
    money.belong = material.belong
    money.value = copy.deepcopy(material.value)
    money.color = copy.deepcopy(material.color)
    if material.amount > 1:
        money.pos[0] = money.pos[0] + random.randint(30, 70)
        money.pos[1] = money.pos[1] + random.randint(30, 100)
    deck.append(money)
    return deck

def getAllMoney(deck, material):
    money = Money("")
    money.pos = copy.deepcopy(material.pos)
    money.belong = material.belong
    money.value = copy.deepcopy(material.value) * copy.deepcopy(material.amount)
    money.color = copy.deepcopy(material.color)
    deck.append(money)
    return deck

