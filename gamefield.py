from carddeck import Carddeck
from player import Player

import numpy as np
import random

random.seed(42)


class GameField:
    def __init__(self, length: int, height: int, players: list, carddeck):
        self.length = length
        self.height = height
        self.field_temp = []
        self.field_visible = []
        self.star_string = "\u2666"

        self.player_list = players

        self.carddeck = carddeck

        for player in players:
            start_array = np.array(["*" for _ in range(height * length)]).reshape((height, length))
            self.field_visible.append({player.name: start_array})

        # create a numpy array for every player; a temporary list is needed to store the arrays
        for player in players:
            numpy_array_player_cards = np.array(player.cards).reshape((height, length))
            self.field_temp.append({player.name: numpy_array_player_cards})

        self.field_hidden = self.make_field_hidden(self.field_temp, players)

        self.sum_player = self.calculate_sum_player(players, self.carddeck.value_string_mapping())

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

    def calculate_sum_player(self, players: list, card_value_mapping: dict):
        sum_player_dict = {}
        for player in players:
            player_carddeck = player.carddeck_player
            for dic in self.field_hidden:
                for name, tup in dic.items():
                    sum_player = 0
                    for entry in tup:
                        if entry[2]:
                            sum_player += card_value_mapping[str(entry[0])]
                        else:
                            sum_player += 0
                    sum_player_dict[name] = sum_player

        def check_stars_in_line():
            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]
                    columns_values = list(zip(*rows_values))

                    values_flipped = [entry[2] for entry in array]
                    rows_values_flipped = [values_flipped[i:i + self.length] for i in
                                           range(0, len(values_flipped), self.length)]
                    columns_values_flipped = list(zip(*rows_values_flipped))

                    for row, flip in zip(rows_values, rows_values_flipped):
                        if row.count(self.star_string) == self.length and all(flip):
                            sum_player_dict[name] -= 15

                    for column, flip in zip(columns_values, columns_values_flipped):
                        if column.count(self.star_string) == self.height and all(flip):
                            sum_player_dict[name] -= 10

        check_stars_in_line()

        return sum_player_dict

    def flip_card_on_field(self, player: Player, position: tuple):
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
            print(f"Card already flipped at position {position} or invalid input!")
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
                                card_on_field = entry[0]
                                entry[0] = player.card_on_hand
                                player.card_on_hand = None

                                try:
                                    player.card_on_hand = eval(card_on_field)
                                except Exception:
                                    player.card_on_hand = card_on_field

                                entry[2] = True
                                return True

    def check_full_line(self):
        def count_elements(row):
            counts = {}
            for element in row:
                if element in counts:
                    counts[element] += 1
                else:
                    counts[element] = 1
            return counts

        def check_rows_first():
            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]

                    # Set values of row to 0 if all values are the same
                    for i, row in enumerate(rows_values):
                        row_counts = count_elements(row)
                        if "-" in list(row_counts.keys()):
                            count_deleted = row_counts["-"]
                        else:
                            count_deleted = 0

                        for key, value in row_counts.items():
                            if value == 3 and count_deleted == 1 or value == 4 and key != self.star_string:
                                for entry in array:
                                    if entry[1][0] == i and entry[0] != self.star_string:
                                        entry[0] = "-"
                                        entry[2] = True

            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]
                    columns_values = list(zip(*rows_values))

                    # Set column values to 0 if all values are the same
                    for i, column in enumerate(columns_values):
                        column_counts = count_elements(column)

                        for key, value in column_counts.items():
                            if value == 3 and key != self.star_string:
                                for entry in array:
                                    if entry[1][1] == i and entry[0] != self.star_string:
                                        entry[0] = "-"
                                        entry[2] = True

        def check_columns_first():
            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]
                    columns_values = list(zip(*rows_values))

                    # Set column values to 0 if all values are the same
                    for i, column in enumerate(columns_values):
                        column_counts = count_elements(column)

                        for key, value in column_counts.items():
                            if value == 3 and key != self.star_string:
                                for entry in array:
                                    if entry[1][1] == i and entry[0] != self.star_string:
                                        entry[0] = "-"
                                        entry[2] = True

            for dic in self.field_hidden:
                for name, array in dic.items():
                    values = [entry[0] for entry in array]
                    rows_values = [values[i:i + self.length] for i in range(0, len(values), self.length)]

                    # Set values of row to 0 if all values are the same
                    for i, row in enumerate(rows_values):
                        row_counts = count_elements(row)
                        if "-" in list(row_counts.keys()):
                            count_deleted = row_counts["-"]
                        else:
                            count_deleted = 0

                        for key, value in row_counts.items():
                            if value == 3 and count_deleted == 1 or value == 4 and key != self.star_string:
                                for entry in array:
                                    if entry[1][0] == i and entry[0] != self.star_string:
                                        entry[0] = "-"
                                        entry[2] = True

        check_rows_first()
        # check_columns_first()
        # check_rows_first()
        # check_columns_first()

    def _set_values(self, player, position: tuple, value):
        for dic in self.field_hidden:
            for name, array in dic.items():
                if name == player.name:
                    for entry in array:
                        if entry[1] == position:
                            entry[0] = value
                            entry[2] = True

        self.check_full_line()

    def check_end(self):
        for dic in self.field_hidden:
            for name, array in dic.items():
                check_end_list = []
                for entry in array:
                    check_end_list.append(entry[2])
                if all(check_end_list):
                    return True, name
        return False, None

    def __str__(self):
        self.check_full_line()
        sum_player = self.calculate_sum_player(self.player_list, self.carddeck.value_string_mapping())

        string = f"\nDiscard stack: {self.carddeck.discard_stack}\n"
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
                string += "-------------------\n"
        return string


if __name__ == "__main__":
    C = Carddeck()

    S = Player("Sven", C, (4, 3))
    A = Player("Anna", C, (4, 3))

    G = GameField(4, 3, [S, A], C)
    star = G.star_string

    G._set_values(A, (0, 0), star)
    G._set_values(A, (0, 1), star)
    G._set_values(A, (0, 2), star)

    G.flip_card_on_field(A, (0, 3))

    print(G.field_hidden)
