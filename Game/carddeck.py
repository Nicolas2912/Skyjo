# from seed import random_seed
from collections import Counter

import random, time

# random.seed(7)


class Carddeck:
    def __init__(self, seed: int = 7):
        random.seed(seed)
        self.cards = self.init_carddeck()
        self.discard_stack = [self.cards.pop(0)]
        self.all_cards = self.cards + self.discard_stack

        self.card_value_mapping = self.value_string_mapping()

    def init_carddeck(self) -> list:
        cards = [card for card in range(-1, 13) for _ in range(7) if card != 0]
        cards.extend([-2 for _ in range(3)])
        cards.extend([0 for _ in range(11)])
        star_string = "\u2666"
        cards.extend([star_string for _ in range(15)])
        random.shuffle(cards)

        return cards

    def value_string_mapping(self) -> dict:
        cards = list(set(self.all_cards))
        mapping = {str(card): card for card in cards}

        # add star
        star_string = "\u2666"
        mapping[star_string] = 0

        # add special character that represents a row/column that is deleted (when a row/column is full with same values)
        mapping["-"] = 0

        return mapping


if __name__ == "__main__":
    c = Carddeck()
    cards_counter = Counter(c.cards)
    cards_counter = sorted(cards_counter.items(), key=lambda x: x[1], reverse=False)
    print(dict(cards_counter))
    print(len(c.cards))
