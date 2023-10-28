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
                                card_on_field = entry[0]
                                entry[0] = player.card_on_hand
                                player.card_on_hand = None
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
                    columns_values = list(zip(*rows_values))

                    # Set values of row to 0 if all values are the same
                    for i, row in enumerate(rows_values):
                        row_counts = count_elements(row)
                        if "-" in list(row_counts.keys()):
                            count_deleted = row_counts["-"]
                        else:
                            count_deleted = 0

                        for key, value in row_counts.items():
                            if value == 3 and count_deleted == 1 or value == 4 and key != self.star_string:
                                print("bin drin")
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
                    columns_values = list(zip(*rows_values))

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

    def __str__(self):
        self.check_full_line()
        sum_player = self.calculate_sum_player(self.player_list)

        string = f""
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


class Carddeck:
    def __init__(self):
        self.cards = self.init_carddeck()
        print("carddeck no discard deck: ", self.cards)
        self.card_value_mapping = self.value_string_mapping()
        self.discard_stack = [self.cards.pop(0)]

        print("inital Carddeck: ", self.cards)
        print("initial discard stack: ", self.discard_stack)

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
        self.carddeck_player = Carddeck
        self.card_on_hand = None

    def flip_card(self, position: tuple):
        return position

    def pull_card_from_discard_stack(self, carddeck: Carddeck):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                card_on_hand = carddeck.discard_stack.pop()
                self.card_on_hand = card_on_hand
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


if __name__ == "__main__":
    C = Carddeck()

    S = Player("Sven", C, (4, 3))
    A = Player("Anna", C, (4, 3))

    G = GameField(4, 3, [S, A])
    star = G.star_string

    print(G.field_hidden)
    print(G)
    S.pull_card_from_discard_stack(C)
    print(S.card_on_hand)
    G.change_card_with_card_on_hand(S, (0, 0))
    S.put_card_on_discard_stack(C)
    print(G)
    print(S.card_on_hand)
