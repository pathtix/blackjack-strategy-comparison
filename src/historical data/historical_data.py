import pandas as pd
import os
import ast

from resources.deck import Deck
from resources.hand import Hand

class HistoricalData:
    def __init__(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def shuffle_deck(self):
        self.main_deck.shuffle()

    def importCSV(self):
        chunksize = 5000
        chunks = []
        rows = 0

        for chunk in pd.read_csv("./etc/blackjack_simulator.csv", chunksize=chunksize):
            chunks.append(chunk)
            rows += chunk.shape[0]
            
            if rows >= 500000:
                break
        df = pd.concat(chunks, ignore_index=True)
        return df
    
    def check_next_move(self, inital_hand, dealer_up, df):
        filtered_df = df.loc[(df['initial_hand'] == inital_hand) & (df['dealer_up'] == dealer_up)]        
        if not filtered_df.empty:
            # Convert the actions_taken column to lists
            filtered_df.loc[:, 'actions_taken'] = filtered_df['actions_taken'].apply(ast.literal_eval)

            first_actions = filtered_df['actions_taken'].apply(lambda x: x[0] if x else None)
            action_counts = first_actions.value_counts()

            # Get the action sequence with the highest count
            most_common_action_sequence = action_counts.idxmax()
        else:
            most_common_action_sequence = None

        return most_common_action_sequence
    
    def simulate_game(self, player_hand, dealer_hand, deck):
        dealer_up = dealer_hand.cards[0]

        player_card_value = self.get_card_values(player_hand)
        action = self.check_next_move(str(player_card_value), dealer_up.value, self.importCSV())
        if action is not None:
            action_list_len = len(action)
        else:
            action_list_len = 0

        # TODO: Check the all action types
            
        for i in range(action_list_len):
            if action[i] == 'H':
                player_hand.add_card(deck.deal())
            elif action[i] == 'S':
                continue
            else:
                continue
        
        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal())

        player_total = player_hand.get_value()
        dealer_total = dealer_hand.get_value()

        if player_total > 21:
            return str(action) + 'Lose'
        elif dealer_total > 21 or player_total > dealer_total:
            return str(action) + 'Win'
        elif player_total == dealer_total:
            return str(action) + 'Tie'
        else:
            return str(action) + 'Lose'
        
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
            'Action Taken' : result
        }
    
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

            results.append({
                'Player Hand': '',
                'Dealer Hand': '',
                'Player Total': '',
                'Dealer Total': ''
            })

            df = pd.DataFrame(results)
            return df

    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'historical_data_results')
        output_filename = os.path.join(output_dir, 'historical_data_results.xlsx')

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        df = self.simulate()

        if not os.path.isfile(output_filename):
            pd.DataFrame().to_excel(output_filename)
        
        try:
            with pd.ExcelWriter(output_filename, mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name= "test" + str(i), index=False)
        except Exception as e:
            print(f"An error occurred during simulation {i}: {e}")
    
        
            
    
if __name__ == "__main__":
    for i in range(1):
        HD = HistoricalData()
        HD.output_results()