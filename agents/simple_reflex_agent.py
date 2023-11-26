from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from Game.environment import Environment
# from seed import random_seed

import random, time


# random.seed(time.process_time())

class RandomAgent2(Carddeck):

    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        super().__init__()
        self.name = name

        self.player_cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])

        self.card_on_hand = None

    def flip_cards_start(self, positions: list, output: bool = True):
        pos1, pos2 = random.sample(positions, 2)

        if output:
            print(f"Agent {self.name} flipped cards at position {pos1} and {pos2}")

        return pos1, pos2

    def flip_card(self, positions: list, output: bool = True):
        pos = random.choice(positions)

        if output:
            print(f"Agent {self.name} flipped card at position {pos}")

        return pos

    def choose_random_action(self, legal_actions: list, output: bool = True):
        action = random.choice(legal_actions)

        if output:
            print(f"Agent {self.name} executed action {action}")

        return action

    def choose_random_position(self, legal_positions: list, output: bool = True):
        pos = random.choice(legal_positions)

        if output:
            print(f"Agent {self.name} chose position {pos}")

        return pos

    def put_card_on_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if self.card_on_hand is not None:
            carddeck.discard_stack.append(self.card_on_hand)
            self.card_on_hand = None
            if output:
                print(f"Agent {self.name} put card on discard stack!")
        else:
            raise ValueError("Agent has no card on hand! Cannot put card on discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck, output: bool = True):
        try:
            card_on_hand = carddeck.cards[0]
        except Exception as e:
            print(carddeck.cards)
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        if output:
            print(f"Agent {self.name} pulled card {self.card_on_hand} from deck!")
        return card_on_hand

    def pull_card_from_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                self.card_on_hand = carddeck.discard_stack.pop()
                if output:
                    print(f"Agent {self.name} pulled card {self.card_on_hand} from discard stack!")
            else:
                raise ValueError("Agent already has a card on hand! Cannot have more than one card on hand!")
        else:
            raise ValueError("Discard stack is empty! Cannot pull card from empty discard stack!")


class ReflexAgent2(Carddeck):

    def __init__(self, name: str, carddeck: Carddeck, game_field_dimensions: tuple):
        super().__init__()

        self.name = name

        self.player_cards = random.sample(carddeck.cards, game_field_dimensions[0] * game_field_dimensions[1])

        self.card_on_hand = None

    def flip_cards_start(self, positions: list, env: Environment, output: bool = True):

        pos1 = random.choice(positions)

        pos1_next = [(pos1[0] + 1, pos1[1]), (pos1[0] - 1, pos1[1]),
                     (pos1[0], pos1[1] + 1), (pos1[0], pos1[1] - 1)]

        all_positions = env.all_positions()
        pos1_next = [pos for pos in pos1_next if pos in all_positions]

        pos2 = random.choice(pos1_next)

        if output:
            print(f"Agent {self.name} flipped cards at position {pos1} and {pos2}")

        return pos1, pos2

    def perform_action(self, env: Environment):
        discard_stack = env.state["discard_stack"]
        field = env.state[self.name]["field"]
        last_action = env.state[self.name]["last_action"]

        card_mapping = self.card_value_mapping
        cards_flipped = {}
        for entry in field:
            if entry[2]:
                cards_flipped[entry[1]] = entry[0]

        card_threshold = 5

        try:
            card_mapping[str(discard_stack[-1])] < int(max(cards_flipped.values()))
        except Exception:
            card_m = card_mapping[str(discard_stack[-1])]
            max_cards = max(list(cards_flipped.values()))
            print(card_mapping[str(discard_stack[-1])])
            print(max(cards_flipped.values()))

        # check if card on discard stack is lower than cards flipped
        if card_mapping[str(discard_stack[-1])] < int(max(cards_flipped.values())):
            action = "pull discard"
            action1 = "change card"
            pos_max = max(cards_flipped, key=cards_flipped.get)

            return action, action1, pos_max

        elif card_mapping[str(discard_stack[-1])] in list(cards_flipped.values()):
            pos_card = [pos for pos, card in cards_flipped.items() if card == card_mapping[str(discard_stack[-1])]]
            pos_card = pos_card[0]
            pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                       (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
            pos_card_next_positions = [pos for pos in pos_card_next_positions if pos in env.all_positions()]

            # check if card on position next to card is flipped or not
            pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                        pos not in cards_flipped.keys()]
            if len(pos_card_next_positions_not_flipped_list) > 0:
                pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                action = "pull discard"
                action1 = "change card"
                return action, action1, pos_card_next_positions_flipped
            else:
                action = "pull deck"

                card_on_hand = env.state[self.name]["player_hand"]

                if card_mapping[str(card_on_hand)] < max(cards_flipped.values()):
                    action1 = "change card"
                    pos_max = max(cards_flipped, key=cards_flipped.get)
                    return action, action1, pos_max
                elif card_on_hand in list(cards_flipped.values()):
                    pos_card = [pos for pos, card in cards_flipped.items() if card == card_on_hand]
                    pos_card = pos_card[0]
                    pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                               (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                    pos_card_next_positions = [pos for pos in pos_card_next_positions if
                                               pos in env.all_positions()]
                    pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                                pos not in cards_flipped.keys()]

                    if len(pos_card_next_positions_not_flipped_list) > 0:
                        pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                        action1 = "change card"
                        return action, action1, pos_card_next_positions_flipped
                    else:
                        if card_mapping[str(card_on_hand)] <= card_threshold:
                            action1 = "change card"
                            legal_positions = env.legal_positions(action1, self.name)
                            pos = random.choice(legal_positions)
                            return action, action1, pos
                        else:
                            action1 = "put discard"
                            legal_positions = env.legal_positions(action1, self.name)
                            pos = random.choice(legal_positions)
                            return action, action1, pos
                else:
                    if card_mapping[str(card_on_hand)] <= card_threshold:
                        action1 = "change card"
                        legal_positions = env.legal_positions(action1, self.name)
                        pos = random.choice(legal_positions)
                        return action, action1, pos
                    else:
                        action1 = "put discard"
                        legal_positions = env.legal_positions(action1, self.name)
                        pos = random.choice(legal_positions)
                        return action, action1, pos

    def flip_card(self, positions: list, output: bool = True):
        pos = random.choice(positions)

        if output:
            print(f"Agent {self.name} flipped card at position {pos}")

        return pos

    def choose_random_action(self, legal_actions: list, output: bool = True):
        action = random.choice(legal_actions)

        if output:
            print(f"Agent {self.name} executed action {action}")

        return action

    def choose_random_position(self, legal_positions: list, output: bool = True):
        pos = random.choice(legal_positions)

        if output:
            print(f"Agent {self.name} chose position {pos}")

        return pos

    def put_card_on_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if self.card_on_hand is not None:
            carddeck.discard_stack.append(self.card_on_hand)
            self.card_on_hand = None
            if output:
                print(f"Agent {self.name} put card on discard stack!")
        else:
            raise ValueError("Agent has no card on hand! Cannot put card on discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck, output: bool = True):
        try:
            card_on_hand = carddeck.cards[0]
        except Exception as e:
            print(carddeck.cards)
        carddeck.cards.remove(card_on_hand)
        self.card_on_hand = card_on_hand
        if output:
            print(f"Agent {self.name} pulled card {self.card_on_hand} from deck!")
        return card_on_hand

    def pull_card_from_discard_stack(self, carddeck: Carddeck, output: bool = True):
        if len(carddeck.discard_stack) > 0:
            if self.card_on_hand is None:
                # get last card from discard stack
                self.card_on_hand = carddeck.discard_stack.pop()
                if output:
                    print(f"Agent {self.name} pulled card {self.card_on_hand} from discard stack!")
            else:
                raise ValueError("Agent already has a card on hand! Cannot have more than one card on hand!")
        else:
            raise ValueError("Discard stack is empty! Cannot pull card from empty discard stack!")


class ReflexAgent(Environment):

    def __init__(self, player_names: list, carddeck: Carddeck, gamefield: GameField, agent_name: str = "ReflexAgent"):
        super().__init__(player_names, carddeck, gamefield)
        self.player_names = player_names
        self.agent_name = agent_name

        self.agent_player = self.players[self.agent_name]

        # agent name because agent just act for its name and player act for name in player_names
        if agent_name not in player_names:
            raise ValueError(f"Agent name ({self.agent_name}) must be in player names!")

        self.state = self.init_state()

    def act(self, output: bool = True):
        if self.state[self.agent_name]["state_of_game"] == "beginning":
            # choose random positions
            all_positions = self.all_positions()
            position1 = random.choice(all_positions)

            # choose next position on random but only a position that is next to the first position (up or down or left or right) and is not position1
            position1_next = [(position1[0] + 1, position1[1]), (position1[0] - 1, position1[1]),
                              (position1[0], position1[1] + 1), (position1[0], position1[1] - 1)]
            position1_next = [pos for pos in position1_next if pos in all_positions]
            position2 = random.choice(position1_next)

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

            # choose action
            card_mapping = self.carddeck.card_value_mapping
            field = self.state[self.agent_name]["field"]
            cards_flipped = {}
            for entry in field:
                if entry[2]:
                    cards_flipped[entry[1]] = entry[0]

            for pos, value in cards_flipped.items():
                cards_flipped[pos] = card_mapping[str(value)]

            card_threshold = -2

            # check if card on discard stack is lower than cards flipped
            discard_stack = self.state["discard_stack"]
            if card_mapping[str(discard_stack[-1])] < max(cards_flipped.values()):
                action = "pull discard"
                self.execute_action(self.agent_player, action, None, output)
                action = "change card"
                pos_max = max(cards_flipped, key=cards_flipped.get)
                self.execute_action(self.agent_player, action, pos_max, output)

            elif card_mapping[str(discard_stack[-1])] in list(cards_flipped.values()):
                pos_card = [pos for pos, card in cards_flipped.items() if card == card_mapping[str(discard_stack[-1])]]
                pos_card = pos_card[0]
                pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                           (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                pos_card_next_positions = [pos for pos in pos_card_next_positions if pos in self.all_positions()]

                # check if card on position next to card is flipped or not
                pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                            pos not in cards_flipped.keys()]
                if len(pos_card_next_positions_not_flipped_list) > 0:
                    pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                    action = "pull discard"
                    self.execute_action(self.agent_player, action, None, output)
                    action = "change card"
                    self.execute_action(self.agent_player, action, pos_card_next_positions_flipped, output)
                else:
                    action = "pull deck"
                    self.execute_action(self.agent_player, action, None, output)

                    card_on_hand = self.state[self.agent_name]["player_hand"]

                    if card_mapping[str(card_on_hand)] < max(cards_flipped.values()):
                        action = "change card"
                        pos_max = max(cards_flipped, key=cards_flipped.get)
                        self.execute_action(self.agent_player, action, pos_max, output)
                    elif card_on_hand in list(cards_flipped.values()):
                        pos_card = [pos for pos, card in cards_flipped.items() if card == card_on_hand]
                        pos_card = pos_card[0]
                        pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                                   (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                        pos_card_next_positions = [pos for pos in pos_card_next_positions if
                                                   pos in self.all_positions()]
                        pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                                    pos not in cards_flipped.keys()]
                        if len(pos_card_next_positions_not_flipped_list) > 0:
                            pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                            action = "change card"
                            self.execute_action(self.agent_player, action, pos_card_next_positions_flipped, output)
                        else:
                            if card_mapping[str(card_on_hand)] <= card_threshold:
                                action = "change card"
                                legal_positions = self.legal_positions(action, self.agent_name)
                                pos = random.choice(legal_positions)
                                self.execute_action(self.agent_player, action, pos, output)
                            else:
                                action = "put discard"
                                legal_positions = self.legal_positions(action, self.agent_name)
                                pos = random.choice(legal_positions)
                                self.execute_action(self.agent_player, action, pos, output)
                    else:
                        if card_mapping[str(card_on_hand)] <= card_threshold:
                            action = "change card"
                            legal_positions = self.legal_positions(action, self.agent_name)
                            pos = random.choice(legal_positions)
                            self.execute_action(self.agent_player, action, pos, output)
                        else:
                            action = "put discard"
                            legal_positions = self.legal_positions(action, self.agent_name)
                            pos = random.choice(legal_positions)
                            self.execute_action(self.agent_player, action, pos, output)

            else:
                action = "pull deck"
                self.execute_action(self.agent_player, action, None, output)

                card_on_hand = self.state[self.agent_name]["player_hand"]

                # print(f"card on hand: {card_on_hand}")
                # print(f"max cards flipped: {max(cards_flipped.values())}")

                for pos, value in cards_flipped.items():
                    cards_flipped[pos] = card_mapping[str(value)]

                if card_mapping[str(card_on_hand)] < max(cards_flipped.values()):
                    action = "change card"
                    pos_max = max(cards_flipped, key=cards_flipped.get)
                    self.execute_action(self.agent_player, action, pos_max, output)
                elif card_on_hand in list(cards_flipped.values()):
                    pos_card = [pos for pos, card in cards_flipped.items() if card == card_on_hand]
                    pos_card = pos_card[0]
                    pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                               (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                    pos_card_next_positions = [pos for pos in pos_card_next_positions if pos in self.all_positions()]
                    pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                                pos not in cards_flipped.keys()]
                    if len(pos_card_next_positions_not_flipped_list) > 0:
                        pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                        action = "change card"
                        self.execute_action(self.agent_player, action, pos_card_next_positions_flipped, output)
                    else:
                        if card_mapping[str(card_on_hand)] <= card_threshold:
                            action = "change card"
                            legal_positions = self.legal_positions(action, self.agent_name)
                            pos = random.choice(legal_positions)
                            self.execute_action(self.agent_player, action, pos, output)
                        else:
                            action = "put discard"
                            legal_positions = self.legal_positions(action, self.agent_name)
                            pos = random.choice(legal_positions)
                            self.execute_action(self.agent_player, action, pos, output)
                else:
                    if card_mapping[str(card_on_hand)] <= card_threshold:
                        action = "change card"
                        legal_positions = self.legal_positions(action, self.agent_name)
                        pos = random.choice(legal_positions)
                        self.execute_action(self.agent_player, action, pos, output)
                    else:
                        action = "put discard"
                        legal_positions = self.legal_positions(action, self.agent_name)
                        pos = random.choice(legal_positions)
                        self.execute_action(self.agent_player, action, pos, output)

            if output:
                print(f"Agent {self.agent_name} executed action {action}")
                print()
                self.print_game_field()


if __name__ == "__main__":
    agent_name = "RandomAgent"
    agent_name1 = "RandomAgent1"

    c = Carddeck()

    randomagent = RandomAgent2(agent_name, c, (4, 3))

    print(type(randomagent))
