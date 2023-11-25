from Game.carddeck import Carddeck
# from seed import random_seed

import random, time


# random.seed(time.process_time())


class Player(Carddeck):
    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        super().__init__()
        if type(name) == str:
            self.name = name
        else:
            raise TypeError("Name must be a string")

        self.player_cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])

        for card in self.player_cards:
            carddeck.cards.remove(card)

        self.card_on_hand = None

    def flip_card(self, position: tuple):
        return position

    def pull_card_from_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                self.card_on_hand = carddeck.discard_stack.pop()
                if output:
                    print(f"Player {self.name} pulled card {self.card_on_hand} from discard stack!")
            else:
                raise ValueError("Player already has a card on hand! Cannot have more than one card on hand!")
        else:
            raise ValueError("Discard stack is empty! Cannot pull card from empty discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck, output: bool = True):
        try:
            card_on_hand = carddeck.cards[0]
        except Exception as e:
            print(carddeck.cards)
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        if output:
            print(f"Player {self.name} pulled card {self.card_on_hand} from deck!")
        return card_on_hand

    def put_card_on_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if self.card_on_hand is not None:
            carddeck.discard_stack.append(self.card_on_hand)
            self.card_on_hand = None
            if output:
                print(f"Player {self.name} put card on discard stack!")
        else:
            raise ValueError("Player has no card on hand! Cannot put card on discard stack!")

    def __str__(self):
        return f"Name: {self.name}\nCards: {self.cards}\nCard on hand: {self.card_on_hand}\n"


if __name__ == "__main__":
    c = Carddeck()
    print("len of all cards: ")
    print(len(c.cards))
    p = Player("Test", c, (4, 3))
    #p1 = Player("Test1", c, (4, 3))
    #p2 = Player("Test2", c, (4, 3))
    print(p.player_cards)
    print(len(c.cards))

