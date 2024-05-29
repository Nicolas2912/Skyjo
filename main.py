import numpy as np

from Game.gamefield import GameField
from Game.player import Player
from Game.carddeck import Carddeck

from agents.simple_reflex_agent import RandomAgent2, ReflexAgent2
from Game.environment import Environment
from scipy.stats import norm

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import random, time, copy

from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


# random.seed(10)


def set_up_game():
    n = int(input("How many players?"))
    player_names = []
    for i in range(n):
        pass

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

        if len(self.env.players) > 0:
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
        if len(self.env.agents) > 0 and len(self.env.players) > 0:

            if player_name in self.env.players:
                self.turn_players(player_name)

            elif player_name in self.env.agents:

                if output:
                    print(f"Agent {player_name} turn!")

                last_action = self.env.state[player_name]["last_action"]
                legal_actions = self.env.legal_actions(last_action, player_name)

                agent = self.env.agents[player_name]

                # make first action
                action = agent.choose_random_action(legal_actions, output)
                self.env.execute_action(self.env.agents[player_name], action, None, output)

                # make second action
                legal_actions = self.env.legal_actions(action, player_name)
                action = agent.choose_random_action(legal_actions, output)
                legal_positions = self.env.legal_positions(action, player_name)
                pos = agent.choose_random_position(legal_positions, output)
                self.env.execute_action(self.env.agents[player_name], action, pos, output)

                self.env.update_state(player_name, action)
                if output:
                    self.env.print_game_field()

    def run_player_agent(self):
        end_player = False
        end = False

        while not self.end:

            for i, player_name in enumerate(self.player_turn_order):
                self.turn_player_agent(player_name)
                end, name = self.env.gamefield.check_end()

                if end and name in self.player_turn_order:
                    print(f"Player {name} ended the game. Everyone else has one more turn!")
                    self.player_turn_order.remove(name.strip())
                    end_player = True
                    break

            if end_player:
                for i, player_name in enumerate(self.player_turn_order):
                    self.turn_player_agent(player_name)

                    end, name = self.env.gamefield.check_end()

            if end and end_player:
                self.end = True
                self.__flip_all_cards()
                print("Final board:\n", self.env.gamefield)
                break

        print("Game ended!")

        # calculate winner
        card_sum = self.env.gamefield.calculate_sum_player(list(self.players_agents.values()),
                                                           self.env.carddeck.card_value_mapping)
        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

        print(f"The winner is: {list(card_sum.keys())[0]}, Sum: {list(card_sum.values())[0]}")

        # output of the other places
        for i, player_name in enumerate(list(card_sum.keys())[1:]):
            print(f"{i + 2}. place: {player_name}, Sum: {list(card_sum.values())[i + 1]}")

        print("=" * 50)

        return card_sum

    def start_agents(self, output: bool = True):
        if len(self.env.agents) > 0 and len(self.env.players) == 0:
            probs = []

            if output:
                print("Starting Skyjo!")

            for agent_name, agent in self.env.agents.items():
                legal_positions = self.env.legal_positions(player_name=agent_name)

                if isinstance(agent, RandomAgent2):
                    pos1, pos2 = agent.flip_cards_start(legal_positions, output)
                    self.env.execute_action(agent, "flip card", pos1, output)
                    self.env.execute_action(agent, "flip card", pos2, output)
                    prob = self.env.state["probabilities"]
                    probs.append(prob)

                    if output:
                        self.env.print_game_field()

                elif isinstance(agent, ReflexAgent2):
                    pos1, pos2 = agent.flip_cards_start(legal_positions, self.env, output)
                    self.env.execute_action(agent, "flip card", pos1, output)
                    self.env.execute_action(agent, "flip card", pos2, output)
                    prob = self.env.calc_probabilities()
                    probs.append(prob)

                    if output:
                        self.env.print_game_field()

            # choose agent thats starts. That agent with the lowest card sum on field starts
            card_sum = self.env.gamefield.calculate_sum_player(list(self.players_agents.values()),
                                                               self.env.carddeck.card_value_mapping)

            # sort card_sum dictionary by value
            card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

            first_agent = list(card_sum.keys())[0]
            if output:
                print(f"Agent {first_agent} starts!")

            # create agent turn order
            self.player_turn_order.append(first_agent)
            for agent in self.players_agents.values():
                if agent.name != first_agent:
                    self.player_turn_order.append(agent.name)

            if output:
                print(f"Agent turn order: {self.player_turn_order}\n")
                print("-" * 50)

        else:
            raise ValueError(
                f"There must be at least one agent and no players! \nAgent: {self.env.agents}\nPlayer: {self.env.players}")

        return probs

    def turn_agents(self, agent_name, output: bool = True):
        probs = []
        if len(self.env.agents) > 0 and len(self.env.players) == 0:

            if output:
                print(f"Agent {agent_name} turn!")

            last_action = self.env.state[agent_name]["last_action"]
            legal_actions = self.env.legal_actions(last_action, agent_name)

            agent = self.env.agents[agent_name]

            if isinstance(agent, RandomAgent2):
                # make first action
                action = agent.choose_random_action(legal_actions, output)
                self.env.execute_action(self.env.agents[agent_name], action, None, output)

                # make second action
                legal_actions = self.env.legal_actions(action, agent_name)
                action = agent.choose_random_action(legal_actions, output)
                legal_positions = self.env.legal_positions(action, agent_name)
                pos = agent.choose_random_position(legal_positions, output)
                self.env.execute_action(self.env.agents[agent_name], action, pos, output)

                prob = self.env.state["probabilities"]

                if output:
                    self.env.print_game_field()

            elif isinstance(agent, ReflexAgent2):

                action, action1, pos = agent.perform_action(self.env)
                self.env.execute_action(self.env.agents[agent_name], action, None, output)
                self.env.execute_action(self.env.agents[agent_name], action1, pos, output)

                prob = self.env.state["probabilities"]

                if output:
                    print(f"Agent {agent_name} performed action {action} and {action1} at position {pos}!")
                    self.env.print_game_field()

        return prob

    def run_agents(self, output: bool = True, end_output: bool = True):
        end_agents = False
        end = False
        probs = []

        while not self.end:

            for agent_name in self.player_turn_order:
                prob_turn = self.turn_agents(agent_name, output)
                # print heatmap animated of probabilities after every turn
                probs.append(prob_turn)

                end, name = self.env.gamefield.check_end()

                if end and name in self.player_turn_order:
                    if output and not end_output:
                        print(f"Agent {name} ended the game. Everyone else has one more turn!")
                    self.player_turn_order.remove(name.strip())
                    end_agents = True
                    break

            if end_agents:
                for agent_name in self.player_turn_order:
                    prob_turn = self.turn_agents(agent_name, output)
                    probs.append(prob_turn)

                    end, name = self.env.gamefield.check_end()

            if end and end_agents:
                self.end = True
                self.__flip_all_cards()
                probs_end = self.env.calc_probabilities()
                probs.append(probs_end)
                if not output and end_output:
                    print("Final board:\n", self.env.gamefield)
                    # print(f"Final probabilities: {probs}")
                    print("-" * 50)
                break

        if output:
            print("Game ended!")

        # calculate winner
        card_sum = self.env.gamefield.calculate_sum_player(list(self.players_agents.values()),
                                                           self.env.carddeck.card_value_mapping)

        # sort card_sum dictionary by value
        card_sum = {k: v for k, v in sorted(card_sum.items(), key=lambda item: item[1])}

        if output:
            print(f"The winner is: {list(card_sum.keys())[0]}, Sum: {list(card_sum.values())[0]}")

        if output:
            # output of the other places
            for i, agent_name in enumerate(list(card_sum.keys())[1:]):
                print(f"{i + 2}. place: {agent_name}, Sum: {list(card_sum.values())[i + 1]}")

            print("=" * 50)

        return card_sum, probs


class Simulation:

    def __init__(self, agent_names: list):
        self.agent_names = agent_names
        self.agents = []

    def simulate_agent_games(self, n: int, output: bool = True, end_output: bool = True):

        start_simulation = time.time()

        overall_results = {name: [] for name in self.agent_names}
        time_results = []
        probs = []

        for _ in tqdm(range(n)):
            carddeck = Carddeck()
            game_field_dimensions = (4, 3)
            agents = []
            for agent_name in self.agent_names:
                agent = None
                if agent_name == "RandomAgent":
                    agent = RandomAgent2(agent_name, carddeck, game_field_dimensions)
                elif agent_name == "ReflexAgent":
                    agent = ReflexAgent2(agent_name, carddeck, game_field_dimensions)
                agents.append(agent)

            gamefield = GameField(4, 3, agents, carddeck)
            environment = Environment(gamefield)
            game = Game2(environment)

            probs_start = game.start_agents(output)
            probs.append(probs_start)

            result, probs_turn = game.run_agents(output, end_output)

            agent_names_result = list(result.keys())
            for agent_name in self.agent_names:
                if agent_name in agent_names_result:
                    overall_results[agent_name].append(result[agent_name])

            probs.append(probs_turn)
            time_elapsed_simulation = time.time() - start_simulation
            time_results.append(time_elapsed_simulation)

        print(f"Average time per run: {np.mean(time_results):.2f} seconds")

        # plot histogram
        # Histogram
        # fig, axs = plt.subplots(1, 4, figsize=(10, 5))
        #
        # for agent_name, results in overall_results.items():
        #     if agent_name == "RandomAgent":
        #         color = "blue"
        #         label = "RandomAgent results"
        #     elif agent_name == "ReflexAgent":
        #         color = "orange"
        #         label = "ReflexAgent results"
        #
        #     n, bins, _ = axs[0].hist(results, bins=20, label=f"{label}", color=color, edgecolor='black')
        #     axs[0].legend(loc='upper right')
        #
        #     mean, std = np.mean(results), np.std(results)
        #
        #     print(f"Agent: {agent_name}")
        #     print(f"Mean: {mean:.2f}, Std: {std:.2f}")
        #
        #     # plot pdf
        #     x = np.linspace(min(results), max(results), 1000)
        #     p = norm.pdf(x, mean, std)
        #     p *= n.max() / p.max()
        #
        #     axs[0].plot(x, p, linewidth=4, label=f'Normal Distribution {agent_name}', color="black")
        #
        # axs[0].set_xlabel("Sum of cards")
        # axs[0].set_ylabel("Frequency")
        # axs[0].set_title("Agent performance")
        #
        # # Pie-Chart
        # points_random = overall_results["RandomAgent"]
        # points_reflex = overall_results["ReflexAgent"]
        #
        # winnings = {"RandomAgent": 0, "ReflexAgent": 0, "Draw": 0}
        #
        # for p_random, p_reflex in zip(points_random, points_reflex):
        #     if p_random < p_reflex:
        #         winnings["RandomAgent"] += 1
        #     elif p_random > p_reflex:
        #         winnings["ReflexAgent"] += 1
        #     else:
        #         winnings["Draw"] += 1
        #
        # labels = winnings.keys()
        # values = winnings.values()
        #
        # axs[1].pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
        #            colors=['blue', 'orange', 'lightcoral'])
        #
        # axs[1].set_title("Agent winnings")
        #
        # probs_all = probs[0] + probs[1]
        #
        # probs_new = {}
        # for dic in probs_all:
        #     for key, value in dic.items():
        #         if key in probs_new.keys():
        #             probs_new[key].append(value)
        #         else:
        #             probs_new[key] = []
        #             probs_new[key].append(value)
        #
        # # Extrahiere die eindeutigen Keys und die Werte für den ersten Zeitpunkt
        # keys = list(probs_new.keys())
        # current_values = [probs_new[key] for key in keys]
        # mean_values = [np.mean(probs_new[key]) for key in keys]
        # heatmap = axs[2].imshow(np.array(current_values).T, cmap='jet', interpolation='nearest', aspect='auto',
        #                     animated=True)
        #
        # # bar plot of mean values
        # axs[3].bar(keys, mean_values, color="brown", edgecolor="black")
        #
        # # heatmap_mean = axs[3].imshow(np.array(mean_values).T, cmap='jet', interpolation='nearest', aspect='auto',
        # #                     animated=True)
        #
        # # Beschriftungen hinzufügen
        # axs[2].set_xlabel('Keys')
        # axs[2].set_ylabel('Zeitpunkt')
        # axs[2].set_title('Animierte Heatmap der Daten aus probs_new')
        #
        # # Setze die x-Ticks, um alle Keys anzuzeigen
        # axs[2].set_xticks(np.arange(len(keys)))
        # axs[2].set_xticklabels(keys)
        #
        # every_n = 50
        # y_ticks_positions = np.arange(0, len(max(current_values, key=len)), every_n)
        # axs[2].set_yticks(y_ticks_positions)
        # axs[2].set_yticklabels(np.arange(0, len(max(current_values, key=len)), every_n))
        #
        # # add colorbar
        # fig.colorbar(heatmap, ax=axs[2])
        #
        # # Funktion für die Animation
        # def update(frame):
        #     current_values = [probs_new[key][:frame + 1] for key in keys]
        #     heatmap.set_array(np.array(current_values).T)
        #     return heatmap,
        #
        # # Erstelle die Animation
        # # animation = FuncAnimation(fig, update, frames=len(max(current_values, key=len)), interval=100, repeat=False)
        #
        # plt.show()

        fig2, axs2 = plt.subplots(nrows=1, ncols=3)

        probs_all = []
        for i in range(len(probs)):
            probs_all.extend(probs[i])

        probs_new = {}
        for dic in probs_all:
            for key, value in dic.items():
                if key in probs_new.keys():
                    probs_new[key].append(value)
                else:
                    probs_new[key] = []
                    probs_new[key].append(value)

        # Extrahiere die eindeutigen Keys und die Werte für den ersten Zeitpunkt
        keys = list(probs_new.keys())
        keys = sorted(keys)
        current_values = [probs_new[key] for key in keys]
        mean_values = [np.mean(probs_new[key]) for key in keys]

        heatmap = axs2[0].imshow(np.array(current_values).T, cmap='jet', interpolation='nearest', aspect='auto',
                                 animated=True)

        # set x ticks
        axs2[0].set_xticks(np.arange(len(keys)))
        axs2[0].set_xticklabels(keys)

        # text in plot
        # for i in range(len(keys)):
        #     for j in range(len(current_values[i])):
        #         axs2.text(i, j, f"{current_values[i][j]:.5f}", ha="center", va="center", color="black")

        fig2.colorbar(heatmap, ax=axs2[0])

        # bar chart of mean of probabilities
        axs2[1].bar(keys, mean_values, color="brown", edgecolor="black")

        # set x ticks
        axs2[1].set_xticks(np.arange(len(keys)))
        axs2[1].set_xticklabels(keys)

        # set x label
        axs2[1].set_xlabel("Cards")
        axs2[1].set_ylabel("Mean of probabilities")

        # set title
        axs2[0].set_title("Heatmap of probabilities")
        axs2[1].set_title("Mean of probabilities")

        axs2[2].boxplot(current_values, labels=keys, vert=True, patch_artist=True)

        plt.show()


if __name__ == "__main__":
    # carddeck = Carddeck()
    # player = Player("Nicolas", carddeck, (4, 3))
    # player1 = Player("Linus", carddeck, (4, 3))
    # agent = RandomAgent2("RandomAgent", carddeck, (4, 3))
    # # agent1 = ReflexAgent2("ReflexAgent", carddeck, (4, 3))
    # #
    # gamefield = GameField(4, 3, [player, agent], carddeck)
    # environment = Environment(gamefield)
    # #
    # game = Game2(environment)
    # game.start_agents(True)
    # game.run_agents()

    S = Simulation(["ReflexAgent", "ReflexAgent"])
    S.simulate_agent_games(1000, False, False)
