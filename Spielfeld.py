import random
import numpy as np

# set seed for reproducibility
random.seed(42)


class GameField:
    def __init__(self, length: int, height: int, players: list):
        self.length = length
        self.height = height
        self.field_temp = []
        self.field_hidden = []
        self.field_visible = []
        for player in players:
            start_array = np.array(["*" for _ in range(length * height)]).reshape((length, height))
            self.field_visible.append({player.name: start_array})

        # create a numpy array for every player; a temporary list is needed to store the arrays
        for player in players:
            numpy_array_player_cards = np.array(player.cards).reshape((length, height))
            self.field_temp.append({player.name: numpy_array_player_cards})

        print(f"Field temp: {self.field_temp}")

        for counter, player in enumerate(self.field_temp):
            field_hidden_dict = {}

            for name, array in player.items():
                # get value and position of every entry in the array
                list_value_position_apparent = []
                for position, value in np.ndenumerate(array):
                    # Bool indicates if card is hidden or visible; at start all cards are hidden
                    list_value_position_apparent.append((value, position, False))
                field_hidden_dict[name] = list_value_position_apparent

            self.field_hidden.append(field_hidden_dict)
            if counter == len(players) - 1:
                break

    def __str__(self):
        string = ""
        for dic in self.field_hidden:
            for name, array in dic.items():
                string += f"{name}:\n"
                for entry in array:
                    if entry[2] == False:
                        string += f"*\t"
                    else:
                        string += f"{entry[0]}"
                    # if more than game_field.length are added, a new line is started
                    if (array.index(entry) + 1) % self.length == 0:
                        string += "\n"
        return string


class Carddeck:
    def __init__(self):
        self.cards = self.init_carddeck()
        self.card_value_mapping = self.value_string_mapping()

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
        star_string = "\u2666"
        mapping[star_string] = 0
        return mapping


class Player:
    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        if type(name) == str:
            self.name = name
        else:
            raise TypeError("Name must be a string")

        self.cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])


if __name__ == "__main__":
    C = Carddeck()

    S = Player("Sven", C, (4, 3))
    A = Player("Anna", C, (4, 3))

    G = GameField(4, 3, [S, A])
