from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from Game.environment import Environment

import random


class RandomAgent(Environment):

    def __init__(self, player_names: list, agent_name: str = "RandomAgent"):
        super().__init__(player_names)
        self.player_names = player_names
        self.agent_name = agent_name

        # agent name because agent just act for its name and player act for name in player_names
        if agent_name not in player_names:
            raise ValueError("Agent name must be in player names!")

        self.state = self.init_state()
        # self.action_space = self.init_action_space()

    def act(self):
        if self.state["state_of_game"] == "beginning":
            # choose random positions
            position1 = (random.randint(0, 2), random.randint(0, 3))
            position2 = (random.randint(0, 2), random.randint(0, 3))

            return position1, position2

        else:

            actions = {1: "flip_card", 2: "pull_card_from_deck", 3: "pull_card_from_discard_stack", 4: "put_card_on_discard_stack"}
            action = actions[random.randint(1, 4)]
            position = (random.randint(0, 2), random.randint(0, 3))

            return action, position

class ReflexAgent:

    def __init__(self):
        pass

if __name__ == "__main__":
    R = RandomAgent(["Player1", "RandomAgent"])
    print(R.state)
