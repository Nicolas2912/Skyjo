from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField

import copy
from collections import Counter


class Environment:

    def __init__(self, gamefield: GameField):
        self.carddeck = gamefield.carddeck
        # make copy of carddeck
        self.carddeck_copy = copy.deepcopy(self.carddeck)

        self.gamefield = gamefield

        self.gamefield_dimensions = (gamefield.length, gamefield.height)

        player_names = [player.name for player in gamefield.players_list]

        self.players = self.init_players(player_names)
        self.agents = self.init_agents(player_names)

        self.players_agents = self.players | self.agents

        self.number_all_cards = len(self.carddeck.all_cards)  # number of all cards with no card on discard stack

        self.state = self.init_state()

    def init_players(self, player_names: list):
        players = {}
        for player_name in player_names:
            if "agent" not in player_name.lower():
                player = Player(player_name, self.carddeck_copy, (self.gamefield.length, self.gamefield.height))
                players[player_name] = player

        return players

    def init_agents(self, agent_names: list):
        players = self.gamefield.players_list

        agents = {}
        for agent_name in agent_names:
            for player in players:
                if agent_name == player.name and agent_name not in self.players:
                    agents[agent_name] = player

        return agents

    def init_state(self):
        state = {}

        player_agents = self.players | self.agents

        for player_name, player in player_agents.items():
            state[player_name] = {}
            state[player_name]["player_hand"] = player.card_on_hand

            field = self.reformat_field_hidden(player)

            state[player_name]["field"] = field

            state[player_name]["last_action"] = None

            # states of game: beginning, running, finished
            state[player_name]["state_of_game"] = self.state_of_game(player_name)

        state["probabilities"] = self.calc_probabilities()

        state["discard_stack"] = self.carddeck.discard_stack

        return state

    def _update_probabilities(self, cards_counter, number_all_cards):
        probabilities = {}
        for card, count in cards_counter.items():
            try:
                probabilities[card] = count / (number_all_cards)
            except Exception as e:
                print(e)
                print(self.number_all_cards)
                break

        return probabilities

    def _update_probabilities_discard_stack(self, cards_counter, discard_stack):
        for card in discard_stack:
            if card != "-" and cards_counter[str(card)] > 0:
                cards_counter[str(card)] -= 1
            elif card == "-":
                self.gamefield.check_full_line()
                print(f"field hidden: {self.gamefield.field_hidden}")
                print(f"field environment: {self.state['ReflexAgent']['field']}")
                print("Error: Card is -")
                print(f"discard stack: {discard_stack}")
                # TODO: Irgendwie aktualisiert der das field (field_hidden) nicht korrekt, sodass zar 3 "-" angezeigt werden, aber intern wird das nicht so gespeichert
                raise ValueError("Card is -")

        return cards_counter, discard_stack

    def _update_probabilities_field(self, cards_counter, field):
        for dic in field:
            for name, field in dic.items():
                for entry in field:
                    if entry[2] and entry[0] != "-" and cards_counter[str(entry[0])] > 0:
                        cards_counter[str(entry[0])] -= 1

        return cards_counter

    def _update_number_all_cards(self, cards_counter, discard_stack, field):
        number_all_cards = 120

        for card in discard_stack:
            if card != "-" and cards_counter[str(card)] > 0:
                number_all_cards -= 1
            elif card == "-":
                print("Error: Card is -")
                print(f"discard stack: {discard_stack}")

                raise ValueError("Card is -")

        for dic in field:
            for name, field in dic.items():
                for entry in field:
                    if entry[2] and entry[0] != "-" and cards_counter[str(entry[0])] > 0:
                        number_all_cards -= 1

        return number_all_cards

    def calc_probabilities(self):
        cards_counter = Counter(self.carddeck.all_cards)

        # make all keys in cards_counter strings
        cards_counter = {str(key): value for key, value in cards_counter.items()}

        # update probabilities with discard stack
        cards_counter, discard_stack = self._update_probabilities_discard_stack(cards_counter,
                                                                                self.carddeck.discard_stack)

        cards_counter = self._update_probabilities_field(cards_counter,
                                                         self.gamefield.field_hidden)

        number_all_cards = self._update_number_all_cards(cards_counter,
                                                         self.carddeck.discard_stack,
                                                         self.gamefield.field_hidden)

        probabilities = self._update_probabilities(cards_counter, number_all_cards)

        return probabilities

    def reformat_field_hidden(self, player):
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

    def execute_action(self, player, action: str, pos=None, output: bool = True):

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
            print(f"Legal positions are: {legal_positions}")
            print(f"Your position is: {pos}")
            raise ValueError("Position is not legal!")

        from agents.simple_reflex_agent import RandomAgent2, ReflexAgent2

        if isinstance(player, RandomAgent2) or isinstance(player, ReflexAgent2):

            if action == "flip card":
                # I need this just for the beginning where I flip two cards

                self.flip_card_on_field(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

            if action == "pull deck":
                self.pull_card_deck(player, output)

                # update self.state
                self.update_state(player.name, action)

            if action == "pull discard":
                self.pull_card_discard_stack(player, output)

                # update self.state
                self.update_state(player.name, action)

            elif pos is not None and action == "put discard":
                player.put_card_on_discard_stack(self.carddeck, output)
                self.flip_card_on_field(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

            elif pos is not None and action == "change card":
                self.change_card(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

        if isinstance(player, Player):

            if action == "flip card":
                # I need this just for the beginning where I flip two cards
                self.flip_card_on_field(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

            if action == "pull deck":
                self.pull_card_deck(player, output)

                # update self.state
                self.update_state(player.name, action)

            if action == "pull discard":
                self.pull_card_discard_stack(player, output)

                # update self.state
                self.update_state(player.name, action)

            elif pos is not None and action == "put discard":
                player.put_card_on_discard_stack(self.carddeck, output)
                self.flip_card_on_field(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

            elif pos is not None and action == "change card":
                self.change_card(player, pos, output)

                # update self.state
                self.update_state(player.name, action)

    def update_state(self, player_name, action):

        player = self.players_agents[player_name]
        self.state[player.name]["player_hand"] = player.card_on_hand
        self.state[player.name]["field"] = self.reformat_field_hidden(player)
        self.state[player.name]["state_of_game"] = self.state_of_game(player.name)
        self.state[player.name]["last_action"] = action

        self.state["probabilities"] = self.calc_probabilities()

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
        if action == "put discard":
            # just get the positions where card is not flipped (False)
            legal_positions = []
            for entry in self.state[player_name]["field"]:
                if not entry[2] and entry[0] != "-":
                    legal_positions.append(entry[1])
        else:
            legal_positions = []
            for entry in self.state[player_name]["field"]:
                if entry[0] != "-":
                    legal_positions.append(entry[1])

        return legal_positions

    def flip_card_on_field(self, player, card_position: tuple, output: bool = True):
        self.gamefield.flip_card_on_field(player, card_position, output)

    def pull_card_discard_stack(self, player, output: bool = True):
        player.pull_card_from_discard_stack(self.carddeck, output)

    def pull_card_deck(self, player, output: bool = True):
        player.pull_card_from_deck(self.carddeck, output)

    def change_card(self, player, card_position: tuple, output: bool = True):
        self.gamefield.change_card_with_card_on_hand(player, card_position)
        player.put_card_on_discard_stack(self.carddeck, output)

    def reset(self):
        self.gamefield.reset()

    def print_game_field(self):
        print(self.gamefield)


if __name__ == "__main__":
    carddeck = Carddeck()
    player1 = Player("Player1", carddeck, (4, 3))
    gamefield = GameField(4, 3, [player1], carddeck)
    env = Environment(gamefield)

    print(env.carddeck.discard_stack)

    env.execute_action(env.players["Player1"], "flip card", (0, 0))
    env.execute_action(env.players["Player1"], "flip card", (0, 1))
    print(env.gamefield.field_hidden)

    env.execute_action(env.players["Player1"], "pull deck")
    env.execute_action(env.players["Player1"], "change card", (0, 2))
    print(env.gamefield.field_hidden)
    print(env.carddeck.discard_stack)
