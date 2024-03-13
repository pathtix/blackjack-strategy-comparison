import random
import pandas as pd

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        
        if self.value == 11:
            self.name = "Jack"
        elif self.value == 12:
            self.name = "Queen"
        elif self.value == 13:
            self.name = "King"
        else:
            self.name = str(self.value)

    def __repr__(self):
        return f"{self.name} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades'] for value in range(1, 14)]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop(0)
        else:
            return None

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        ace = False
        
        for card in self.cards:
            if card.value > 10: # Jack, Queen, King
                value += 10
            elif card.value == 1: # Ace can be 1 or 11
                value += 11
                ace = True
            else:
                value += card.value
        
        if ace and value > 21:
            value -= 10
        return value

# TODO : implement stand bruteforce

def main():
    deck = Deck()
    deck.shuffle()

if __name__ == "__main__":
    main()
