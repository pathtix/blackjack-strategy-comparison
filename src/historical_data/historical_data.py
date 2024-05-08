import pandas as pd
import os
import ast
import time

from resources.deck import Deck
from resources.hand import Hand

from settings import HistoricalDataSettings

from basic_strategy.basic_strategy import BasicStrategy

#TODO : Fix the issue with action taken list is missing if basic strategy is used !!

class HistoricalData:
    def __init__(self):
        self.df = None
        self.create_deck()
        self.simulation_amount = 10
        self.doublingAllowed = HistoricalDataSettings['Doubleing Allowed']
        
        self.money = 1000
        self.usedBasicStrategy = False

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
        df.set_index(['initial_hand', 'dealer_up'], inplace=True)  # Set multi-index on columns used in queries
        
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
        else: # Apply basic strategy if no data is found
            self.usedBasicStrategy = True
            basic_strategy = BasicStrategy()
            list = ast.literal_eval(inital_hand)
            player_hand_value = sum(list)
            action = basic_strategy.check_basicstrategy(player_hand_value,dealer_up)

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
        
        action = self.check_next_move(str(player_hand_simplified), dealer_up.value, self.df)
        return action
    
    def simulate_game(self, player_hand, dealer_hand, deck):
        action = self.find_action(player_hand, dealer_hand.cards[0])
        action_list_len = len(action) if action else 0
        
        for i in range(action_list_len):
            if action[i] == 'H':
                player_hand.add_card(deck.deal())
            elif action[i] == 'D':
                if self.doublingAllowed:
                    player_hand.add_card(deck.deal())
                break
            elif action[i] == 'S':
                break


        if self.usedBasicStrategy:
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
                            recent_action = None
                            continue
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
    
    def simulate(self):
            results = []
            wins, ties, loses = 0, 0, 0
        
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
    hd.set_simulation_amount()
    hd.importCSV_async()
    hd.output_results()