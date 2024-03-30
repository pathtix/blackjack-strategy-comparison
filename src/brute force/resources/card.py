class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        
        if self.value == 11:
            self.name = "Jack"
        elif self.value == 12:
            self.name = "Queen"
        elif self.value == 13:
            self.name = "King"
        else:
            self.name = str(self.value)

    def __repr__(self):
        return f"{self.name} of {self.suit}"
