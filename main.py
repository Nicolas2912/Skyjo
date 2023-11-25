import numpy as np

from Game.gamefield import GameField
from Game.player import Player
from Game.carddeck import Carddeck

from agents.simple_reflex_agent import RandomAgent2, ReflexAgent2
from Game.environment import Environment
from scipy.stats import norm

import matplotlib.pyplot as plt

import random, time, copy

from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


# random.seed(10)


def set_up_game():
    n = int(input("How many players?"))
    player_names = []
    for i in range(n):
        player_names.append(input(f"Enter name of player {i + 1}:"))

    return player_names


class Game2:

    def __init__(self, environment: Environment):
        self.env = environment

        self.player_turn_order = []

        self.players_agents = self.env.players | self.env.agents

        self.end = False

    def __flip_all_cards(self):
        for dic in self.env.gamefield.field_hidden:
            for name, array in dic.items():
                for entry in array:
                    entry[2] = True

    def start_players(self):
        # starts game. Every player has to flip to cards. The player with the lowest sum of the two cards starts.
        if len(self.env.agents) == 0:

            print("Starting Skyjo!")

            # flip two cards for every player
            for player_name, player in self.env.players.items():
                while True:
                    try:
                        position1 = input(f"Player {player_name} flip two cards! Enter position one [(0,0) - (2,3)]:")
                        position1 = eval(position1)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.env.gamefield.flip_card_on_field(player, position1)
                print(self.env.gamefield)

                while True:
                    try:
                        position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                        position2 = eval(position2)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.env.gamefield.flip_card_on_field(player, position2)
                print(self.env.gamefield)

            # choose player that starts. That player with the lowest card sum on field starts
            card_sum = self.env.gamefield.calculate_sum_player(list(self.env.players.values()),
                                                               self.env.carddeck.card_value_mapping)

            # sort card_sum dictionary by value
            card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

            first_player = list(card_sum.keys())[0]
            print(f"Player {first_player} starts!")

            # create player turn order
            self.player_turn_order.append(first_player)
            for player in self.env.players.values():
                if player.name != first_player:
                    self.player_turn_order.append(player.name)

            print(f"Player turn order: {self.player_turn_order}\n")
            print("-" * 50)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def turn_players(self, player_name):

        if len(self.env.agents) == 0:
            print(f"Player {player_name} turn!")

            def get_valid_action(prompt, valid_actions):
                action = input(prompt)

                while action not in valid_actions:
                    print("Invalid action! Try again!")
                    action = input(prompt)

                return action

            action = get_valid_action(
                "Choose action (pull deck : pd, pull discard stack : pds):",
                ["pd", "pds"]
            )

            if action == "pd":
                self.env.players[player_name].pull_card_from_deck(self.env.carddeck)
                print(f"Your card on hand: {self.env.players[player_name].card_on_hand}")

                action = get_valid_action(
                    "Choose action (put card on discard stack : pcds, change card with card on field : cc):",
                    ["pcds", "cc"]
                )

                if action == "pcds":
                    self.env.players[player_name].put_card_on_discard_stack(self.env.carddeck)

                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.env.gamefield.flip_card_on_field(self.env.players[player_name], position)

                    print(self.env.gamefield)

                elif action == "cc":
                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.env.gamefield.change_card_with_card_on_hand(self.env.players[player_name], position)
                    self.env.players[player_name].put_card_on_discard_stack(self.env.carddeck)

                    print(self.env.gamefield)

            elif action == "pds":
                self.env.players[player_name].pull_card_from_discard_stack(self.env.carddeck)
                print(f"Your card on hand: {self.env.players[player_name].card_on_hand}")

                action = get_valid_action(
                    "Choose action (change card with card on field : cc):",
                    ["cc"]
                )

                if action == "cc":
                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.env.gamefield.change_card_with_card_on_hand(self.env.players[player_name], position)
                    self.env.players[player_name].put_card_on_discard_stack(self.env.carddeck)

                    print(self.env.gamefield)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def run_players(self):

        if len(self.env.agents) == 0:
            end_player = False
            end = False

            while not self.end:

                for i, player_name in enumerate(self.player_turn_order):
                    self.turn_players(player_name)
                    end, name = self.env.gamefield.check_end()

                    if end and name in self.player_turn_order:
                        print(f"Player {name} ended the game. Everyone else has one more turn!")
                        self.player_turn_order.remove(name.strip())
                        end_player = True
                        break

                if end_player:
                    for i, player_name in enumerate(self.player_turn_order):
                        self.turn_players(player_name)

                        end, name = self.env.gamefield.check_end()

                if end and end_player:
                    self.end = True
                    self.__flip_all_cards()
                    print("Final board:\n", self.env.gamefield)
                    break

            print("Game ended!")

            # calculate winner
            card_sum = self.env.gamefield.calculate_sum_player(list(self.env.players.values()),
                                                               self.env.carddeck.card_value_mapping)
            # sort card_sum dictionary by value
            card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}
            print(f"The winner is: {list(card_sum.keys())[0]}, Sum: {list(card_sum.values())[0]}")

            # output of the other places
            for i, player_name in enumerate(list(card_sum.keys())[1:]):
                print(f"{i + 2}. place: {player_name}, Sum: {list(card_sum.values())[i + 1]}")

            print("=" * 50)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def start_player_agent(self, output: bool = True):
        if len(self.env.players) > 0 and len(self.env.agents) > 0:
            if output:
                print("Starting Skyjo!")

            agents_players = self.env.players | self.env.agents

            # flip two cards for every player
            for name, obj in agents_players.items():
                # make action for player
                if name in self.env.players:
                    if output:
                        print(f"Player {name} turn!\n")
                    while True:
                        try:
                            position1 = input(f"Player {name} flip two cards! Enter position one [(0,0) - (2,3)]:")
                            position1 = eval(position1)
                            break
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.env.execute_action(obj, "flip card", position1, output)
                    if output:
                        self.env.print_game_field()
                    while True:
                        try:
                            position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                            position2 = eval(position2)
                            break
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.env.execute_action(obj, "flip card", position2, output)
                    if output:
                        self.env.print_game_field()

                # make action for agent
                if name in self.env.agents:
                    legal_positions = self.env.legal_positions()
                    pos1, pos2 = obj.flip_cards_start(legal_positions)
                    self.env.execute_action(obj, "flip card", pos1, output)
                    self.env.execute_action(obj, "flip card", pos2, output)
                    if output:
                        self.env.print_game_field()

            # choose player that starts. That player with the lowest card sum on field starts
            card_sum = self.env.gamefield.calculate_sum_player(list(self.players_agents.values()),
                                                               self.env.carddeck.card_value_mapping)

            # sort card_sum dictionary by value
            card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

            first_player = list(card_sum.keys())[0]
            print(f"Player {first_player} starts!")

            # create player turn order
            self.player_turn_order.append(first_player)
            for player in self.players_agents.values():
                if player.name != first_player:
                    self.player_turn_order.append(player.name)

            print(f"Player turn order: {self.player_turn_order}\n")

        else:
            raise ValueError(
                f"There must be at least one player and one agent! \nPlayer: {self.env.players}\nAgent: {self.env.agents}")

    def turn_player_agent(self, player_name, output: bool = True):
        pass

    def run_player_agent(self):
        pass

    def start_agents(self):
        pass

    def turn_agents(self):
        pass

    def run_agents(self):
        pass


class Game(Environment):

    def __init__(self, player_names: list, game_field_dimensions: tuple, carddeck: Carddeck, player_and_agents: list):
        super().__init__(player_names, carddeck, GameField(game_field_dimensions[0], game_field_dimensions[1],
                                                           player_and_agents, carddeck))
        self.game_field_dimensions = game_field_dimensions
        self.carddeck = carddeck

        self.players = self.init_players(player_names)
        self.agents = self.init_agents(player_names)

        self.card_value_mapping = self.carddeck.card_value_mapping

        self.end = False

        self.player_turn_order = []

    def start_player_agent(self, output: bool = True):
        if len(self.players) > 0 and len(self.agents) > 0:
            if output:
                print("Starting Skyjo!")

            agents_players = self.players | self.agents

            # flip two cards for every player
            for name, obj in agents_players.items():
                # make action for player
                if name in self.players:
                    if output:
                        print(f"Player {name} turn!\n")
                    while True:
                        try:
                            position1 = input(f"Player {name} flip two cards! Enter position one [(0,0) - (2,3)]:")
                            position1 = eval(position1)
                            break
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.execute_action(obj, "flip card", position1, output)
                    if output:
                        self.print_game_field()
                    while True:
                        try:
                            position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                            position2 = eval(position2)
                            break
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.execute_action(obj, "flip card", position2, output)
                    if output:
                        self.print_game_field()

                # make action for agent
                if name in self.agents:
                    self.execute_action(obj, "flip card", None, output)
                    if output:
                        self.print_game_field()

            # if output:
            #     self.print_game_field()


        else:
            raise ValueError(
                f"There must be at least one player and one agent! \nPlayer: {self.players}\nAgent: {self.agents}")

    def start_players(self):
        # starts game. Every player has to flip to cards. The player with the lowest sum of the two cards starts.
        if len(self.agents) == 0:

            print("Starting Skyjo!")

            # flip two cards for every player
            for player_name, player in self.players.items():
                while True:
                    try:
                        position1 = input(f"Player {player_name} flip two cards! Enter position one [(0,0) - (2,3)]:")
                        position1 = eval(position1)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.gamefield.flip_card_on_field(player, position1)
                print(self.gamefield)

                while True:
                    try:
                        position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                        position2 = eval(position2)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.gamefield.flip_card_on_field(player, position2)
                print(self.gamefield)

            # choose player that starts. That player with the lowest card sum on field starts
            card_sum = self.gamefield.calculate_sum_player(list(self.players.values()), self.card_value_mapping)

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
            print("-" * 50)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def player_turn_players(self, player_name):

        if len(self.agents) == 0:
            print(f"Player {player_name} turn!")

            def get_valid_action(prompt, valid_actions):
                action = input(prompt)

                while action not in valid_actions:
                    print("Invalid action! Try again!")
                    action = input(prompt)

                return action

            action = get_valid_action(
                "Choose action (pull deck : pd, pull discard stack : pds):",
                ["pd", "pds"]
            )

            if action == "pd":
                self.players[player_name].pull_card_from_deck(self.carddeck)
                print(f"Your card on hand: {self.players[player_name].card_on_hand}")

                action = get_valid_action(
                    "Choose action (put card on discard stack : pcds, change card with card on field : cc):",
                    ["pcds", "cc"]
                )

                if action == "pcds":
                    self.players[player_name].put_card_on_discard_stack(self.carddeck)

                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.gamefield.flip_card_on_field(self.players[player_name], position)

                    print(self.gamefield)

                elif action == "cc":
                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.gamefield.change_card_with_card_on_hand(self.players[player_name], position)
                    self.players[player_name].put_card_on_discard_stack(self.carddeck)

                    print(self.gamefield)

            elif action == "pds":
                self.players[player_name].pull_card_from_discard_stack(self.carddeck)
                print(f"Your card on hand: {self.players[player_name].card_on_hand}")

                action = get_valid_action(
                    "Choose action (change card with card on field : cc):",
                    ["cc"]
                )

                if action == "cc":
                    while True:
                        try:
                            position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                            break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                        except Exception as e:
                            print(f"Error: {e}. Please enter a valid position.")

                    self.gamefield.change_card_with_card_on_hand(self.players[player_name], position)
                    self.players[player_name].put_card_on_discard_stack(self.carddeck)

                    print(self.gamefield)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def run_players(self, set_values: bool = False):

        if set_values:
            self.gamefield._set_values(self.players["Nicolas"], (1, 0), 0)
            # self.gamefield._set_values(self.players["Linus"], (1, 2), 9)
            # self.gamefield._set_values(self.players["Linus"], (2, 2), 9)

            print(self.gamefield)

        if len(self.agents) == 0:
            end_player = False
            end = False

            while not self.end:

                for i, player_name in enumerate(self.player_turn_order):
                    self.player_turn_players(player_name)
                    end, name = self.gamefield.check_end()

                    if end and name in self.player_turn_order:
                        print(f"Player {name} ended the game. Everyone else has one more turn!")
                        self.player_turn_order.remove(name.strip())
                        end_player = True
                        break

                if end_player:
                    for i, player_name in enumerate(self.player_turn_order):
                        self.player_turn_players(player_name)

                        end, name = self.gamefield.check_end()

                if end and end_player:
                    self.end = True
                    self.__flip_all_cards()
                    print("Final board:\n", self.gamefield)
                    break

            print("Game ended!")

            # calculate winner
            card_sum = self.gamefield.calculate_sum_player(list(self.players.values()), self.card_value_mapping)
            # sort card_sum dictionary by value
            card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}
            print(f"The winner is: {list(card_sum.keys())[0]}, Sum: {list(card_sum.values())[0]}")

            # output of the other places
            for i, player_name in enumerate(list(card_sum.keys())[1:]):
                print(f"{i + 2}. place: {player_name}, Sum: {list(card_sum.values())[i + 1]}")

            print("=" * 50)
        else:
            raise ValueError("This method is just for players and not for agents!")

    def __flip_all_cards(self):
        for dic in self.gamefield.field_hidden:
            for name, array in dic.items():
                for entry in array:
                    entry[2] = True


class GameAgent(Game, Environment):

    def __init__(self, player_names: list, game_field_dimensions: tuple, carddeck: Carddeck):
        Game.__init__(self, player_names, game_field_dimensions, carddeck)

        Environment.__init__(self, player_names, carddeck, self.gamefield)

        self.agent = self.agents[0]

    def start(self, output: bool = True):

        if output:
            print("Starting Skyjo!")

            self.print_game_field()

        # flip two cards for every player
        for player_name, player in self.players.items():
            if output:
                print(f"Player {player_name} turn!\n")
            if player_name == self.agent.agent_name:
                self.agent.act(output)
                if output:
                    self.print_game_field()

            else:
                while True:
                    try:
                        position1 = input(f"Player {player_name} flip two cards! Enter position one [(0,0) - (2,3)]:")
                        position1 = eval(position1)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.execute_action(player, "flip card", position1, output)
                if output:
                    self.print_game_field()
                while True:
                    try:
                        position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                        position2 = eval(position2)
                        break
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.execute_action(player, "flip card", position2, output)
                if output:
                    self.print_game_field()

        card_sum = self.game_field.calculate_sum_player(list(self.players.values()), self.card_value_mapping)

        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

        first_player = list(card_sum.keys())[0]
        if output:
            print(f"Player {first_player} starts!")

        # create player turn order
        self.player_turn_order.append(first_player)
        for player in self.players.values():
            if player.name != first_player:
                self.player_turn_order.append(player.name)

        if output:
            print(f"Player turn order: {self.player_turn_order}\n")
            print("-" * 50)

    def player_turn_agent(self, player_name, output: bool = True):
        if output:
            print(f"Player {player_name} turn!")

        if player_name == self.agent.agent_name:
            self.agent.act(output)
            self.agent.act(output)
            if output:
                self.print_game_field()

        else:
            raise ValueError("Player name is not agent name!")

    def run(self):
        end_player = False
        end = False

        while not self.end:
            for i, player_name in enumerate(self.player_turn_order):
                if player_name == self.agent.agent_name:
                    self.player_turn_agent(player_name)
                else:
                    self.player_turn(player_name)
                    end, name = self.game_field.check_end()

                    if end and name in self.player_turn_order:
                        print(f"Player {name} ended the game. Everyone else has one more turn!")
                        self.player_turn_order.remove(name.strip())
                        end_player = True
                        break

            if end_player:
                for i, player_name in enumerate(self.player_turn_order):
                    if player_name == self.agent.agent_name:
                        self.player_turn_agent(player_name)
                    else:
                        self.player_turn(player_name)

                    end, name = self.game_field.check_end()

            if end and end_player:
                self.end = True
                self.flip_all_cards()
                print("Final board:\n", self.game_field)
                break

        print("Game ended!")

        # calculate winner
        card_sum = self.game_field.calculate_sum_player(list(self.players.values()), self.card_value_mapping)
        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}
        print(f"The winner is: {list(card_sum.keys())[0]}, Sum: {list(card_sum.values())[0]}")

        # output of the other places
        for i, player_name in enumerate(list(card_sum.keys())[1:]):
            print(f"{i + 2}. place: {player_name}, Sum: {list(card_sum.values())[i + 1]}")

        print("=" * 50)

    def run_agent_alone(self, output: bool = True):
        n = random.randint(0, 10000)
        random.seed(None)

        self.agent.act(output)
        if output:
            self.print_game_field()

        player_name = self.agent.agent_name

        while not self.end:
            self.player_turn_agent(player_name, output)
            end, name = self.game_field.check_end()
            if end:
                self.end = True
        if output:
            print("Game ended!")

        # calculate winner
        card_sum = self.game_field.calculate_sum_player(list(self.players.values()), self.card_value_mapping)

        result = card_sum[self.agent.agent_name]
        if output:
            print("result:", result)
            print("=" * 50)

        return result


class Simulation:

    def __init__(self, agent_name: list):
        self.agent_name = agent_name

    def simulate_agent_games(self, n: int, output: bool = True):

        start_simulation = time.time()

        overall_results = {}

        for agent_name in self.agent_name:
            results = []
            run_time = []

            for _ in tqdm(range(n)):
                carddeck = Carddeck()
                player_names = [agent_name]
                game_field_dimensions = (4, 3)
                G = GameAgent(player_names, game_field_dimensions, carddeck)

                start = time.time()
                G.start(output)
                results.append(G.run_agent_alone(output))
                run_time.append(time.time() - start)

            overall_results[agent_name] = results

            time_elapsed_simulation = time.time() - start_simulation

            time_average = sum(run_time) / n

            x = [i + 1 for i in range(n)]

            average = sum(results) / n

            print(f"Simulation finished in {time_elapsed_simulation:.2f} seconds")
            print(f"Average time per run: {time_average} seconds")

        # plot histogram
        for agent_name, results in overall_results.items():
            if agent_name == "RandomAgent":
                color = "blue"
                label = "RandomAgent results"
            elif agent_name == "ReflexAgent":
                color = "orange"
                label = "ReflexAgent results"

            n, bins, _ = plt.hist(results, bins=75, label=f"{label} results", color=color)
            plt.legend(loc='upper right')

            mean, std = np.mean(results), np.std(results)

            print(f"Mean: {mean:.2f}, Std: {std:.2f}")

            # plot pdf
            x = np.linspace(min(results), max(results), 1000)
            p = norm.pdf(x, mean, std)
            p *= n.max() / p.max()

            plt.plot(x, p, linewidth=4, label=f'Normal Distribution {agent_name}', color=color)

            plt.xlabel("Sum of cards")
            plt.ylabel("Frequency")
            plt.title("Agent performance")

        plt.show()

    def simulate_single_game(self):
        carddeck = Carddeck()
        player_names = ["RandomAgent"]
        game_field_dimensions = (4, 3)
        G = GameAgent(player_names, game_field_dimensions, carddeck)

        start = time.time()
        G.start(False)
        result = G.run_agent_alone(False)
        run_time = time.time() - start

        # print(f"Game finished with result: {result} in {run_time:.2f} seconds")

        return result, run_time

    def simulate_agent_games_parallel(self, n):
        results = []
        run_times = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.simulate_single_game) for _ in tqdm(range(n))]

            for future in tqdm(as_completed(futures), total=n):
                result, run_time = future.result()
                results.append(result)
                run_times.append(run_time)

            # plot histogram
            n, bins, _ = plt.hist(results, bins=50, label=f"Agent results")

            mean, std = np.mean(results), np.std(results)

            print(f"Mean: {mean:.2f}, Std: {std:.2f}")

            # plot pdf
            x = np.linspace(min(results), max(results), 1000)
            p = norm.pdf(x, mean, std)
            p *= n.max() / p.max()
            plt.plot(x, p, 'k', linewidth=2)

            plt.plot(x, p, 'k', linewidth=2, label='Normal Distribution')

            plt.xlabel("Sum of cards")
            plt.ylabel("Frequency")
            plt.title("Agent performance")
            plt.show()

        return results, run_times


if __name__ == "__main__":
    carddeck = Carddeck()
    player = Player("Nicolas", carddeck, (4, 3))
    # player1 = Player("Linus", carddeck, (4, 3))
    agent = RandomAgent2("RandomAgent", carddeck, (4, 3))

    gamefield = GameField(4, 3, [player, agent], carddeck)
    environment = Environment(gamefield)

    game = Game2(environment)
    game.start_player_agent()
    # game.run_players()

    # S = Simulation(["ReflexAgent", "RandomAgent"])
    # S.simulate_agent_games_parallel(100)
    # S.simulate_agent_games(3, True)
