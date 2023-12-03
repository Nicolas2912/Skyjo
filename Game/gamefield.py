from Game.carddeck import Carddeck
from Game.player import Player

import numpy as np

from collections import Counter


class GameField:
    def __init__(self, length: int, height: int, players: list, carddeck):
        self.length = length
        self.height = height
        self.field_temp = []
        self.field_visible = []
        self.star_string = "\u2666"

        self.players_list = players

        self.players_dict = {player.name: player for player in players}

        self.carddeck = carddeck

        for player in players:
            start_array = np.array(["*" for _ in range(height * length)]).reshape((height, length))
            self.field_visible.append({player.name: start_array})

        # create a numpy array for every player; a temporary list is needed to store the arrays
        for player in players:
            numpy_array_player_cards = np.array(player.player_cards).reshape((height, length))
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
        for _ in players:
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

    def flip_card_on_field(self, player, position: tuple, output: bool = True):
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

        self.check_full_line()
        flipped = flip_card_on_field_helper(player, position)
        if output:
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

                                if card_on_field == self.star_string:
                                    player.card_on_hand = card_on_field
                                elif isinstance(card_on_field, int):
                                    player.card_on_hand = card_on_field
                                elif isinstance(card_on_field,
                                                str) and card_on_field != self.star_string and card_on_field != "-":
                                    player.card_on_hand = int(card_on_field)
                                elif isinstance(card_on_field, np.int32):
                                    player.card_on_hand = card_on_field.astype(int)

                                entry[2] = True

        self.check_full_line()

    def check_full_line(self):

        def check_consecutive(lst, n):
            for i in range(len(lst) - n + 1):
                if len(set(lst[i:i + n])) == 1:
                    return True
            return False

        # check if all cards in a column are the same (height = 3 / column)
        for dic in self.field_hidden:
            for name, field in dic.items():

                field_transposed = sorted(field, key=lambda x: x[1][1])

                for column in field_transposed:
                    column_values = [entry[0] for entry in field if entry[1][1] == column[1][1] and entry[2]]

                    column_counts = Counter(column_values)
                    column_counts_dict = dict(column_counts)

                    if len(column_counts_dict.values()) == 1 and list(column_counts_dict.values())[
                        0] == self.height and self.star_string not in list(column_counts_dict.keys()):
                        for entry in field:
                            if entry[1][1] == column[1][1] and entry[2]:
                                entry[0] = "-"

        # check if all cards in a row are the same (length = 4 / row)
        for dic in self.field_hidden:
            for name, field in dic.items():
                for row in field:
                    row_values = [entry[0] for entry in field if entry[1][0] == row[1][0] and entry[2]]
                    row_counts = Counter(row_values)
                    row_counts_dict = dict(row_counts)

                    already_set = False
                    if not already_set and len(row_counts_dict.values()) > 0:
                        if check_consecutive(row_values, self.length):
                            if (len(row_counts_dict.values()) == 1 and list(row_counts_dict.values())[
                                0] == self.length and self.star_string not in list(row_counts_dict.keys())) or (
                                    len(row_counts_dict.values()) == 2 and self.length - 1 in list(
                                row_counts_dict.values()) and self.star_string not in list(row_counts_dict.keys())):
                                for entry in field:
                                    if entry[1][0] == row[1][0] and entry[2]:
                                        entry[0] = "-"
                            already_set = True

    def _set_values(self, player: Player, position: tuple, value):
        for dic in self.field_hidden:
            for name, array in dic.items():
                if name == player.name:
                    for entry in array:
                        if entry[1] == position:
                            entry[0] = value
                            entry[2] = True
                            break
                break
            break

        # self.check_full_line()

    def check_end(self):
        for dic in self.field_hidden:
            for name, array in dic.items():
                check_end_list = []
                for entry in array:
                    check_end_list.append(entry[2])
                if all(check_end_list):
                    return True, name
        return False, None

    def reset(self):
        self.__init__(self.length, self.height, self.players_list, self.carddeck)

    def __str__(self):
        self.check_full_line()
        sum_player = self.calculate_sum_player(self.players_list, self.carddeck.value_string_mapping())

        if len(self.carddeck.discard_stack) == 0:
            string = f"\nDiscard stack: []\n"
        else:
            string = f"\nDiscard stack: {self.carddeck.discard_stack[-1]}\n"

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

    N = Player("Nicolas", C, (4, 3))
    L = Player("Linus", C, (4, 3))

    G = GameField(4, 3, [N, L], C)
    star = G.star_string

    # print(G)
    G._set_values(N, (0, 1), 0)
    G._set_values(N, (1, 1), 0)
    G._set_values(N, (2, 1), 0)

    G._set_values(N, (0, 3), 0)
    G._set_values(N, (0, 2), 0)
    G._set_values(N, (0, 1), 0)
    G._set_values(N, (0, 0), 0)

    # G._set_values(N, (1, 2), 9)
    # G._set_values(A, (2, 2), 9)

    # G.flip_card_on_field(A, (0, 3))

    print(G)

    # G.reset()

    # print(G)
