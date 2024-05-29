from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from agents.rl_agent import RLAgent
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

import copy
from collections import Counter
import numpy as np


class Environment:

    def __init__(self, gamefield: GameField):
        self.carddeck = gamefield.carddeck
        # make copy of carddeck
        self.carddeck_copy = copy.deepcopy(self.carddeck)

        self.gamefield = gamefield

        self.gamefield_dimensions = (gamefield.length, gamefield.height)

        player_names = [player.name for player in gamefield.players_list]

        self.players = self.init_players(self.gamefield.players_list)
        self.agents = self.init_agents(self.gamefield.players_list)

        self.players_agents = self.players | self.agents

        self.number_all_cards = len(self.carddeck.all_cards)  # number of all cards with no card on discard stack

        self.state = self.init_state()

    def init_players(self, player_list: list):
        players = {}
        for player in player_list:
            if isinstance(player, Player):
                player = Player(player.name, self.carddeck_copy, (self.gamefield.length, self.gamefield.height))
                players[player.name] = player

        return players

    def init_agents(self, agent_list: list):
        agents = {}
        for agent in agent_list:
            # check if instance from agent is not Player
            if not isinstance(agent, Player):
                agent = RLAgent(agent.name, self.carddeck_copy, (self.gamefield.length, self.gamefield.height))
                agents[agent.name] = agent


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

        # convert string to int and when string is star convert to 13 then sort the dictionary ascending by key and after
        # sorting convert back to string and 13 back to star
        probabilities = {int(key) if key != "\u2666" else 13: value for key, value in probabilities.items()}
        probabilities = dict(sorted(probabilities.items(), key=lambda x: x[0]))
        probabilities = {str(key) if key != 13 else "\u2666": value for key, value in probabilities.items()}

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

        if isinstance(player, RandomAgent2) or isinstance(player, ReflexAgent2) or isinstance(player, RLAgent):

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


class RLEnvironment(gym.Env):
    def __init__(self, environment: Environment):
        super(RLEnvironment, self).__init__()
        self.skyjo_env = environment
        self.rl_name = None
        for agent_name, agent in self.skyjo_env.agents.items():
            if isinstance(agent, RLAgent):
                self.rl_name = agent_name


        """
        6. Which actions do I have?
            a. Pull a card from the deck
                a1. Change a card on the field with a card from the deck (all actions = legal)
                a2. Put card on discard stack and turn around one card on your field (legal actions)
            b. Pull a card from the discard stack
                a1. Change a card on the field with a card from the deck (all actions = legal)
                a2. Put card on discard stack and turn around one card on your field (legal actions) => NONSENSE
        """
        self.gamefield = self.skyjo_env.gamefield
        self.length = self.gamefield.length
        self.height = self.gamefield.height

        state = self.skyjo_env.state
        # state just for visible things
        self.state = self._transform_state(state)

        self.position_action_mapping = self._position_action_mapping()
        self.action_position_mapping = {v: k for k, v in self.position_action_mapping.items()}

        self.game_state = self.get_state_of_game()

        # TODO: At initialization there are only two actions possible: pos1 for flipping card and pos2 for flipping card
        self.action_space = gym.spaces.Discrete(len(self.position_action_mapping))

        self.observation_space = gym.spaces.Dict({
            "field": gym.spaces.Box(low=-2, high=14, shape=(self.height, self.length), dtype=int),
            "discard_stack": gym.spaces.Box(low=-2, high=13, shape=(1, ), dtype=int), # TODO: Discard stack dimension changes over time. Adjust that!
            "probabilities": gym.spaces.Box(low=0, high=1, shape=(16, ), dtype=float),

        })
        # self.action_space = gym.spaces.MultiDiscrete([5, len(self.position_action_mapping)])

        # define variables for actions
        # define variables
        self.pull_deck = False
        self.pull_discard = False
        self.change_card = False
        self.put_discard = False

    def _transform_state(self, state):
        new_state = {}
        for key, field_state in state.items():
            if key != "probabilities" and key != "discard_stack":
                # add playername to new state
                new_state[key] = {}
                field = field_state["field"]
                new_state[key]["field"] = []
                for entry in field:
                    card_value = entry[0]
                    if not entry[2]:  # If card is hidden
                        card_value = 14  # Use 14 to represent hidden cards
                    elif card_value == "\u2666":  # Convert diamond symbol to 13
                        card_value = 13
                    new_state[key]["field"].append(card_value)
                last_action = field_state["last_action"]
                new_state[key]["last_action"] = last_action
                state_of_game = field_state["state_of_game"]
                new_state[key]["state_of_game"] = state_of_game

        # reshape field
        for key, field_state in new_state.items():
            field = field_state["field"]
            field = np.array(field).reshape((self.height, self.length))
            new_state[key]["field"] = field

        discard_stack = state["discard_stack"]
        new_state["discard_stack"] = discard_stack
        probabilities = state["probabilities"]
        new_state["probabilities"] = probabilities

        return new_state


    def get_state_of_game(self):
        rl_agent_name = None
        for player in self.skyjo_env.gamefield.players_list:
            if isinstance(player, RLAgent):
                rl_agent_name = player.name

        state_of_game = self.state[rl_agent_name]["state_of_game"]

        return state_of_game

    @staticmethod
    def _action_mapping():
        action_mapping = {
            0: "pull deck",
            1: "pull discard",
            2: "change card",
            3: "put discard",
            4: "choose position",
        }

        return action_mapping

    def _position_action_mapping(self):
        position_action_mapping = {}
        action = 0
        for i in range(self.height):
            for j in range(self.length):
                position_action_mapping[(i, j)] = action
                action += 1

        return position_action_mapping

    def _check_every_card_hidden(self):
        field = self.state[self.rl_name]["field"]
        return np.all(field == 14)

    def _legal_actions(self):
        last_action = self.state[self.rl_name]["last_action"]
        legal_actions = self.skyjo_env.legal_actions(last_action, self.rl_name)
        return legal_actions

    def _legal_positions(self, field: np.ndarray) -> list:
        legal_positions = []
        for i in range(self.height):
            for j in range(self.length):
                if field[i][j] == 14:
                    legal_positions.append((i, j))
        return legal_positions

    def step(self, action):

        every_card_hidden = self._check_every_card_hidden()
        self.game_state = self.get_state_of_game()

        # check last action
        last_action = self.state[self.rl_name]["last_action"]
        if last_action == "pull discard":
            self.change_card = True
            self.pull_discard = True

        if last_action == "pull deck":
            self.pull_deck = True
            self.change_card = True

        if self.game_state == "beginning" and every_card_hidden:
            position = self.action_position_mapping[action]
            self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "flip card", position)
            # print the game field
            self.skyjo_env.print_game_field()
            # get current state
            state = self.skyjo_env.state
            self.state = self._transform_state(state)
            ever_card_hidden = self._check_every_card_hidden()

            # make new action space
            field = self.state[self.rl_name]["field"].astype(int)
            legal_positions = self._legal_positions(field)

            position_action_mapping = self.position_action_mapping

            # delete key, value in position_action_mapping key is not in legal_positions
            new_position_action_mapping = {}
            action = 0
            for pos, act in position_action_mapping.items():
                if pos in legal_positions:
                    new_position_action_mapping[pos] = action
                    action += 1

            self.new_action_position_mapping = {v: k for k, v in new_position_action_mapping.items()}

            self.action_space = gym.spaces.Discrete(len(new_position_action_mapping))

        elif self.game_state == "beginning" and not every_card_hidden:
            position = self.new_action_position_mapping[action]
            self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "flip card", position)
            # print the game field
            self.skyjo_env.print_game_field()
            # get current state
            state = self.skyjo_env.state
            self.state = self._transform_state(state)
            # make new action space
            field = self.state[self.rl_name]["field"].astype(int)
            legal_positions = self._legal_positions(field)

            position_action_mapping = self.position_action_mapping

            # delete key, value in position_action_mapping key is not in legal_positions
            new_position_action_mapping = {}
            action = 0
            for pos, act in position_action_mapping.items():
                if pos in legal_positions:
                    new_position_action_mapping[pos] = action
                    action += 1

            self.new_action_position_mapping = {v: k for k, v in new_position_action_mapping.items()}

            # TODO: Adjust action_space for running game
            # First: Pull deck or pull discard stack (0, 1)
            # Second: Change card or put discard (0, 1)
            # Third: Choose position [all positions when change card, only legal positions when put discard]
                # a): 0-11: legal positions
                # b): legal positions

            self.action_space = gym.spaces.Discrete(2)
            print(f"Action space: {self.action_space}")
            print(f"Type action space: {type(self.action_space)}")
            print(f"Shape action space: {self.action_space.shape}")

        elif self.game_state == "running":
            print(f"Action running: {action}")
            if action == 0 and not self.pull_deck:
                # 0 --> pull deck
                self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "pull deck")
                # print gamefield
                self.skyjo_env.print_game_field()
                self.state = self._transform_state(self.skyjo_env.state)

            if self.pull_deck and self.action_space == gym.spaces.Discrete(2) and action == 0:
                # TODO: Wieso geht der hier nicht rein, wenn er soll?
                # second time: 0 --> change card
                self.change_card = True
                self.action_space = gym.spaces.Discrete(12)
                self.pull_deck = False

            if action == 1 and self.pull_deck:
                # second time: 1 --> put discard
                self.put_discard = True
                # get legal positions
                field = self.state[self.rl_name]["field"].astype(int)
                legal_positions = self._legal_positions(field)
                position_action_mapping = self.position_action_mapping

                self.action_space = gym.spaces.Discrete(len(self.new_action_position_mapping))

                # update new_action_position_mapping
                new_position_action_mapping = {}
                action = 0
                for pos, act in position_action_mapping.items():
                    if pos in legal_positions:
                        new_position_action_mapping[pos] = action
                        action += 1
                self.new_action_position_mapping = {v: k for k, v in new_position_action_mapping.items()}
                self.pull_deck = False

            if self.put_discard:
                position = self.new_action_position_mapping[action] # TODO: Fix this
                self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "put discard", position)
                # print gamefield
                self.skyjo_env.print_game_field()
                self.state = self._transform_state(self.skyjo_env.state)
                self.put_discard = False
                self.action_space = gym.spaces.Discrete(2)

            if self.change_card and self.pull_deck:
                position = self.new_action_position_mapping[action]
                self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "change card", position)
                # print gamefield
                self.skyjo_env.print_game_field()
                self.state = self._transform_state(self.skyjo_env.state)
                self.change_card = False
                self.action_space = gym.spaces.Discrete(2)

            elif action == 1 and not self.pull_discard:
                # pull discard
                self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "pull discard")
                # print gamefield
                self.skyjo_env.print_game_field()
                self.state = self._transform_state(self.skyjo_env.state)

                self.action_space = gym.spaces.Discrete(12)

            if self.pull_discard and self.change_card:
                # change card
                position = self.new_action_position_mapping[action]
                self.skyjo_env.execute_action(self.skyjo_env.agents[self.rl_name], "change card", position)
                # print gamefield
                self.skyjo_env.print_game_field()
                self.state = self._transform_state(self.skyjo_env.state)
                self.pull_discard = False
                self.change_card = False

        elif self.game_state == "finished":
            print("Game is finished!")
            done = True
            reward = 1
            return self.state, reward, done, {}


        reward = 0
        done = False
        truncated = False

        field = np.array(self.state[self.rl_name]["field"], dtype=int)
        probabilities = list()
        for prob in self.skyjo_env.state["probabilities"].values():
            probabilities.append(prob)
        probabilities = np.array(probabilities)
        discard_stack = np.array(self.skyjo_env.carddeck.discard_stack)

        discard_stack_new = []
        for card in discard_stack:
            if card == "\u2666":
                card = 13
            discard_stack_new.append(int(card))
        discard_stack = np.array(discard_stack_new, dtype=int)


        state = {
            "field": field,
            "discard_stack": discard_stack,
            "probabilities": probabilities
        }

        return state, reward, done, truncated, {}

    def reset(self, seed=None):

        field = []
        agents_dict = self.skyjo_env.agents
        for agent_name, agent in agents_dict.items():
            if isinstance(agent, RLAgent):
                row = list()
                for card in agent.player_cards:
                    # check for star and convert to 13
                    if card == "\u2666":
                        card = 13
                    row.append(card)
                    if len(row) == self.length:
                        field.append(row)
                        row = []

        field = np.array(field)

        probabilities = list()
        for prob in self.skyjo_env.state["probabilities"].values():
            probabilities.append(prob)
        probabilities = np.array(probabilities)

        discard_stack = self.skyjo_env.carddeck.discard_stack
        discard_stack_new = []
        for card in discard_stack:
            if card == "\u2666":
                card = 13
            discard_stack_new.append(int(card))

        reset_state = {
            "field": np.array(field),
            "discard_stack": np.array(discard_stack_new, dtype=int),
            "probabilities": probabilities
        }

        return reset_state, {}


if __name__ == "__main__":
    carddeck = Carddeck()
    agent1 = RLAgent("RLBOT", carddeck, (4, 3))
    #player1 = Player("Player1", carddeck, (4, 3))

    gamefield = GameField(4, 3, [agent1], carddeck)
    env = Environment(gamefield)

    rl_env = RLEnvironment(env)
    check_env(rl_env)
