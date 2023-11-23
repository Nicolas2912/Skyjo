from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField

import json


class Environment:

    def __init__(self, player_names: list, carddeck: Carddeck, gamefield: GameField):
        self.carddeck = carddeck
        self.players = self.init_players(player_names)
        self.gamefield = gamefield

        self.state = self.init_state()

    def init_players(self, player_names: list):
        players = {}
        for player_name in player_names:
            player = Player(player_name, self.carddeck, (4, 3))
            players[player_name] = player

        return players

    def init_state(self):
        state = {}

        for player_name, player in self.players.items():
            state[player_name] = {}
            state[player_name]["player_hand"] = player.card_on_hand

            field = self.reformat_field_hidden(player)

            state[player_name]["field"] = field

            state[player_name]["last_action"] = None

            # states of game: beginning, running, finished
            state[player_name]["state_of_game"] = self.state_of_game(player_name)

        state["discard_stack"] = self.carddeck.discard_stack

        return state

    def reformat_field_hidden(self, player: Player):
        field_hidden = self.gamefield.field_hidden
        for dic in field_hidden:
            for name, field in dic.items():
                if name == player.name:
                    return field

    def state_of_game(self, player_name: str):
        player_field = self.gamefield.field_hidden

        end, name = self.gamefield.check_end()

        if end and name == player_name:
            return "finished"

        # check if every player has two cards flipped
        flipped_cards = {}
        for dic in player_field:
            for name, field in dic.items():
                for entry in field:
                    if name not in flipped_cards and name == player_name:
                        flipped_cards[name] = []
                        flipped_cards[name].append(entry[2])
                    elif name == player_name:
                        flipped_cards[name].append(entry[2])

        for name, flipped in flipped_cards.items():
            if name == player_name and flipped_cards[name].count(True) < 2:
                return "beginning"

        else:
            return "running"

    def execute_action(self, player: Player, action: str, pos=None):

        # check legal actions
        last_action = self.state[player.name]["last_action"]
        legal_actions = self.legal_actions(last_action, player.name)

        # check if action is legal
        if action not in legal_actions:
            print(action)
            raise ValueError("Action is not legal!")

        # legal positions ((0,0) - (2,3))
        legal_positions = self.legal_positions(action, player.name)

        # check if position is legal
        if pos is not None and pos not in legal_positions:
            raise ValueError("Position is not legal!")

        if action == "flip card":
            # I need this just for the beginning where I flip two cards
            self.flip_card_on_field(player, pos)

            # update self.state
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["state_of_game"] = self.state_of_game(player.name)
            self.state[player.name]["last_action"] = action

        if action == "pull deck":
            self.pull_card_deck(player)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action
            self.state[player.name]["state_of_game"] = self.state_of_game(player.name)

        if action == "pull discard":
            self.pull_card_discard_stack(player)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action
            self.state[player.name]["state_of_game"] = self.state_of_game(player.name)

        elif pos is not None and action == "put discard":
            player.put_card_on_discard_stack(self.carddeck)
            self.flip_card_on_field(player, pos)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action
            self.state[player.name]["state_of_game"] = self.state_of_game(player.name)

        elif pos is not None and action == "change card":
            self.change_card(player, pos)

            # update self.state
            self.state[player.name]["player_hand"] = player.card_on_hand
            self.state[player.name]["field"] = self.reformat_field_hidden(player)
            self.state[player.name]["last_action"] = action
            self.state[player.name]["state_of_game"] = self.state_of_game(player.name)

    def all_actions(self) -> list:
        all_actions = ["pull deck", "pull discard", "put discard", "change card", "flip card"]
        return all_actions

    def all_positions(self) -> list:
        all_positions = [(i, j) for i in range(self.gamefield.height) for j in range(self.gamefield.length)]
        return all_positions

    def _count_flipped_cards(self, player_name):
        flipped_cards = []
        for entry in self.state[player_name]["field"]:
            flipped_cards.append(entry[2])

        return flipped_cards.count(True)

    def legal_actions(self, last_action: str, player_name) -> list:
        # check how many cards are flipped
        flipped_cards = self._count_flipped_cards(player_name)

        if last_action == "flip card" and flipped_cards < 2:
            legal_actions = ["flip card"]
        elif last_action in ["change card", "put discard", "flip card"] and flipped_cards >= 2:
            legal_actions = ["pull deck", "pull discard"]
        elif last_action in ["pull deck", "pull discard"]:
            legal_actions = ["change card", "put discard"]
        elif last_action is None:
            legal_actions = ["flip card"]
        else:
            raise ValueError("Last action is not valid!")

        return legal_actions

    def legal_positions(self, action: str = None, player_name: str = None):
        legal_positions = self.all_positions()

        if action == "put discard":
            # just get the positions where card is not flipped (False)
            legal_positions = []
            for entry in self.state[player_name]["field"]:
                if not entry[2]:
                    legal_positions.append(entry[1])

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

    def print_game_field(self):
        print(self.gamefield)


if __name__ == "__main__":
    carddeck = Carddeck()

    player1 = Player("Player1", carddeck, (4, 3))
    player2 = Player("Player2", carddeck, (4, 3))
    gamefield = GameField(4, 3, [player1, player2], carddeck)
    E = Environment(["Player1", "Player2"], carddeck, gamefield)

    E.execute_action(E.players["Player1"], "flip card", (0, 0))
    E.execute_action(E.players["Player1"], "flip card", (0, 1))

    E.execute_action(E.players["Player1"], "pull deck")
    E.execute_action(E.players["Player1"], "put discard")

    all_pos = E.all_positions()
    print(all_pos)
    # E.execute_action(E.players["Player1"], "put discard", (0, 0))

    # E.execute_action(E.players["Player1"], "change card", (0, 1))

    # print(E.state)

    # state = E.state
    # print(state)
    # print(state.keys())
    # print(state.values())
    # print(state["Player1"])

    # E.execute_action(E.players["Player1"], "put discard", (0, 0))
    # print(E.get_state())

    # state:
    # {player1: {player_hand: "1", field: [['1', (0,0), False], ...]}, player2: {player_hand: "2", field: [['2', (0,0), False], ...]}}
