import pandas as pd
import os
import ast
import time

from resources.deck import Deck
from resources.hand import Hand

from settings import HistoricalDataSettings

class HistoricalData:
    def __init__(self):
        self.df = None
        self.create_deck()
        self.simulation_amount = 10

    def set_simulation_amount(self):
        self.simulation_amount = HistoricalDataSettings['Simulation Amount']

    def shuffle_deck(self):
        self.main_deck.shuffle()
    
    def create_deck(self):
        self.deck_1 = Deck()
        self.deck_2 = Deck()

        self.main_deck = Deck()
        self.main_deck.cards = self.deck_1.cards + self.deck_2.cards

    def importCSV_async(self):
        self.df = self.importCSV()

    def importCSV(self):
        start_time = time.time()
        print("Importing CSV...")
        chunksize = 100000
        chunks = []
        rows = 0

        cols_to_keep = ['initial_hand', 'dealer_up', 'actions_taken']

        for chunk in pd.read_csv(HistoricalDataSettings['Data Source'], usecols=cols_to_keep, chunksize=chunksize):
            chunks.append(chunk)
            rows += chunk.shape[0]
            
            if rows >= HistoricalDataSettings['Rows']:
                break
        df = pd.concat(chunks, ignore_index=True)
    
        end_time = time.time()
        print(f"Importing CSV took {end_time - start_time} seconds")

        return df
    
    def hand_simplifier(self, hand):
        face_cards = ['King', 'Queen', 'Jack']
        values = []

        for card in hand:
            card = str(card)
            card_name = card.split(' ')[0]  # Get the first word in the card name

            if card_name in face_cards:
                values.append(10)
            elif card_name == 'Ace':
                values.append(11)  # or 11, depending on your game's rules
            else:
                values.append(int(card_name))  # Convert the card name to an integer

        return values
    
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
    
    def find_action(self, player_hand, dealer_up):
        player_hand = self.hand_simplifier(player_hand.cards)
        action = self.check_next_move(str(player_hand), dealer_up.value, self.df)
        return action
    
    def simulate_game(self, player_hand, dealer_hand, deck):
        dealer_up = dealer_hand.cards[0]    
          
        action = self.find_action(player_hand, dealer_up)

        if action is not None:
            action_list_len = len(action)
        else:
            action_list_len = 0

        # TODO: Check the all action types
            
        for i in range(action_list_len):
            if action[i] == 'H':
                player_hand.add_card(deck.deal())
                continue
            elif action[i] == 'D':
                player_hand.add_card(deck.deal())
                continue
            elif action[i] == 'S':
                continue
            else:
                continue
        
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
        self.set_simulation_amount()
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
            'Action Taken' : action
        }
    
    def simulate(self):
            results = []
            wins = 0
            ties = 0
            loses = 0
        
            print("Simulating game...")
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
                'Dealer Hand': ''
            })

            df = pd.DataFrame(results)
            return df

    def output_results(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, 'historical_data_results')
        output_filename = os.path.join(output_dir, 'historical_data_results.xlsx')

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
    

if __name__ == "__main__":
    hd = HistoricalData()
    hd.importCSV_async()
    hd.output_results()