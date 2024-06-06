import os
import ast
import time
import pickle

import pandas as pd
import numpy as np

from resources.deck import Deck
from resources.hand import Hand

from settings import RLSettings

class ReinforcementLearning:
    def __init__(self):
        self.create_deck()
        self.q_table_path = None
        self.set_simulation_settings()

        self.simulation_amount = 10
        self.money = 1000
        self.q_table = self.import_q_table()


    def set_simulation_settings(self):
        self.simulation_amount = RLSettings['Simulation Amount']
        self.money = RLSettings['Initial Money']
        self.bet_amount = RLSettings['Bet Amount']
        self.q_table_path = RLSettings['Q Table Path']
        self.alpha = RLSettings['Alpha']
        self.gamma = RLSettings['Gamma']
        self.epsilon = RLSettings['Epsilon']
        self.number_of_episodes = RLSettings['Number of Episodes']

    def shuffle_deck(self):
        self.main_deck.shuffle()

    def create_deck(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()
        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def import_q_table(self):
        with open(self.q_table_path, 'rb') as f:
            self.q_table = pickle.load(f)
        return self.q_table

    def choose_action(self, state):
        return np.argmax(self.q_table[state])

    def simulate_game(self, player_hand, dealer_hand, deck):
        dealer_up = dealer_hand.cards[0]
        dealer_up_value = dealer_up.value
        double_down = False
        if dealer_up_value > 10:
            dealer_up_value = 10
        elif dealer_up_value == 1:
            dealer_up_value = 11

        player_card_value = player_hand.get_value()
        action = self.choose_action((player_card_value, dealer_up_value))
        action_list = []

        if action == 1:  # Hit
            while action == 1:
                player_hand.add_card(deck.deal())
                player_card_value = player_hand.get_value()
                action_list.append('Hit')
                if player_card_value > 21:
                    return 'Lose', action_list
                action = self.choose_action((player_card_value, dealer_up_value))
        elif action == 2:  # Double
            if self.money >= self.bet_amount:
                self.money -= self.bet_amount
                player_hand.add_card(deck.deal())
                player_card_value = player_hand.get_value()
                action_list.append('Double')
                double_down = True
                if player_card_value > 21:
                    return 'Lose', action_list
        else:
            action_list.append('Stand')

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return 'Lose', action_list
        elif dealer_total > 21 or player_total > dealer_total:
            self.money += self.bet_amount * 2
            return 'Win', action_list
        elif (dealer_total > 21 or player_total > dealer_total) and double_down:
            self.money += self.bet_amount * 4
            return 'Win'
        elif player_total == 21 and len(player_hand.cards) == 2:
            self.money += self.bet_amount * 2.5
            return 'Blackjack', action_list
        elif player_total == dealer_total:
            self.money += self.bet_amount
            return 'Tie', action_list
        else:
            return 'Lose', action_list

    def bj_simulation(self, deck):
        self.money -= self.bet_amount
        action_list = []
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
            'Result': result[0],
            'Action': result[1] if len(result) > 1 else None,
            'Money': self.money,
        }
    
    def calculate_roi(self, df):
        initial_money = RLSettings['Initial Money']
        df['Net Profit'] = df['Money'] - initial_money
        df['Total Invested'] = df['Money'].apply(lambda x: x if x < 0 else initial_money)
        df['ROI'] = (df['Net Profit'] / df['Total Invested']) * 100
        return df

    def simulate(self):
        results = []
        wins, ties, loses = 0, 0, 0

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

        total_games = wins + ties + loses
        winrate = (wins / total_games * 100) if total_games > 0 else 0

        df = pd.DataFrame(results)
        df = self.calculate_roi(df)
        return df

    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'reincforment_learing_results')
        output_filename = os.path.join(output_dir, 'reincforment_learing_results.xlsx')

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

if __name__ == '__main__':
    RL = ReinforcementLearning()
    print(RL.output_results())
