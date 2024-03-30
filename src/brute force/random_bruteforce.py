import pandas as pd
import os
import random
import time

random.seed(time.time())

from resources.deck import Deck
from resources.hand import Hand

class RadnomBruteForce:
    def __init__(self):
        self.deck_1 = Deck()
        self.deck_1.shuffle()
        self.deck_2 = Deck()
        self.deck_2.shuffle()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards
        self.main_deck.shuffle()

    def simulate_game(self, player_hand, dealer_hand, deck):
        while True:
            action = random.choice(['H', 'S'])  # Randomly choose 'H' or 'S'
            player_total = player_hand.get_value()
            if action == 'H':
                player_hand.add_card(deck.deal())
            else:
                break
        
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

    def bj_simulation(self, deck):
        player_hand = Hand()
        dealer_hand = Hand()

        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())

        dealer_hand.add_card(deck.deal())

        result = self.simulate_game(player_hand, dealer_hand, deck)

        return {
            'Player Hand': str(player_hand.cards),
            'Dealer Hand': str(dealer_hand.cards),
            'Player Total': player_hand.get_value(),
            'Dealer Total': dealer_hand.get_value(),
            'Result': result
        }

    

if __name__ == "__main__":
    RBF = RadnomBruteForce()

    results = []
    wins = 0
    ties = 0
    loses = 0

    while len(RBF.main_deck.cards) >= 10:
        # print(f"Remaining cards: {len(deck.cards)}")
        result = RBF.bj_simulation(RBF.main_deck)

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

    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(script_dir, 'random_hitstand_results')
    output_filename = os.path.join(output_dir, 'random_hitstand_results.xlsx')

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    with pd.ExcelWriter(output_filename) as writer:
        for i in range(10): # Run the simulation 10 times
            df.to_excel(writer, sheet_name= "test" + str(i), index=False)
    
    
