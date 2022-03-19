import numpy as np
from random import shuffle
import time
import sys
import copy
#
#



# def rank(hand: List[str]) -> int:
#     ranks = {
#         'KK': 1,
#         'QQ': 2,
#         'JJ': 3,
#         'KQ': 4, 'QK': 4,
#         'KJ': 5, 'JK': 5,
#         'QJ': 6, 'JQ': 6
#     }
#
#     cards = hand[0][0] + hand[1][0]
#     return ranks[cards]
#
#
# class GameState(ABC):
#     @abstractmethod
#     def is_terminal(self) -> bool:
#         pass
#
#     @abstractmethod
#     def get_payoffs(self) -> List[int]:
#         pass
#
#     @abstractmethod
#     def get_actions(self, player: Player) -> List[Action]:
#         pass
#
#     @abstractmethod
#     def handle_action(self, player: Player, action: Action) -> GameState:
#         pass
#
#     @abstractmethod
#     def get_active_player(self) -> Player:
#         pass
#
#     @abstractmethod
#     def get_index(self, player: Player) -> int:
#         pass
#
#     @abstractmethod
#     def get_representation(self) -> str:
#         pass
#
#
#
#









class Kunh:

    def __init__(self):
        self.nodeMap = {}
        self.expected_game_value = 0
        self.n_cards = 6
        self.nash_equilibrium = dict()
        self.current_player = 0
        self.deck = np.array(['1', '1', '2', '2', '3', '3'])
        # self.n_actions = 2


    def train(self, n_iterations=50000):
        expected_game_value = 0
        for _ in range(n_iterations):
            shuffle(self.deck)
            expected_game_value += self.cfr(History(), 1, 1)
            for _, v in self.nodeMap.items():
                v.update_strategy()

        expected_game_value /= n_iterations
        display_results(expected_game_value, self.nodeMap)

    def cfr(self, history, pr_1, pr_2):
        # n = len(history.history)
        # is_player_1 = n % 2 == 0
        is_player_1 = history.player_1
        player_card = self.deck[0] if is_player_1 else self.deck[1]
        community_card = self.deck[2]

        if self.is_terminal(history):
            card_player = self.deck[0] if is_player_1 else self.deck[1]
            card_opponent = self.deck[1] if is_player_1 else self.deck[0]
            reward = self.get_reward(history.history, card_player, card_opponent, community_card)
            return reward

        node = self.get_node(player_card, history)
        strategy = node.strategy

        # Counterfactual utility per action.
        action_utils = np.zeros(node.n_actions)

        for act in range(node.n_actions):
            # next_history = history + node.action_dict[act]
            next_history = history.add_history(node.action_dict[act])
            if is_player_1:
                action_utils[act] = -1 * self.cfr(next_history, pr_1 * strategy[act], pr_2)
            else:
                action_utils[act] = -1 * self.cfr(next_history, pr_1, pr_2 * strategy[act])

        # Utility of information set.
        util = sum(action_utils * strategy)
        regrets = action_utils - util
        if is_player_1:
            node.reach_pr += pr_1
            node.regret_sum += pr_2 * regrets
        else:
            node.reach_pr += pr_2
            node.regret_sum += pr_1 * regrets

        return util

    @staticmethod
    def is_terminal(history):
        sec_rnd = history.round == 3

        if (sec_rnd and (history.history[-2:] == 'pp' or history.history[-1:] == "c")) or history.history[-1:] == 'f':
            return True

    @staticmethod
    # def get_round_history(history):
    #     if len(history) <= 2:
    #         return history
    #
    #     if history[:2] == 'pp' or history[:2] == 'rc':
    #         len_frst_rnd
    #
    #
    #     if len(history) <= 2:
    #         return history
    #     if len(history) == 3:
    #



    @staticmethod
    def get_options(history):

        _raise = history[-1:] == 'r'

        check_raise = history[-2:] == 'pr'
        # call, fold, raise
        double_raise = history[-2:] == 'rr'
        # call, fold

        if _raise and not (double_raise or check_raise):
            return {0: 'f', 1: 'c', 2: 'r'}
        if double_raise or check_raise:
            return {0: 'f', 1: 'c'}
        else:
            return {0: 'p', 1: 'r'}

        single_check = history[-1:] = 'p'
        # check, raise
        double_check = history[-2:] == 'pp'
        # check, raise
        call = history[-1:] = 'c'
        # check, raise

    @staticmethod
    def get_reward(history, player_card, opponent_card, communnity_card):
     #
     # a  raise fold  << -1
     # b raise raise fold << -3
     # c  check raise fold << -1
     #
     #
     #  d raise call  << +2
     #  e raise raise call << +4
     #  f check raise call << +2
     #  g check check << 0
     #
     #
     #
     #
     #   raise call  << +4
     #   raise raise call << +8
     #   check raise call << +2
     #   check check << 0
     #
     #  if_2_rounds:
     #    check_first_round
     #    secnd_round
     #  else:

     if history[-1] == 'f':
         return 1
     return 1 if player_card > opponent_card else -1

        # terminal_pass = history[-1] == 'p'
        # double_bet = history[-2:] == "bb"
        #
        #
        #
        # if terminal_pass:
        #     if history[-2:] == 'pp':
        #         return 1 if player_card > opponent_card else -1
        #     else:
        #         return 1
        # elif double_bet:
        #     return 2 if player_card > opponent_card else -2




    def get_node(self, card, hist):
        history = hist.history
        key = str(card) + " " + history
        if key not in self.nodeMap:
            # get_options(history)
            action_dict = self.get_options(history)
            info_set = Node(key, action_dict, hist)
            self.nodeMap[key] = info_set
            return info_set
        return self.nodeMap[key]





class History:
    def __init__(self, prev_history=None):
        if prev_history == None:
            self.round = 1
            self.history = ''
            self.round_history = ''
            self.player_1 = True
        else:
            self.history = prev_history.history
            self.round = prev_history.round
            self.round_history = prev_history.round_history
            self.player_1 = prev_history.player_1


    def get_round (self):
        if self.round_history[-1:] == 'c' or self.round_history[-2:] == 'pp':
            self.round += 1
            self.round_history = ''
            self.player_1 = True

    def add_history(self, move):
        new_history = copy.deepcopy(self)
        new_history.history = self.history + move
        new_history.round_history = self.round_history + move
        new_history.player_1 = not self.player_1
        new_history.get_round()
        return History(new_history)



class Node:
    def __init__(self, key, action_dict, hist):
        self.key = key
        self.hist = hist
        self.n_actions = len(action_dict.keys())
        self.regret_sum = np.zeros(self.n_actions)
        self.strategy_sum = np.zeros(self.n_actions)
        self.action_dict = action_dict
        self.strategy = np.repeat(1/self.n_actions, self.n_actions)
        self.reach_pr = 0
        self.reach_pr_sum = 0



    def update_strategy(self):
        self.strategy_sum += self.reach_pr * self.strategy
        self.reach_pr_sum += self.reach_pr
        self.strategy = self.get_strategy()
        self.reach_pr = 0

    def get_strategy(self):
        regrets = self.regret_sum
        regrets[regrets < 0] = 0
        normalizing_sum = sum(regrets)
        if normalizing_sum > 0:
            return regrets / normalizing_sum
        else:
            return np.repeat(1/self.n_actions, self.n_actions)

    def get_average_strategy(self):
        strategy = self.strategy_sum / self.reach_pr_sum
        # Re-normalize
        total = sum(strategy)
        strategy /= total
        return strategy

    def __str__(self):
        strategies = ['{:03.2f}'.format(x)
                      for x in self.get_average_strategy()]
        return '{} {}'.format(self.key.ljust(6), strategies)


def display_results(ev, i_map):
    print('player 1 expected value: {}'.format(ev))
    print('player 2 expected value: {}'.format(-1 * ev))

    print()
    print('player 1 strategies:')
    sorted_items = sorted(i_map.items(), key=lambda x: x[0])
    for _, v in filter(lambda x: len(x[1].hist.round_history) % 2 == 0, sorted_items):
        print(v)
    print()
    print('player 2 strategies:')
    for _, v in filter(lambda x: len(x[1].hist.round_history) % 2 == 1, sorted_items):
        print(v)


if __name__ == "__main__":
    time1 = time.time()
    trainer = Kunh()
    trainer.train(n_iterations=8000)
    print(abs(time1 - time.time()))
    print(sys.getsizeof(trainer))
