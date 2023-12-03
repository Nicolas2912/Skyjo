from Game.player import Player
from Game.carddeck import Carddeck
from Game.gamefield import GameField
from Game.environment import Environment
# from seed import random_seed

import random, time

from copy import copy
from collections import Counter


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
            card_on_hand_loc = self.card_on_hand
            self.card_on_hand = None
            if output:
                print(f"Agent {self.name} put card {card_on_hand_loc} on discard stack!")
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

        card_mapping = self.card_value_mapping
        cards_flipped = {}
        for entry in field:
            if entry[2]:
                cards_flipped[entry[1]] = card_mapping[str(entry[0])]

        card_threshold = 4

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
            pos_card_next_positions = [pos for pos in pos_card_next_positions if pos in env.legal_positions(player_name=self.name)]

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

                card_on_hand_future = env.carddeck.cards[0]

                if card_mapping[str(card_on_hand_future)] < max(cards_flipped.values()):
                    action1 = "change card"
                    pos_max = max(cards_flipped, key=cards_flipped.get)
                    return action, action1, pos_max
                elif card_on_hand_future in list(cards_flipped.values()):
                    pos_card = [pos for pos, card in cards_flipped.items() if card == card_on_hand_future]
                    pos_card = pos_card[0]
                    pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                               (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                    pos_card_next_positions = [pos for pos in pos_card_next_positions if
                                               pos in env.legal_positions(player_name=self.name)]
                    pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                                pos not in cards_flipped.keys()]

                    if len(pos_card_next_positions_not_flipped_list) > 0:
                        pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                        action1 = "change card"
                        return action, action1, pos_card_next_positions_flipped
                    else:
                        if card_mapping[str(card_on_hand_future)] <= card_threshold:
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
                    if card_mapping[str(card_on_hand_future)] <= card_threshold:
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
            action = "pull deck"

            card_on_hand_future = env.carddeck.cards[0]

            for pos, value in cards_flipped.items():
                cards_flipped[pos] = card_mapping[str(value)]

            if card_mapping[str(card_on_hand_future)] < max(cards_flipped.values()):
                action1 = "change card"
                pos_max = max(cards_flipped, key=cards_flipped.get)
                return action, action1, pos_max
            elif card_on_hand_future in list(cards_flipped.values()):
                pos_card = [pos for pos, card in cards_flipped.items() if card == card_on_hand_future]
                pos_card = pos_card[0]
                pos_card_next_positions = [(pos_card[0] + 1, pos_card[1]), (pos_card[0] - 1, pos_card[1]),
                                           (pos_card[0], pos_card[1] + 1), (pos_card[0], pos_card[1] - 1)]
                pos_card_next_positions = [pos for pos in pos_card_next_positions if pos in env.legal_positions(player_name=self.name)]
                pos_card_next_positions_not_flipped_list = [pos for pos in pos_card_next_positions if
                                                            pos not in cards_flipped.keys()]
                if len(pos_card_next_positions_not_flipped_list) > 0:
                    pos_card_next_positions_flipped = random.choice(pos_card_next_positions_not_flipped_list)
                    action1 = "change card"
                    return action, action1, pos_card_next_positions_flipped
                else:
                    if card_mapping[str(card_on_hand_future)] <= card_threshold:
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
                if card_mapping[str(card_on_hand_future)] <= card_threshold:
                    action1 = "change card"
                    legal_positions = env.legal_positions(action1, self.name)
                    pos = random.choice(legal_positions)
                    return action, action1, pos
                else:
                    action1 = "put discard"
                    legal_positions = env.legal_positions(action1, self.name)
                    pos = random.choice(legal_positions)
                    return action, action1, pos

    def perform_action_probs(self, env: Environment):
        pass

    def calculate_probabilities(self, env: Environment):
        field = env.state[self.name]["field"]
        discard_stack = env.state["discard_stack"]

        cards = self.init_carddeck()
        number_all_cards = len(cards)

        probabilities = {}

        cards_counter = Counter(cards)
        cards_counter = sorted(cards_counter.items(), key=lambda x: x[1], reverse=False)
        cards_counter = dict(cards_counter)

        for card, count in cards_counter.items():
            probabilities[str(card)] = count / number_all_cards

        # update probabilities with card in discard stack
        card_in_discard_stack = discard_stack[-1]
        probabilities[str(card_in_discard_stack)] = (cards_counter[card_in_discard_stack] - 1) / (number_all_cards - 1)

        print(f"Card on discard stack: {card_in_discard_stack}")
        print(probabilities)

        # TODO: Hier weitermachen! Anzahl der Karten, die im Spiel sind (number_all_cards) muss variabel sein, da Spiel sich ändert.

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
            card_on_hand_loc = self.card_on_hand
            self.card_on_hand = None
            if output:
                print(f"Agent {self.name} put card {card_on_hand_loc} on discard stack!")
        else:
            raise ValueError("Agent has no card on hand! Cannot put card on discard stack!")

    def pull_card_from_deck(self, carddeck: Carddeck, output: bool = True):
        try:
            card_on_hand = carddeck.cards[0]
        except Exception as e:
            raise ValueError("Carddeck is empty! Cannot pull card from empty carddeck!")

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


if __name__ == "__main__":
    agent_name = "RandomAgent"
    agent_name1 = "RandomAgent1"

    c = Carddeck()

    reflexagent = ReflexAgent2(agent_name, c, (4, 3))

    gamefield = GameField(4, 3, [reflexagent], c)

    env = Environment(gamefield)

    reflexagent.calculate_probabilities(env)
