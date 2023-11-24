import numpy as np

from Game.gamefield import GameField
from Game.player import Player
from Game.carddeck import Carddeck

from agents.simple_reflex_agent import RandomAgent
from Game.environment import Environment
from scipy.stats import norm

import matplotlib.pyplot as plt

import random, time

from tqdm import tqdm


# random.seed(10)


def set_up_game():
    n = int(input("How many players?"))
    player_names = []
    for i in range(n):
        player_names.append(input(f"Enter name of player {i + 1}:"))

    return player_names


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

            self.game_field.flip_card_on_field(player, position1)
            print(self.game_field)

            while True:
                try:
                    position2 = input(f"Enter position two [(0,0) - (2,3)]:")
                    position2 = eval(position2)
                    break
                except Exception as e:
                    print(f"Error: {e}. Please enter a valid position.")

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
        print("-" * 50)

    def flip_all_cards(self):
        for dic in self.game_field.field_hidden:
            for name, array in dic.items():
                for entry in array:
                    entry[2] = True

    def player_turn(self, player_name):
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

                self.game_field.flip_card_on_field(self.players[player_name], position)

                print(self.game_field)

            elif action == "cc":
                while True:
                    try:
                        position = eval(input("Choose position on field [(0,0) - (2,3)]:"))
                        break  # Wenn die Eingabe erfolgreich evaluiert werden konnte, beende die Schleife
                    except Exception as e:
                        print(f"Error: {e}. Please enter a valid position.")

                self.game_field.change_card_with_card_on_hand(self.players[player_name], position)
                self.players[player_name].put_card_on_discard_stack(self.carddeck)

                print(self.game_field)

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

                self.game_field.change_card_with_card_on_hand(self.players[player_name], position)
                self.players[player_name].put_card_on_discard_stack(self.carddeck)

                print(self.game_field)

    def run(self):
        end_player = False
        end = False

        while not self.end:

            for i, player_name in enumerate(self.player_turn_order):
                self.player_turn(player_name)
                end, name = self.game_field.check_end()

                if end and name in self.player_turn_order:
                    print(f"Player {name} ended the game. Everyone else has one more turn!")
                    self.player_turn_order.remove(name.strip())
                    end_player = True
                    break

            if end_player:
                for i, player_name in enumerate(self.player_turn_order):
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


class GameAgent(Game, Environment):

    def __init__(self, player_names: list, game_field_dimensions: tuple, carddeck: Carddeck):
        Game.__init__(self, player_names, game_field_dimensions, carddeck)

        Environment.__init__(self, player_names, carddeck, self.game_field)

        self.agent = RandomAgent(player_names, carddeck, self.game_field)

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

    def simulate_agent_games(self, n: int, output: bool = True):
        x = [i + 1 for i in range(n)]
        y = []

        for i in range(n):
            self.start(output)
            y.append(self.run_agent_alone(output))

        plt.plot(x, y)
        plt.grid()
        plt.xlabel("Game Run")
        plt.ylabel("Sum of cards")
        plt.title("Agent performance")
        plt.show()


class Simulation:

    def __init__(self):
        pass

    def simulate_agent_games(self, n: int, output: bool = True):
        results = []
        run_time = []
        start_simulation = time.time()

        for _ in tqdm(range(n)):
            carddeck = Carddeck()
            player_names = ["RandomAgent"]
            game_field_dimensions = (4, 3)
            G = GameAgent(player_names, game_field_dimensions, carddeck)

            start = time.time()
            G.start(output)
            results.append(G.run_agent_alone(output))
            run_time.append(time.time() - start)

        time_elapsed_simulation = time.time() - start_simulation

        time_average = sum(run_time) / n

        x = [i + 1 for i in range(n)]

        average = sum(results) / n

        # plt.plot(x, results, label=f"{G.agent.agent_name} results", marker="o", linestyle="")

        # plot average
        # plt.axhline(y=average, color="r", linestyle="-", label=f"Average: {average:.2f}")
        # plt.grid()
        # plt.xlabel("Game Run")
        # plt.ylabel("Sum of cards")
        # plt.title("Agent performance")
        # plt.legend()
        # plt.show()

        print(f"Simulation finished in {time_elapsed_simulation:.2f} seconds")
        print(f"Average time per run: {time_average} seconds")

        # plot histogram
        n, bins, _ = plt.hist(results, bins=20, label=f"{G.agent.agent_name} results")

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

if __name__ == "__main__":
    carddeck = Carddeck()

    # player_names = set_up_game()
    player_names = ["Nicolas", "Jolan"]

    # G1 = Game(player_names, (4, 3), carddeck)
    # G1.start()
    # G1.run()

    # G = GameAgent(player_names, (4, 3), carddeck)
    # G.start()
    # G.run_agent_alone()
    # G.simulate_agent_games(2)

    S = Simulation()
    S.simulate_agent_games(1000000, False)
