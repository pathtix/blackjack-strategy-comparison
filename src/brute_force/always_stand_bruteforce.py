import pandas as pd
import os

from resources.deck import Deck
from resources.hand import Hand

from settings import AlwaysStandBruteForceSettings

class AlwaysStandBruteForce:
    def __init__(self):
        self.set_simulation_settings()
        self.create_deck()

    def set_simulation_settings(self):
        self.simulation_amount = AlwaysStandBruteForceSettings['Simulation Amount']
        self.money = AlwaysStandBruteForceSettings['Initial Money']
        self.bet_amount = AlwaysStandBruteForceSettings['Bet Amount']

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
            self.money += self.bet_amount * 2
            return 'Win'
        elif player_total == dealer_total:
            self.money += self.bet_amount
            return 'Tie'
        elif player_total == 21 and len(player_hand.cards) == 2:
            self.money += self.bet_amount * 2.5
            return 'Blackjack'
        else:
            return 'Lose'

    def bj_simulation(self, deck):
        self.money -= self.bet_amount
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
    
    def calculate_roi(self, df):
        initial_money = AlwaysStandBruteForceSettings['Initial Money']
        df['Net Profit'] = df['Money'] - initial_money
        df['Total Invested'] = df['Money'].apply(lambda x: x if x < 0 else initial_money)
        df['ROI'] = (df['Net Profit'] / df['Total Invested']) * 100
        return df

    def simulate(self):
            results = []
            wins = 0
            ties = 0
            loses = 0

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
            df = self.calculate_roi(df)
            return df
    
    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'always_stand_results')
        output_filename = os.path.join(output_dir, 'always_stand_results.xlsx')

        os.makedirs(output_dir, exist_ok=True)
        all_results = []
        self.set_simulation_settings()
        for i in range(self.simulation_amount):
            self.create_deck()
            self.set_simulation_settings()
            df = self.simulate()
            df['Simulation'] = i
            all_results.append(df)

        # Concatenate all results into a single DataFrame
        final_df = pd.concat(all_results, ignore_index=True)

        try:
            print(f"Saving results to {output_filename}")
            final_df.to_excel(output_filename, index=False)
        except Exception as e:
            print(f"An error occurred while saving results: {e}")

        return "Simulation complete. Check the output file for results."
