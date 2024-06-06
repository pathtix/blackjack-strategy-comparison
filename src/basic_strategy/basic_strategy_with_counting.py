import pandas as pd
import os
import time

from resources.deck import Deck
from resources.hand import Hand
from basic_strategy.basic_strategy import BasicStrategy

from settings import BasicStrategyWithCountingSettings

class CountingStrategy(BasicStrategy):
    def __init__(self):
        super().__init__()
        self.set_simulation_settings()
        self.running_count = 0
        self.true_count = 0
        self.minimum_bet = 100
        self.maximum_bet = 1000

    def set_simulation_settings(self):
        self.simulation_amount = BasicStrategyWithCountingSettings['Simulation Amount']
        self.money = BasicStrategyWithCountingSettings['Initial Money']
        self.is_double_allowed = BasicStrategyWithCountingSettings['Doubleing Allowed']
        self.minimum_bet = BasicStrategyWithCountingSettings['Minimum Bet']
        self.maximum_bet = BasicStrategyWithCountingSettings['Maximum Bet']

    def count_card(self, card):
        card_value = card.value
        if card_value in [2, 3, 4, 5, 6]:
            return +1
        elif card_value in [10, 11]:  # 10s and Aces
            return -1
        else:
            return 0

    def update_running_count(self, hand):
        for card in hand.cards:
            self.running_count += self.count_card(card)

    def calculate_true_count(self):
        remaining_decks = len(self.main_deck.cards) / 52.0
        self.true_count = self.running_count / remaining_decks if remaining_decks else 0

    def get_bet_amount(self):
        self.calculate_true_count()
        remaining_decks = len(self.main_deck.cards) / 52.0

        bet_multiplier = max(1, int(self.true_count * min(remaining_decks, 1)))
        bet_amount = self.minimum_bet * bet_multiplier
        bet_amount = min(bet_amount, self.maximum_bet)
        return min(bet_amount, self.money)

    def simulate_game(self, player_hand, dealer_hand, deck):
        self.update_running_count(player_hand)
        self.update_running_count(dealer_hand)

        bet_amount = self.get_bet_amount()
        self.money -= bet_amount

        dealer_up = dealer_hand.cards[0]
        action = self.find_action(player_hand, dealer_up)
        double_down = False
        action_list = []

        while action == 'Hit' or action == 'Double if possible, otherwise hit' or action == 'Surrender if possible, otherwise hit':
            if action == 'Double if possible, otherwise hit':
                if len(player_hand.cards) == 2:  # Typically doubling down is only allowed on the first move
                        action_list.append('Doubled')
                        self.money -= bet_amount
                        player_hand.add_card(deck.deal())
                        double_down = True
                        break  # Player must stand after doubling down
                else:
                    action = 'Hit'
                    action_list.append('Hit')

            if action == 'Hit' or action == 'Surrender if possible, otherwise hit':
                player_hand.add_card(deck.deal())
                action_list.append('Hit')
                if player_hand.get_value() > 21:
                    return 'Lose', action_list

            action = self.find_action(player_hand, dealer_up)

        if action == 'Stand' or action == 'Surrender if possible, otherwise stand':
            action_list.append('Stand')

        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal())

        self.update_running_count(dealer_hand)

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return 'Lose', action_list
        elif dealer_total > 21 or player_total > dealer_total:
            self.money += bet_amount * 2
            return 'Win', action_list
        elif player_total == dealer_total:
            self.money += bet_amount
            return 'Tie', action_list
        elif double_down and player_total < dealer_total:
            self.money += bet_amount * 4
            return 'Win', action_list
        elif player_total == 21 and len(player_hand.cards) == 2:
            self.money += self.bet_amount * 2.5
            return 'Blackjack', action_list
        else:
            self.money -= bet_amount
            return 'Lose', action_list

    def simulate(self):
        results = []
        wins = 0
        ties = 0
        loses = 0

        self.running_count = 0
        self.true_count = 0
        self.shuffle_deck()

        while len(self.main_deck.cards) >= 20 and self.money >= self.minimum_bet:
            player_hand = Hand()
            dealer_hand = Hand()

            player_hand.add_card(self.main_deck.deal())
            player_hand.add_card(self.main_deck.deal())

            dealer_hand.add_card(self.main_deck.deal())

            result = self.simulate_game(player_hand, dealer_hand, self.main_deck)

            if result[0] == 'Win':
                wins += 1
            elif result[0] == 'Tie':
                ties += 1
            else:
                loses += 1

            results.append({
                'Player Hand': str(player_hand.cards),
                'Player Hand Value': player_hand.get_value(),
                'Dealer Hand': str(dealer_hand.cards),
                'Dealer Hand Value': dealer_hand.get_value(),
                'Result': result[0],
                'Action': result[1] if len(result) > 1 else None,
                'Running Count': self.running_count,
                'True Count': self.true_count,
                'Money': self.money
            })

        total_games = wins + ties + loses
        if total_games > 0:
            winrate = wins / total_games * 100
        else:
            winrate = 0

        df = pd.DataFrame(results)
        df = self.calculate_roi(df)
        return df
    
    def calculate_roi(self, df):
        initial_money = BasicStrategyWithCountingSettings['Initial Money']
        df['Net Profit'] = df['Money'] - initial_money
        df['Total Invested'] = df['Money'].apply(lambda x: x if x < 0 else initial_money)
        df['ROI'] = (df['Net Profit'] / df['Total Invested']) * 100
        return df


    def output_results(self):
            script_dir = os.path.dirname(os.path.realpath(__file__))
            output_dir = os.path.join(script_dir, 'counting_strategy_results')
            output_filename = os.path.join(output_dir, 'counting_strategy_results.xlsx')

            os.makedirs(output_dir, exist_ok=True)
            self.set_simulation_settings()
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
