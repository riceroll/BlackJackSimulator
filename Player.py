import os

import numpy as np
from matplotlib import pyplot as plt


class Player:
    def __init__(self, table=None, chips=0, is_bot=False):
        self.POKER = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'J': 10, 'Q': 10, 'K': 10}
        self.ACTION = {0: 's', 1: 'h', 2: 'd', 3: 'p'}
        self.OMEGA2 = {'A': 0, '2': 1, '3': 1, '4': 2, '5': 2, '6': 2, '7': 1, '8': 0, '9': -1, '10': -2,
                       'J': -2, 'Q': -2, 'K': -2}
        self.N_ROW_HARD = 17
        self.N_ROW_SOFT = 7
        self.N_ROW_SPLIT = 10
        self.BET_DEFAULT = 1

        self.table = table
        self.strategy = None
        self.is_bot = is_bot
        self.init_chips = chips
        self.chips = chips
        self.count = 0
        self.count_normalized = 0

        self.count_history = [0]

        self.read_strategy()

    def reset(self):
        self.count_history = [0]
        self.count = 0
        self.count_normalized = 0
        self.chips = self.init_chips

    def reset_counter(self):
        self.count = 0
        self.count_normalized = 0

    def read_strategy(self, strategy='Basic'):
        cwd = os.path.split(os.path.realpath(__file__))[0]
        dir_strategy = os.path.join(cwd, 'strategies', strategy+'.csv')
        self.strategy = np.genfromtxt(dir_strategy, delimiter=',').astype(int)

    def sum(self, hand):
        hand = [self.POKER[card] for card in hand]
        while 11 in hand:
            if sum(hand) > 21:
                hand[hand.index(11)] = 1
            else:
                break
        return sum(hand)

    def count_card(self, card):
        self.count += self.OMEGA2[card]
        self.count_history.append(self.count)
        if len(self.table.shoe):
            self.count_normalized = self.count / len(self.table.shoe)
        else:
            self.count_normalized = 0

    def plot_count_history(self):
        n_counts = [i for i in range(len(self.count_history))]
        plt.plot(n_counts, self.count_history)
        plt.show()

    def get_bet(self):
        return 1
        if self.count > 5:
            return 4
        elif self.count > 3:
            return 2
        return 1

    def get_action(self, dealer_card, player_hand):
        if not self.is_bot:
            print('not bot')

        col = self.POKER[dealer_card] - 2
        row = -1
        is_hard = True

        if len(player_hand) == 1:
            return 'h'

        if len(player_hand) == 2:
            if player_hand[0] == player_hand[1]:    # split
                row = self.POKER[player_hand[0]] - 2 + self.N_ROW_HARD + self.N_ROW_SOFT
                is_hard = False
            elif 'A' in player_hand:
                if 13 <= self.sum(player_hand) <= 19:   # soft
                    row = self.sum(player_hand) - 11 - 2 + self.N_ROW_HARD
                    is_hard = False
        if is_hard:
            if 4 <= self.sum(player_hand) <= 20:
                row = self.sum(player_hand) - 4

        return self.ACTION[self.strategy[row, col]]











