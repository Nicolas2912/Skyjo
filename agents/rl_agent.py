from Game.carddeck import Carddeck

import random

class RLAgent(Carddeck):

    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        super().__init__()
        self.name = name

        self.player_cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])

        self.card_on_hand = None

    def flip_cards_start(self, positions: list, output: bool = True):
        pos1 = positions[0]
        pos2 = positions[1]

        if output:
            print(f"Agent {self.name} flipped cards at position {pos1} and {pos2}")

        return pos1, pos2

    def flip_card(self, position: tuple, output: bool = True):
        if output:
            print(f"Agent {self.name} flipped card at position {position}")
        return position

    def choose_position(self, position: tuple, output: bool = True):
        if output:
            print(f"Agent {self.name} chose position {position}")
        return position

    def pull_card_from_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                self.card_on_hand = carddeck.discard_stack.pop()
                if output:
                    print(f"Agent {self.name} pulled card {self.card_on_hand} from discard stack!")
            else:
                raise ValueError("Agent already has a card on hand! Cannot have more than one card on hand!")
        else:
            raise ValueError("Discard stack is empty! Cannot pull card from empty discard stack!")

    def put_card_on_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if self.card_on_hand is not None:
            carddeck.discard_stack.append(self.card_on_hand)
            self.card_on_hand = None
            if output:
                print(f"Agent {self.name} put card on discard stack!")
        else:
            raise ValueError("Agent has no card on hand! Cannot put card on discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck, output: bool = True):
        try:
            card_on_hand = carddeck.cards[0]
        except Exception as e:
            print(carddeck.cards)
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        if output:
            print(f"Agent {self.name} pulled card {self.card_on_hand} from deck!")
        return card_on_hand


