import pandas as pd
import os

from resources.deck import Deck
from resources.hand import Hand

from settings import AlwaysStandBruteForceSettings

class AlwaysStandBruteForce:
    def __init__(self):
        self.create_deck()
        self.simulation_amount = 10

        self.money = 1000

    def set_simulation_amount(self):
        self.simulation_amount = AlwaysStandBruteForceSettings['Simulation Amount']

    def shuffle_deck(self):
        self.main_deck.shuffle()
    
    def create_deck(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def simulate_game(self, player_hand, dealer_hand, deck):
        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal())

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return 'Lose'
        elif dealer_total > 21 or player_total > dealer_total:
            self.money += 200
            return 'Win'
        elif player_total == dealer_total:
            self.money += 100
            return 'Tie'
        else:
            return 'Lose'

    def bj_simulation(self, deck):
        self.money -= 100
        self.set_simulation_amount()
        player_hand = Hand()
        dealer_hand = Hand()

        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())

        dealer_hand.add_card(deck.deal())

        result = self.simulate_game(player_hand, dealer_hand, deck)

        return {
            'Player Hand': str(player_hand.cards),
            'Player Hand Value': player_hand.get_value(),
            'Dealer Hand': str(dealer_hand.cards),
            'Dealer Hand Value': dealer_hand.get_value(),
            'Result': result,
            'Action': 'S',
            'Money': self.money
        }
    
    def simulate(self):
            results = []
            wins = 0
            ties = 0
            loses = 0
            
            self.money = 1000
            self.shuffle_deck()
            while len(self.main_deck.cards) >= 10:
                result = self.bj_simulation(self.main_deck)

                if result['Result'] == 'Win':
                    wins += 1
                elif result['Result'] == 'Tie':
                    ties += 1
                else:
                    loses += 1

                results.append(result)
            
            #winrate = wins / (wins + ties + loses) * 100

            df = pd.DataFrame(results)
            return df

    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'always_stand_results')
        output_filename = os.path.join(output_dir, 'always_stand_results.xlsx')

        os.makedirs(output_dir, exist_ok=True)

        # Create a new Excel file or clear the existing one
        df_empty = pd.DataFrame()
        df_empty.to_excel(output_filename, index=False)  # This creates a new file or overwrites an existing file

        i = 0
        while (i < self.simulation_amount):
            print(f"Simulation {i}")
            self.create_deck()
            df = self.simulate()
            try:
                # Open the Excel writer in append mode now that the file definitely exists
                with pd.ExcelWriter(output_filename, mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name="test" + str(i), index=False)
            except Exception as e:
                print(f"An error occurred during simulation {i}: {e}")
            i += 1

        return "Simulation complete. Check the output file for results."
