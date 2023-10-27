import random
import numpy as np

# set seed for reproducibility
random.seed(42)


class GameField:
    def __init__(self, length: int, height: int, players: list):
        self.length = length
        self.height = height
        self.field_temp = []
        self.field_visible = []
        self.star_string = "\u2666"

        self.player_list = players

        for player in players:
            start_array = np.array(["*" for _ in range(height * length)]).reshape((height, length))
            self.field_visible.append({player.name: start_array})

        # create a numpy array for every player; a temporary list is needed to store the arrays
        for player in players:
            numpy_array_player_cards = np.array(player.cards).reshape((height, length))
            self.field_temp.append({player.name: numpy_array_player_cards})

        self.field_hidden = self.make_field_hidden(self.field_temp, players)

        self.sum_player = self.calculate_sum_player(players)

    def make_field_hidden(self, field_temp, players):
        field_hidden = []
        for counter, player in enumerate(field_temp):
            field_hidden_dict = {}

            for name, array in player.items():
                # get value and position of every entry in the array
                list_value_position_apparent = []
                for position, value in np.ndenumerate(array):
                    # Bool indicates if card is hidden or visible; at start all cards are hidden
                    list_value_position_apparent.append([value, position, False])
                field_hidden_dict[name] = list_value_position_apparent

            field_hidden.append(field_hidden_dict)
            if counter == len(players) - 1:
                break

        return field_hidden

    def calculate_sum_player(self, players: list):
        sum_player_dict = {}
        for player in players:
            player_carddeck = player.carddeck_player
            for dic in self.field_hidden:
                for name, tup in dic.items():
                    sum_player = 0
                    for entry in tup:
                        if entry[2]:
                            sum_player += player_carddeck.card_value_mapping[str(entry[0])]
                        else:
                            sum_player += 0
                    sum_player_dict[name] = sum_player

        def check_stars_in_line():
            rows_values = []
            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]
                    columns_values = list(zip(*rows_values))

                    for row in rows_values:
                        if row.count(self.star_string) == self.length:
                            sum_player_dict[name] -= 15

                    for column in columns_values:
                        if column.count(self.star_string) == self.height:
                            sum_player_dict[name] -= 10

        check_stars_in_line()

        return sum_player_dict

    def flip_card_on_field(self, player, position: tuple):
        def flip_card_on_field_helper(player, position: tuple):
            for dic in self.field_hidden:
                for name, array in dic.items():
                    if name == player.name:
                        for entry in array:
                            if entry[1] == position:
                                if not entry[2]:
                                    entry[2] = True
                                    return True
                                else:
                                    return False

        flipped = flip_card_on_field_helper(player, position)

        if flipped:
            print(f"Card flipped at position {position}")

        while not flipped:
            print(f"Card already flipped at position {position}!")
            new_position = input(f"Enter new position: (x,y):")
            new_position = eval(new_position)
            flipped = flip_card_on_field_helper(player, new_position)

    def change_card_with_card_on_hand(self, player, position: tuple):
        if player.card_on_hand is None:
            print("No card on hand!")
            return False
        else:
            for dic in self.field_hidden:
                for name, array in dic.items():
                    if name == player.name:
                        for entry in array:
                            if entry[1] == position:
                                if entry[2]:
                                    entry[0] = player.card_on_hand
                                    player.card_on_hand = None
                                    return True
                                else:
                                    entry[0] = player.card_on_hand
                                    player.card_on_hand = None
                                    entry[2] = True
                                    return True

    def check_full_line(self):
        for dic in self.field_hidden:
            for name, array in dic.items():

                values = [entry[0] for entry in array]
                rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]

                # Set values of row to 0 if all values are the same
                for i, row in enumerate(rows_values):
                    if all(element == row[0] for element in row if element != "-"):
                        print("in row")
                        for entry in array:
                            if entry[1][0] == i and entry[0] != self.star_string:
                                entry[0] = "-"
                                entry[2] = True

                columns_values = list(zip(*rows_values))

                # Set column values to 0 if all values are the same
                for i, column in enumerate(columns_values):
                    if all(element == column[0] for element in column if element != "-"):
                        for entry in array:
                            if entry[1][1] == i and entry[0] != self.star_string:
                                entry[0] = "-"
                                entry[2] = True

        for dic in self.field_hidden:
            for name, array in dic.items():
                values = [entry[0] for entry in array]
                rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]
                columns_values = list(zip(*rows_values))

                # Set values of row to 0 if all values are the same
                for i, row in enumerate(rows_values):
                    # TODO: Problem with row[0]. It must be indepent of the first element in the row
                    if all(element == row[0] for element in row if element != "-"):
                        for entry in array:
                            if entry[1][0] == i and entry[0] != self.star_string:
                                entry[0] = "-"
                                entry[2] = True

                # Set column values to 0 if all values are the same
                for i, column in enumerate(columns_values):
                    if all(element == column[0] for element in column if element != "-"):
                        for entry in array:
                            if entry[1][1] == i and entry[0] != self.star_string:
                                entry[0] = "-"
                                entry[2] = True
    def _set_values(self, player, position: tuple, value):
        for dic in self.field_hidden:
            for name, array in dic.items():
                if name == player.name:
                    for entry in array:
                        if entry[1] == position:
                            entry[0] = value
                            entry[2] = True

    def __str__(self):
        self.check_full_line()
        sum_player = self.calculate_sum_player(self.player_list)

        string = ""
        for dic in self.field_hidden:
            for name, array in dic.items():
                string += f"Name: {name}; Sum: {sum_player[name]}\n"
                for entry in array:
                    if not entry[2]:
                        string += f"*\t"
                    else:
                        string += f"{entry[0]}\t"
                    # if more than game_field.length are added, a new line is started
                    if (array.index(entry) + 1) % self.length == 0:
                        string += "\n"
                string += "----------------\n"
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

        # add star
        star_string = "\u2666"
        mapping[star_string] = 0

        # add special character that represents a row/column that is deleted (when a row/column is full with same values)
        mapping["-"] = 0

        return mapping


class Player:
    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        if type(name) == str:
            self.name = name
        else:
            raise TypeError("Name must be a string")

        self.cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])
        self.carddeck_player = Carddeck()
        self.card_on_hand = None

    def flip_card(self, position: tuple):
        return position

    def pull_card_from_deck(self, carddeck: Carddeck):
        card_on_hand = carddeck.cards[0]
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        return card_on_hand


if __name__ == "__main__":
    C = Carddeck()

    S = Player("Sven", C, (4, 3))
    A = Player("Anna", C, (4, 3))

    G = GameField(4, 3, [S, A])
    star = G.star_string


    G._set_values(S, (0, 0), 1)
    G._set_values(S, (1, 0), 1)
    G._set_values(S, (2, 0), 1)

    G._set_values(S, (0, 1), 3)
    G._set_values(S, (0, 2), 3)
    G._set_values(S, (0, 3), 3)

    print(G.field_hidden)

    print(G)
