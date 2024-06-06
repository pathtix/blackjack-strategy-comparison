import numpy as np
import random
import pickle

from resources.deck import Deck
from resources.hand import Hand

from settings import RLSettings

# Define the Blackjack Environment
class BlackjackEnv:
    def __init__(self, alpha, gamma, epsilon, num_episodes):
        self.action_space = [0, 1, 2]  # 0: Stand, 1: Hit, 2: Double
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.num_episodes = num_episodes
        self.q_table = {}
        self.reset()

    def reset(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.player_hand = Hand()
        self.dealer_hand = Hand()

        # Deal initial cards
        self.player_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())

        self.dealer_hand.add_card(self.deck.deal())
        self.dealer_showing = self.dealer_hand.cards[0]

        dealer_up_value = self.dealer_showing.value
        if dealer_up_value > 10:
            dealer_up_value = 10  # Convert J, Q, K to 10
        elif dealer_up_value == 1:
            dealer_up_value = 11  # Represent Ace as 11

        return (self.player_hand.get_value(), dealer_up_value)

    def fill_q_table(self):
        for i in range(4, 32):
            for j in range(2, 12):
                state = (i, j)
                self.q_table[state] = [0, 0, 0]

        # Add states for dealer's Ace represented as 11
        for i in range(4, 32):
            state = (i, 11)
            self.q_table[state] = [0, 0, 0]

    def step(self, action):
        if action == 1:  # Hit
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.get_value() > 21:
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), -1, True, {}  # Player bust
            else:
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), 0, False, {}
        elif action == 2:  # Double
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.get_value() > 21:
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), -2, True, {}  # Player bust with double loss
            else:
                while self.dealer_hand.get_value() < 17:
                    self.dealer_hand.add_card(self.deck.deal())
                if self.dealer_hand.get_value() > 21 or self.player_hand.get_value() > self.dealer_hand.get_value():
                    return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), 2, True, {}  # Double win
                elif self.player_hand.get_value() == self.dealer_hand.get_value():
                    return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), 0, True, {}  # Draw
                else:
                    return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), -2, True, {}  # Double loss
        else:  # Stand
            while self.dealer_hand.get_value() < 17:
                self.dealer_hand.add_card(self.deck.deal())
            if self.dealer_hand.get_value() > 21 or self.player_hand.get_value() > self.dealer_hand.get_value():
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), 1, True, {}  # Win
            elif self.player_hand.get_value() == self.dealer_hand.get_value():
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), 0, True, {}  # Draw
            else:
                return (self.player_hand.get_value(), min(self.dealer_showing.value, 10)), -1, True, {}  # Lose

    def train_model(self):
        for _ in range(self.num_episodes):
            state = self.reset()
            done = False
            while not done:
                if random.uniform(0, 1) < self.epsilon:
                    action = random.choice(self.action_space)
                else:
                    action = np.argmax(self.q_table[state])

                next_state, reward, done, _ = self.step(action)

                if next_state not in self.q_table:
                    self.q_table[next_state] = [0, 0, 0]

                self.q_table[state][action] = self.q_table[state][action] + self.alpha * (reward + self.gamma * max(self.q_table[next_state]) - self.q_table[state][action])
                state = next_state

    def save_q_table(self):
        with open(RLSettings["Q Table Path"], 'wb') as f:
            pickle.dump(self.q_table, f)

if __name__ == '__main__':
    env = BlackjackEnv(0.1, 0.9, 0.1, 1000)
    env.fill_q_table()
    env.train_model()
    env.save_q_table()
    print("Q-Table saved!")
