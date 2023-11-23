# from seed import random_seed

import random, time

# random.seed(time.process_time())




class Carddeck:
    def __init__(self):
        self.cards = self.init_carddeck()
        self.card_value_mapping = self.value_string_mapping()
        self.discard_stack = [self.cards.pop(0)]

        print(f"Carddeck random seed: {random.getstate()}")

    def init_carddeck(self):
        cards = [card for card in range(-1, 13) for _ in range(7) if card != 0]
        cards.extend([-2 for _ in range(3)])
        cards.extend([0 for _ in range(11)])
        star_string = "\u2666"
        cards.extend([star_string for _ in range(15)])
        random.shuffle(cards)

        return cards

    def value_string_mapping(self):
        cards = list(set(self.cards))
        mapping = {str(card): card for card in cards}

        # add star
        star_string = "\u2666"
        mapping[star_string] = 0

        # add special character that represents a row/column that is deleted (when a row/column is full with same values)
        mapping["-"] = 0

        return mapping


if __name__ == "__main__":
    c = Carddeck()
    print(c.cards)
