from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from Game.environment import Environment

import random

random.seed(42)


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

    def act(self):
        if self.state[self.agent_name]["state_of_game"] == "beginning":
            # choose random positions
            position1 = (random.randint(0, 2), random.randint(0, 3))
            position2 = (random.randint(0, 2), random.randint(0, 3))

            action = "flip card"
            self.execute_action(self.agent_player, action, position1)
            self.execute_action(self.agent_player, action, position2)
            self.state[self.agent_name]["last_action"] = action

        elif self.state[self.agent_name]["state_of_game"] == "running":
            last_action = self.state[self.agent_name]["last_action"]

            legal_actions = self.legal_actions(last_action)
            legal_positions = self.legal_positions()

            # choose random action and position
            action = random.choice(legal_actions)

            if action in ["pull deck", "pull discard"]:
                self.execute_action(self.agent_player, action)

            if action == "put discard":
                position = random.choice(legal_positions)
                self.execute_action(self.agent_player, action, position)

            elif action == "change card":
                position = random.choice(legal_positions)
                self.execute_action(self.agent_player, action, position)

        else:
            raise ValueError("State of game is not valid or game is finished!")


class ReflexAgent:

    def __init__(self):
        pass


if __name__ == "__main__":
    R = RandomAgent(["Player1", "RandomAgent"])
    print(R.state)
    print(R.act())
    print(R.state)
    print(R.act())
