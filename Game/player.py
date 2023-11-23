from Game.carddeck import Carddeck
# from seed import random_seed

import random, time

# random.seed(time.process_time())



class Player:
    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        if type(name) == str:
            self.name = name
        else:
            raise TypeError("Name must be a string")

        self.cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])
        self.card_on_hand = None

        self.last_turn = False


    def flip_card(self, position: tuple):
        return position

    def pull_card_from_discard_stack(self, carddeck: Carddeck):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                self.card_on_hand = carddeck.discard_stack.pop()
            else:
                raise ValueError("Player already has a card on hand! Cannot have more than one card on hand!")
        else:
            raise ValueError("Discard stack is empty! Cannot pull card from empty discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck):
        card_on_hand = carddeck.cards[0]
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        return card_on_hand

    def put_card_on_discard_stack(self, carddeck: Carddeck):
        if self.card_on_hand is not None:
            carddeck.discard_stack.append(self.card_on_hand)
            self.card_on_hand = None
        else:
            raise ValueError("Player has no card on hand! Cannot put card on discard stack!")

    def __str__(self):
        return f"Name: {self.name}\nCards: {self.cards}\nCard on hand: {self.card_on_hand}\n"
