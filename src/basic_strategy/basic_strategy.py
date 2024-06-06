import pandas as pd
import os
import ast
import time

from resources.deck import Deck
from resources.hand import Hand

from settings import BasicStrategyWithoutCountingSettings

class BasicStrategy:
    def __init__(self):
        self.set_simulation_settings()
        self.create_deck()
        self.simulation_amount = 10


    def set_simulation_settings(self):
        self.simulation_amount = BasicStrategyWithoutCountingSettings['Simulation Amount']
        self.money = BasicStrategyWithoutCountingSettings['Initial Money']
        self.isDoubleAllowed = BasicStrategyWithoutCountingSettings['Doubleing Allowed']
        self.bet_amount = BasicStrategyWithoutCountingSettings['Bet Amount']

    def shuffle_deck(self):
        self.main_deck.shuffle()

    def create_deck(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def check_basicstrategy(self, player_hand_value, dealer_hand_value):
        H = "Hit"
        S = "Stand"
        Dh = "Double if possible, otherwise hit"
        Rh = "Surrender if possible, otherwise hit"
        Rs = "Surrender if possible, otherwise stand"

        if (dealer_hand_value == 11 or dealer_hand_value == 12 or dealer_hand_value == 13):
            dealer_hand_value = 10

        player_index = player_hand_value - 4  # Adjust for 0-based index, as the matrix starts from 4
        dealer_index = dealer_hand_value - 2  # Adjust for 0-based index, as the matrix starts from 2

        hard_strategy = [
            #2   3   4   5   6   7   8   9   10  A
            [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 4
            [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 5
            [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 6
            [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 7
            [H,  H,  H,  H,  H,  H,  H,  H,  H,  H],   # 8
            [H,  Dh, Dh, Dh, Dh, H,  H,  H,  H,  H],   # 9
            [Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, H,  H],   # 10
            [Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh, Dh],  # 11
            [H,  H,  S,  S,  S,  H,  H,  H,  H,  H],   # 12
            [S,  S,  S,  S,  S,  H,  H,  H,  H,  H],   # 13
            [S,  S,  S,  S,  S,  H,  H,  H,  H,  H],   # 14
            [S,  S,  S,  S,  S,  H,  H,  H,  Rh, Rh],  # 15
            [S,  S,  S,  S,  S,  H,  H,  Rh, Rh, Rh],  # 16
            [S,  S,  S,  S,  S,  S,  S,  S,  S,  Rs],  # 17
            [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 18
            [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 19
            [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 20
            [S,  S,  S,  S,  S,  S,  S,  S,  S,  S],   # 21
        ]

        strategy = hard_strategy[player_index][dealer_index]

        return strategy

    def find_action(self, player_hand, dealer_up):
        player_card_value = player_hand.get_value()
        #print(player_card_value, dealer_up.value)
        action = self.check_basicstrategy(player_card_value, dealer_up.value)
        #print(action)
        return action

    def simulate_game(self, player_hand, dealer_hand, deck):
        dealer_up = dealer_hand.cards[0]
        action = self.find_action(player_hand, dealer_up)
        double_down = False
        action_list = []

        while action == 'Hit' or action == 'Double if possible, otherwise hit' or action == 'Surrender if possible, otherwise hit':
            if action == 'Double if possible, otherwise hit':
                if len(player_hand.cards) == 2:  # Typically doubling down is only allowed on the first move
                    action_list.append('Doubled')
                    self.money -= self.bet_amount
                    player_hand.add_card(deck.deal())
                    double_down = True
                    break  # Player must stand after doubling down
                else:
                    action = 'Hit'  # Change action to Hit if double down is not possible
                    action_list.append('Hit')

            if action == 'Hit' or action == 'Surrender if possible, otherwise hit':
                player_hand.add_card(deck.deal())
                action_list.append('Hit')
                if player_hand.get_value() > 21:
                    return 'Lose', action_list

            action = self.find_action(player_hand, dealer_up)

        if action == 'Stand' or action == 'Surrender if possible, otherwise stand':
            action_list.append('Stand')
        # Dealer plays their hand
        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal())

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return 'Lose', action_list
        elif dealer_total > 21 or player_total > dealer_total:
            self.money += self.bet_amount * 2
            return 'Win', action_list
        elif player_total == dealer_total:
            self.money += self.bet_amount
            return 'Tie', action_list
        elif (dealer_total > 21 or player_total > dealer_total) and double_down:
            self.money += self.bet_amount * 4
            return 'Win', action_list
        elif player_total == 21 and len(player_hand.cards) == 2:
            self.money += self.bet_amount * 2.5
            return 'Blackjack', action_list
        else:
            return 'Lose', action_list


    def get_card_values(self, hand):
        card_values = []
        for card in hand.cards:
            card_name = str(card)
            card_number = card_name.split(' of ')[0]
            if card_number in ['Jack', 'Queen', 'King']:
                card_values.append(10)
            elif card_number == 'Ace':
                card_values.append(11)
            else:
                card_values.append(int(card_number))
        return card_values

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
        initial_money = BasicStrategyWithoutCountingSettings['Initial Money']
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

            total_games = wins + ties + loses
            if total_games > 0:  # Avoid division by zero
                winrate = wins / total_games * 100
            else:
                winrate = 0

            #print(f"Win rate: {winrate}%")
            #print(self.money)
            #winrate = wins / (wins + ties + loses) * 100

            df = pd.DataFrame(results)
            df = self.calculate_roi(df)
            return df

    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'basic_strategy_results')
        output_filename = os.path.join(output_dir, 'basic_strategy_results.xlsx')

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
