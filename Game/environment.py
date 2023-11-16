from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField

import json


class Environment:

    def __init__(self, player_names: list):
        self.carddeck = self.init_carddeck()
        self.players = self.init_players(player_names)
        self.gamefield = self.init_gamefield()

        self.state = self.init_state()

    def init_carddeck(self):
        carddeck = Carddeck()

        return carddeck

    def init_players(self, player_names: list):
        players = {}
        for player_name in player_names:
            player = Player(player_name, self.carddeck, (4, 3))
            players[player_name] = player

        return players

    def init_gamefield(self):
        gamefield = GameField(4, 3, list(self.players.values()), self.carddeck)

        return gamefield

    def init_state(self):
        state = {}

        for player_name, player in self.players.items():
            state[player_name] = {}
            state[player_name]["player_hand"] = player.card_on_hand

            field = self.reformat_field_hidden(player)

            state[player_name]["field"] = field

            state[player_name]["last_action"] = None

        state["discard_stack"] = self.carddeck.discard_stack

        # states of game: beginning, running, finished
        state["state_of_game"] = self.state_of_game()

        return state

    def reformat_field_hidden(self, player: Player):
        field_hidden = self.gamefield.field_hidden
        for dic in field_hidden:
            for name, field in dic.items():
                if name == player.name:
                    return field



    def start(self, player_pos_dict: dict):
        # player_pos_dict = {"Player1": [(0,0), (0,1)], "Player2": [(0,2), (0,3)]}
        # key is Player object, value is list of positions

        # # check valid positions
        # legal_positions = self.legal_positions()
        # for player, positions in player_pos_dict.items():
        #     for position in positions:
        #         if position not in legal_positions:
        #             raise ValueError("Position is not legal!")
        #
        # # check if every player has two positions
        # for player, positions in player_pos_dict.items():
        #     if len(positions) != 2:
        #         raise ValueError("Player must have two positions for beginning!")
        #
        # # flip two cards for every player
        # for player, positions in player_pos_dict.items():
        #     for position in positions:
        #         self.gamefield.flip_card_on_field(player, position)
        pass

    def state_of_game(self):
        player_field = self.gamefield.field_hidden

        end, name = self.gamefield.check_end()

        if end:
            return "finished"

        flipped_cards = []
        for dic in player_field:
            for name, field in dic.items():
                for entry in field:
                    flipped_cards.append(entry[2])

        if not any(flipped_cards):
            return "beginning"

        else:
            return "running"

    def execute_action(self, player: Player, action: str, pos=None):
        # action1 = ("pull deck", ("change", (0, 0)))
        # action2 = ("pull deck", ("flip", (0, 0)))
        # action3 = ("pull discard", ("change", (0, 0)))
        # action4 = ("pull discard", ("flip", (0, 0)))

        # list of allowed actions:
        legal_actions = self.legal_actions()

        # check lega actions
        last_action = self.state[player.name]["last_action"]
        if last_action in ["change card", "put discard", None] and action not in ["pull deck", "pull discard"]:
            raise ValueError("Action is not legal!")
        elif last_action in ["pull deck", "pull discard"] and action not in ["change card", "put discard"]:
            raise ValueError("Action is not legal!")

        # legal positions ((0,0) - (2,3))
        legal_positions = self.legal_positions()
        legal_positions.append(None)

        # check if action is legal
        if action not in legal_actions:
            raise ValueError("Action is not legal!")

        # check if position is legal
        if pos not in legal_positions:
            raise ValueError("Position is not legal!")

        if action == "pull deck":
            self.pull_card_deck(player)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action

        if action == "pull discard":
            self.pull_card_discard_stack(player)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action

        elif pos is not None and action == "put discard":
            player.put_card_on_discard_stack(self.carddeck)
            self.flip_card_on_field(player, pos)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action

        elif pos is not None and action == "change card":
            self.change_card(player, pos)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action

    def legal_actions(self):
        legal_actions = ["pull deck", "pull discard", "put discard", "change card"]
        return legal_actions

    def legal_positions(self):
        legal_positions = [(i, j) for i in range(3) for j in range(4)]
        return legal_positions

    def flip_card_on_field(self, player: Player, card_position: tuple):
        self.gamefield.flip_card_on_field(player, card_position)

    def pull_card_discard_stack(self, player: Player):
        player.pull_card_from_discard_stack(self.carddeck)

    def pull_card_deck(self, player: Player):
        player.pull_card_from_deck(self.carddeck)

    def change_card(self, player: Player, card_position: tuple):
        self.gamefield.change_card_with_card_on_hand(player, card_position)
        player.put_card_on_discard_stack(self.carddeck)

    def reset(self):
        self.gamefield.reset()


if __name__ == "__main__":
    E = Environment(["Player1", "Player2"])
    state = E.state

    E.execute_action(E.players["Player1"], "pull deck")

    state = E.state
    print(state)
    # print(state.keys())
    # print(state.values())
    # print(state["Player1"])

    E.execute_action(E.players["Player1"], "put discard", (0, 0))
    # print(E.get_state())

    # state:
    # {player1: {player_hand: "1", field: [['1', (0,0), False], ...]}, player2: {player_hand: "2", field: [['2', (0,0), False], ...]}}
