import random

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

def play_round(deck):
    player_hand = Hand()
    dealer_hand = Hand()

    player_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())

    print("Your hand:", player_hand.cards + [f"Total value: {player_hand.get_value()}"])
    print("Dealer's hand:", dealer_hand.cards + [f"Total value: {dealer_hand.get_value()}"])

    while True:
        choice = input("Do you want to hit or stand? (h/s): ").lower()
        if choice == 'h':
            player_hand.add_card(deck.deal())
            print("Your hand:", player_hand.cards)

            if player_hand.get_value() > 21:
                print("Busted! You lose. You got: " + str(player_hand.get_value()))
                return False
            
        elif choice == 's':
            while dealer_hand.get_value() < 17:
                dealer_hand.add_card(deck.deal())
            print("Dealer's hand:", dealer_hand.cards)

            if dealer_hand.get_value() > 21:
                print("Dealer busted! You win. Dealer got: " + str(dealer_hand.get_value()))
            elif dealer_hand.get_value() >= player_hand.get_value():
                print("Dealer wins. Dealer got: " + str(dealer_hand.get_value()) + ", you got: " + str(player_hand.get_value()))
            else:
                print("You win! You got: " + str(player_hand.get_value()) + ", dealer got: " + str(dealer_hand.get_value()))
            return True
        else:
            print("Invalid choice. Please enter 'h' or 's'.")

def main():
    deck = Deck()
    while True:
        deck.shuffle()
        if not play_round(deck):
            print("Game over!")
        play_again = input("Do you want to play again? (y/n): ").lower()
        
        if play_again != 'y':
            break

if __name__ == "__main__":
    main()
