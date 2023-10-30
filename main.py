from gamefield import GameField
from player import Player
from carddeck import Carddeck


class Game:

    def __init__(self, player_names: list, game_field_dimensions: tuple, carddeck: Carddeck):
        self.game_field_dimensions = game_field_dimensions
        self.carddeck = carddeck

        self.players = self.init_players(player_names)  # dictionary [player_name: Player]

        # self.players = list
        self.game_field = GameField(game_field_dimensions[0], game_field_dimensions[1], list(self.players.values()),
                                    carddeck)

        self.card_value_mapping = self.carddeck.card_value_mapping

        self.end = False

        self.player_turn_order = []

    def init_players(self, player_names: list):
        players = {}
        for player_name in player_names:
            player = Player(player_name, self.carddeck, self.game_field_dimensions)
            players[player_name] = player

        return players

    def start(self):
        # starts game. Every player has to flip to cards. The player with the lowest sum of the two cards starts.

        # flip two cards for every player
        for player_name, player in self.players.items():
            position1 = input(f"Player {player_name} flip two cards! Enter position one [(0,0) - (2,3)]:")
            position1 = eval(position1)
            self.game_field.flip_card_on_field(player, position1)
            print(self.game_field)
            position2 = input(f"Enter position two [(0,0) - (2,3)]:")
            position2 = eval(position2)
            self.game_field.flip_card_on_field(player, position2)
            print(self.game_field)

        # choose player that starts. That player with the lowest card sum on field starts
        card_sum = self.game_field.calculate_sum_player(list(self.players.values()), self.card_value_mapping)

        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

        first_player = list(card_sum.keys())[0]
        print(f"Player {first_player} starts!")

        # create player turn order
        self.player_turn_order.append(first_player)
        for player in self.players.values():
            if player.name != first_player:
                self.player_turn_order.append(player.name)

        print(f"Player turn order: {self.player_turn_order}\n")
        print("-"*50)

    def run(self):
        while not self.end:
            last_round = None

            for i, player_name in enumerate(self.player_turn_order):
                print(f"Player {player_name} turn!")

                action = input("Choose action (pull deck : pd, pull discard stack : pds):")

                while action not in ["pd", "pds"]:
                    print("Invalid action! Try again!")
                    action = input("Choose action (pull deck : pd, pull discard stack : pds):")

                if action == "pd":
                    self.players[player_name].pull_card_from_deck(self.carddeck)
                    print(f"Your card on hand: {self.players[player_name].card_on_hand}")

                    action = input(
                        "Choose action (put card on discard stack : pcds, change card with card on field : cc):")

                    while action not in ["pcds", "cc"]:
                        print("Invalid action! Try again!")
                        action = input("Choose action (pull cardm from discard stack : pd, change card : cc):")

                    if action == "pcds":
                        self.players[player_name].put_card_on_discard_stack(self.carddeck)

                        position = input("Choose position on field [(0,0) - (2,3)]:")
                        position = eval(position)
                        self.game_field.flip_card_on_field(self.players[player_name], position)
                        print(self.game_field)

                        valid_action2 = True

                    elif action == "cc":
                        position = input("Choose position on field [(0,0) - (2,3)]:")
                        position = eval(position)
                        self.game_field.change_card_with_card_on_hand(self.players[player_name], position)
                        self.players[player_name].put_card_on_discard_stack(self.carddeck)
                        print(self.game_field)

                elif action == "pds":
                    self.players[player_name].pull_card_from_discard_stack(self.carddeck)
                    print(f"Your card on hand: {self.players[player_name].card_on_hand}")

                    action = input(
                        "Choose action (put card on discard stack : pcds, change card with card on field : cc):")

                    while action not in ["pcds", "cc"]:
                        print("Invalid action! Try again!")
                        action = input("Choose action (pull card from discard stack : pd, change card : cc):")

                    if action == "pcds":
                        self.players[player_name].put_card_on_discard_stack(self.carddeck)

                        position = input("Choose position on field [(0,0) - (2,3)]:")
                        position = eval(position)
                        self.game_field.flip_card_on_field(self.players[player_name], position)
                        print(self.game_field)

                    elif action == "cc":
                        position = input("Choose position on field [(0,0) - (2,3)]:")
                        position = eval(position)
                        self.game_field.change_card_with_card_on_hand(self.players[player_name], position)
                        self.players[player_name].put_card_on_discard_stack(self.carddeck)
                        print(self.game_field)

            end, name = self.game_field.check_end()

            print(end)

            if end:
                print(f"Player {name} ended the game. Everyone else has one more turn!")
                last_round = i
                print(f"Last round: {last_round}")
                continue

            if end and i == last_round:
                self.end = True

        print("Game ended!")

        # calculate winner
        card_sum = self.game_field.calculate_sum_player(list(self.players.values()), self.card_value_mapping)
        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}
        print(f"The winner is: {list(card_sum.keys())[0]}")

        # output of the other places
        for i, player_name in enumerate(list(card_sum.keys())[1:]):
            print(f"{i+2}. place: {player_name}")

        print("-"*50)




if __name__ == "__main__":
    carddeck = Carddeck()
    G = Game(["a", "b"], (4, 3), carddeck)
    G.start()
    G.run()
