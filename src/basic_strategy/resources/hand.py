class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        aces = 0

        for card in self.cards:
            if card.value > 10:  # Jack, Queen, King
                value += 10
            elif card.value == 1:  # Ace
                value += 11
                aces += 1
            else:
                value += card.value

        # Adjust the value of aces from 11 to 1 as necessary
        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value