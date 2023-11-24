from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from Game.environment import Environment
# from seed import random_seed

import random, time

# random.seed(time.process_time())


class RandomAgent(Environment):

    def __init__(self, player_names: list, carddeck: Carddeck, gamefield: GameField, agent_name: str = "RandomAgent"):
        super().__init__(player_names, carddeck, gamefield)
        self.player_names = player_names
        self.agent_name = agent_name

        self.agent_player = self.players[self.agent_name]

        # agent name because agent just act for its name and player act for name in player_names
        if agent_name not in player_names:
            raise ValueError(f"Agent name ({self.agent_name}) must be in player names!")

        self.state = self.init_state()
        # self.action_space = self.init_action_space()

    def act(self, output: bool = True):

        if self.state[self.agent_name]["state_of_game"] == "beginning":
            # choose random positions
            all_positions = self.all_positions()
            position1, position2 = random.sample(all_positions, 2)

            action = "flip card"
            self.execute_action(self.agent_player, action, position1, output)
            self.execute_action(self.agent_player, action, position2, output)
            if output:
                print(f"Agent {self.agent_name} flipped cards at position {position1} and {position2}")
            self.state[self.agent_name]["last_action"] = action

            self.state[self.agent_name]["state_of_game"] = "running"

        elif self.state[self.agent_name]["state_of_game"] == "running":
            last_action = self.state[self.agent_name]["last_action"]
            legal_actions = self.legal_actions(last_action, self.agent_name)

            # choose random action and position
            action = random.choice(legal_actions)

            legal_positions = self.legal_positions(action, self.agent_name)

            if action in ["pull deck", "pull discard"]:
                self.execute_action(self.agent_player, action, None, output)
                if output:
                    print(f"Agent {self.agent_name} executed action {action}")
                    print(f"Agent {self.agent_name} card on hand: {self.agent_player.card_on_hand}")

            if action == "put discard":
                position = random.choice(legal_positions)
                self.execute_action(self.agent_player, action, position, output)
                if output:
                    print(f"Agent {self.agent_name} executed action {action} at position {position}")

            elif action == "change card":
                position = random.choice(legal_positions)
                self.execute_action(self.agent_player, action, position, output)
                if output:
                    print(f"Agent {self.agent_name} executed action {action} and flipped at position {position}")

        elif self.state[self.agent_name]["state_of_game"] == "finished":
            if output:
                print(f"Agent {self.agent_name} has finished the game!")

        else:
            raise ValueError("State of game is not valid!")


class ReflexAgent:

    def __init__(self):
        pass


if __name__ == "__main__":
    R = RandomAgent(["Player1", "RandomAgent"])
    print(R.state)
    print(R.act())
    print(R.state)
    print(R.act())
