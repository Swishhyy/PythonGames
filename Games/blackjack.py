import random

# Card and Deck classes
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Ace can also be 1, handled in game logic
        else:
            return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        self._balanced_shuffle()

    def _balanced_shuffle(self):
        # Shuffle with reduced chances for high cards in the initial deal
        high_cards = [card for card in self.cards if card.rank in ['10', 'J', 'Q', 'K', 'A']]
        low_cards = [card for card in self.cards if card.rank not in ['10', 'J', 'Q', 'K', 'A']]
        random.shuffle(low_cards)
        random.shuffle(high_cards)
        self.cards = low_cards[:30] + high_cards[:22] + low_cards[30:] + high_cards[22:]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()


# Player class
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)

    def hand_value(self):
        value = sum(card.value() for card in self.hand)
        # Adjust for Aces
        aces = sum(1 for card in self.hand if card.rank == 'A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def __str__(self):
        return f"{self.name}'s hand: {', '.join(str(card) for card in self.hand)}"


# Game logic
def play_blackjack():
    print("Welcome to Blackjack!")

    # Initialize deck and players
    deck = Deck()
    player = Player("Player")
    dealer = Player("Dealer")

    # Initial deal
    for _ in range(2):
        player.add_card(deck.draw())
        dealer.add_card(deck.draw())

    # Player's turn
    while True:
        print(player)
        print(f"Hand value: {player.hand_value()}")
        if player.hand_value() > 21:
            print("Bust! You lose.")
            return
        move = input("Hit or Stand? ").lower()
        if move == 'hit':
            player.add_card(deck.draw())
        elif move == 'stand':
            break

    # Dealer's turn
    while dealer.hand_value() < 17:
        dealer.add_card(deck.draw())

    # Results
    print(dealer)
    print(f"Dealer's hand value: {dealer.hand_value()}")
    if dealer.hand_value() > 21 or player.hand_value() > dealer.hand_value():
        print("You win!")
    elif player.hand_value() < dealer.hand_value():
        print("You lose!")
    else:
        print("It's a tie!")


if __name__ == "__main__":
    play_blackjack()
