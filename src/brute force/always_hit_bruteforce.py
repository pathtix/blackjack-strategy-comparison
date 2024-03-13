import random
import pandas as pd
import os

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

def simulate_game(player_hand, dealer_hand, deck):
    while player_hand.get_value() < 19:
        player_hand.add_card(deck.deal())
    
    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(deck.deal())

    player_total = player_hand.get_value()
    dealer_total = dealer_hand.get_value()

    if player_total > 21:
        return 'Lose'
    elif dealer_total > 21 or player_total > dealer_total:
        return 'Win'
    elif player_total == dealer_total:
        return 'Tie'
    else:
        return 'Lose'

def brute_force_simulation(deck):
    player_hand = Hand()
    dealer_hand = Hand()

    player_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())

    dealer_hand.add_card(deck.deal())

    result = simulate_game(player_hand, dealer_hand, deck)

    return {
        'Player Hand': str(player_hand.cards),
        'Dealer Hand': str(dealer_hand.cards),
        'Player Total': player_hand.get_value(),
        'Dealer Total': dealer_hand.get_value(),
        'Result': result
    }

def main():
    results = []
    wins = 0
    ties = 0
    loses = 0

    deck1 = Deck()
    deck1.shuffle()

    deck2 = Deck()
    deck2.shuffle()

    deck = Deck()
    deck.cards = deck1.cards + deck2.cards
    deck.shuffle()

    while len(deck.cards) >= 10:
        # print(f"Remaining cards: {len(deck.cards)}")
        result = brute_force_simulation(deck)

        if result['Result'] == 'Win':
            wins += 1
        elif result['Result'] == 'Tie':
            ties += 1
        else:
            loses += 1

        results.append(result)

    winrate = wins / (wins + ties + loses) * 100

    results.append({
        'Player Hand': '',
        'Dealer Hand': '',
        'Player Total': '',
        'Dealer Total': '',
        'Result': '% ' + "{:.2f}".format(winrate)
    })

    df = pd.DataFrame(results)
    return df
    

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_filename = os.path.join(script_dir, 'always_hit_results', 'always_hit_results.xlsx')

    with pd.ExcelWriter(output_filename) as writer:
        for i in range(10): # Run the simulation 10 times
            df = main()
            df.to_excel(writer, sheet_name= "test" + str(i), index=False)
            

    
    
