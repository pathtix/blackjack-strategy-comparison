import pandas as pd
import os
import ast
import time
import sqlite3

from resources.deck import Deck
from resources.hand import Hand

from settings import HistoricalDataSettings

from basic_strategy.basic_strategy import BasicStrategy


class HistoricalData:
    def __init__(self):
        self.create_deck()
        self.df = None
        self.used_basic_strategy = False
        self.db_conn = None
        self.money = None

        self.set_simulation_settings()

    def set_simulation_settings(self):
        self.simulation_amount = HistoricalDataSettings['Simulation Amount']
        self.doublingAllowed = HistoricalDataSettings['Doubleing Allowed']
        self.pathToDB = HistoricalDataSettings['Database Path']
        self.initial_money = HistoricalDataSettings['Initial Money']
        self.bet_amount = HistoricalDataSettings['Bet Amount']

    def shuffle_deck(self):
        self.main_deck.shuffle()

    def create_deck(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def hand_simplifier(self, hand):
        face_cards = ['King', 'Queen', 'Jack']
        values = []

        for card in hand:
            card = str(card)
            card_name = card.split(' ')[0]

            if card_name in face_cards:
                values.append(10)
            elif card_name == 'Ace':
                values.append(11)
            else:
                values.append(int(card_name))

        return values

    def check_next_move(self, key):
        query = f"SELECT actions_taken FROM historical_data WHERE initial_hand = ? AND dealer_up = ? LIMIT 1"
        cursor = self.db_conn.cursor()
        cursor.execute(query, (key[0], key[1]))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            self.used_basic_strategy = True
            basic_strategy = BasicStrategy()
            list = ast.literal_eval(key[0])
            player_hand_value = sum(list)
            action = basic_strategy.check_basicstrategy(player_hand_value,key[1])

            if action == 'Hit':
                most_common_action_sequence = ['H']
            elif action == 'Stand':
                most_common_action_sequence = ['S']
            elif action == 'Double if possible, otherwise hit':
                if self.doublingAllowed:
                    most_common_action_sequence = ['D']
                else:
                    most_common_action_sequence = ['H']
            elif action == 'Surrender if possible, otherwise hit':
                most_common_action_sequence = ['H']
            elif action == 'Surrender if possible, otherwise stand':
                most_common_action_sequence = ['S']
            else:
                most_common_action_sequence = None
        return most_common_action_sequence

    def find_action(self, player_hand, dealer_up):
        player_hand_simplified = self.hand_simplifier(player_hand.cards)
        if player_hand.get_value() > 21:
            return None

        key = (str(player_hand_simplified), dealer_up.value)
        action = self.check_next_move(key)
        return action

    def simulate_game(self, player_hand, dealer_hand, deck):
        action = self.find_action(player_hand, dealer_hand.cards[0])
        action_list_len = len(action) if action else 0
        double_down = False

        for i in range(action_list_len):
            if action[i] == 'H':
                player_hand.add_card(deck.deal())
                continue
            elif action[i] == 'D':
                if self.doublingAllowed:
                    player_hand.add_card(deck.deal())
                    double_down = True
                    self.money -= self.bet_amount
                    break
            elif action[i] == 'S':
                break

        if self.used_basic_strategy:
            recent_action = action
            while recent_action != None:
                new_action = self.find_action(player_hand, dealer_hand.cards[0])

                if new_action != None:
                    for i in range(len(new_action)):
                        if new_action[i] == 'H':
                            player_hand.add_card(deck.deal())
                            recent_action = new_action
                            continue
                        elif new_action[i] == 'D':
                            player_hand.add_card(deck.deal())
                            double_down = True
                            self.money -= self.bet_amount
                            break
                        elif new_action[i] == 'S':
                            recent_action = None
                        else: # surrender etc.
                            recent_action = None
                else:
                    recent_action = None

        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal())

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return 'Lose'
        elif dealer_total > 21 or player_total > dealer_total:
            self.money += self.bet_amount * 2
            return 'Win'
        elif (dealer_total > 21 or player_total > dealer_total) and double_down:
            self.money += self.bet_amount * 4
            return 'Win'
        elif player_total == 21 and len(player_hand.cards) == 2:
            self.money += self.bet_amount * 2.5
            return 'Blackjack'
        elif player_total == dealer_total:
            self.money += self.bet_amount
            return 'Tie'
        else:
            return 'Lose'

    def bj_simulation(self, deck):
        self.money -= self.bet_amount
        player_hand = Hand()
        dealer_hand = Hand()

        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())

        dealer_hand.add_card(deck.deal())

        action = self.find_action(player_hand, dealer_hand.cards[0])

        result = self.simulate_game(player_hand, dealer_hand, deck)

        return {
            'Player Hand': str(player_hand.cards),
            'Player Hand Value': player_hand.get_value(),
            'Dealer Hand': str(dealer_hand.cards),
            'Dealer Hand Value': dealer_hand.get_value(),
            'Result': result,
            'Action Taken' : action,
            'Money': self.money
        }
    
    def calculate_roi(self, df):
        initial_money = HistoricalDataSettings['Initial Money']
        df['Net Profit'] = df['Money'] - initial_money
        df['Total Invested'] = df['Money'].apply(lambda x: x if x < 0 else initial_money)
        df['ROI'] = (df['Net Profit'] / df['Total Invested']) * 100
        return df

    def simulate(self):
            results = []
            wins, ties, loses = 0, 0, 0

            self.shuffle_deck()
            self.money = self.initial_money
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
        self.set_simulation_settings()
        if not self.db_conn:
            try:
                self.db_conn = sqlite3.connect(self.pathToDB, check_same_thread=False)
            except Exception as e:
                print(f"An error occurred while connecting to the database: {e}")
                return

        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'historical_data_results')
        output_filename = os.path.join(output_dir, 'historical_data_results.xlsx')

        os.makedirs(output_dir, exist_ok=True)
        all_results = []
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
