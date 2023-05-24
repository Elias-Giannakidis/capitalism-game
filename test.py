deck = [1, 2, 3]

deck2 = deck.copy()
for num in deck2:
    newNum = num + 1
    deck.append(newNum)
    print(deck)