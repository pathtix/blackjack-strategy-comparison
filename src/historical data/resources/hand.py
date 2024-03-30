class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        ace = False
        
        for card in self.cards:
            if card.value > 10: # Jack, Queen, King
                value += 10
            elif card.value == 1: # Ace can be 1 or 11
                value += 11
                ace = True
            else:
                value += card.value
        
        if ace and value > 21:
            value -= 10
        return value