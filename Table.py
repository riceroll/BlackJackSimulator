import os
import random

from matplotlib import pyplot as plt
import numpy as np

from Player import Player


class Table:
    def __init__(self, num_decks=6, player_chips=0, penetration_limit=0.0, is_bot=False, BJ_multiple=5/2, strategy="Basic"):
        # TABLE CONSTANT
        self.POKER = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'J': 10, 'Q': 10, 'K': 10}
        self.PENETRATION_LIMIT = penetration_limit
        self.NUM_DECKS = num_decks
        self.BJ_multiple = BJ_multiple

        # player
        self.player = Player(self, player_chips, is_bot, strategy=strategy)

        # table var
        self.shoe = []
        self.discards = []
        self.dealer_hand = []
        self.player_hands = [[]]
        self.betting_box = [0]

        # info
        self.n_rounds = 0
        self.player_chips_history = [self.player.chips]
        self.earning_rate_history = []
        self.earning_rate = None
        self.residual = None

        self.reshuffle()

    # ================ game ================
    def init(self):
        self.reshuffle()
        self.player.reset()
        self.player_chips_history = [self.player.chips]
        self.earning_rate_history = []
        self.earning_rate = None
        self.residual = None
        self.n_rounds = 0

    def bot(self):
        self.player.is_bot = True

    def human(self):
        self.player.is_bot = False

    def penetrated(self):
        if len(self.shoe) / (len(self.shoe) + len(self.discards)) <= self.PENETRATION_LIMIT:
            return True
        return False

    def reshuffle(self):
        self.player.reset_counter()
        self.shoe.clear()
        self.discards.clear()
        self.shoe = list(self.POKER.keys()) * 4 * self.NUM_DECKS
        random.shuffle(self.shoe)

    # ================ turn ================
    def bet(self, i_player_hand, bet):
        self.player.chips -= bet
        self.betting_box[i_player_hand] += bet

    def player_draw(self, i_player_hand):
        if self.penetrated():
            self.reshuffle()
        hand = self.player_hands[i_player_hand]
        hand.append(self.shoe.pop())

    def dealer_draw(self):
        if self.penetrated():
            self.reshuffle()
        self.dealer_hand.append(self.shoe.pop())

    def double(self, i_hand):
        self.bet(i_hand, self.betting_box[i_hand])

    def split(self, i_hand):
        # allow split infinite times
        hand = self.player_hands[i_hand]
        if len(hand) != 2 or hand[0] != hand[1]:
            print(hand)
            print("Cannot split.")
            return False
        hand_new = [hand.pop()]
        self.player_hands.append(hand_new)
        self.betting_box.append(0)
        self.bet(-1, self.betting_box[i_hand])
        return True

    def init_draw(self):
        self.dealer_draw()
        self.dealer_draw()
        self.player_draw(0)
        self.player_draw(0)

    def init_bet(self):
        if self.player.is_bot:
            self.bet(0, self.player.get_bet())
        else:
            os.system('clear')
            bet = input("Bet: ")
            if bet:
                bet = int(bet)
            else:
                bet = self.player.BET_DEFAULT
            self.bet(0, bet)

    # ================ round ================
    def sum(self, hand):
        hand = [self.POKER[card] for card in hand]
        while 11 in hand:
            if sum(hand) > 21:
                hand[hand.index(11)] = 1
            else:
                break
        return sum(hand)

    def settle(self):
        multiples = []
        for player_hand in self.player_hands:
            if self.sum(player_hand) == 21 and len(player_hand) == 2:
                multiples.append(self.BJ_multiple)
            elif self.sum(player_hand) > 21:
                multiples.append(0)
            elif self.sum(self.dealer_hand) > 21:
                multiples.append(2)
            elif self.sum(self.dealer_hand) < self.sum(player_hand):
                multiples.append(2)
            elif self.sum(self.dealer_hand) > self.sum(player_hand):
                multiples.append(0)
            elif self.sum(self.dealer_hand) == self.sum(player_hand):
                multiples.append(1)
        self.betting_box = [multiples[i] * bet for i, bet in enumerate(self.betting_box)]

    def collect(self):
        # discard all cards when the round ends
        for card in self.dealer_hand:
            self.discards.append(card)
            self.player.count_card(card)
        self.dealer_hand.clear()

        for hand in self.player_hands:
            for card in hand:
                self.player.count_card(card)
                self.discards.append(card)
            hand.clear()
        self.player_hands = [[]]

        self.player.chips += sum(self.betting_box)
        self.player_chips_history.append(self.player.chips)
        self.n_rounds += 1
        self.betting_box = [0]
        if not self.player.is_bot:
            print("chips:   ", self.player.chips)
            print("============================")

    # ================ statistics ================
    def display(self, round_ended=False):
        if self.player.is_bot:
            pass
        else:
            os.system('clear')
            if round_ended:
                print("dealer: ", self.dealer_hand)
            else:
                print("dealer: ", self.dealer_hand[:1])
            print("player: ", self.player_hands)
            print("bet:    ", self.betting_box)
            input()

    def fit_chips_history(self):
        x = [i for i in range(len(self.player_chips_history))]
        self.earning_rate, self.residual, _, _ = np.linalg.lstsq(np.array(x)[:, np.newaxis], self.player_chips_history, rcond=None)

    def plot_chips_history(self):
        x = [i for i in range(len(self.player_chips_history))]
        y = self.earning_rate * x
        plt.plot(x, self.player_chips_history)
        plt.plot(x, y)
        plt.show()

    def plot_earning_rate_history(self):
        n_rounds = [i for i in range(len(self.earning_rate_history[100:]))]
        plt.plot(n_rounds, self.earning_rate_history[100:])
        plt.show()

    # ================ play ================
    def play_round(self):
        self.init_bet()
        self.init_draw()

        for i_player_hand, player_hand in enumerate(self.player_hands):     # player's turn
            while True:     # player round
                if self.sum(player_hand) >= 21:
                    break
                self.display()

                if self.player.is_bot:
                    action = self.player.get_action(self.dealer_hand[0], player_hand)
                    # print(action)
                else:
                    action = input()
                if action == 'h':   # hit
                    self.player_draw(i_player_hand)
                    continue
                if action == 's':   # stand
                    break
                if action == 'd':   # double
                    self.double(i_player_hand)
                    self.player_draw(i_player_hand)
                    break
                if action == 'p':   # split
                    self.split(i_player_hand)
                    continue

        while self.sum(self.dealer_hand) < 17:      # dealer's turn
            if self.sum(self.dealer_hand) >= 17:
                break
            self.dealer_draw()

        self.settle()
        self.display(True)
        self.collect()

    def play_game(self, n_rounds_max=1E5, residual_threshold=2E-6,  n_rounds_min=1E3):
        self.init()
        while True:
            if self.n_rounds == n_rounds_max:
                self.fit_chips_history()
                break
            if self.player.is_bot:
                self.play_round()
            else:
                command = input()
                if not command == "e" or command == "exit" or command == "q" or command == "quit":
                    self.play_round()
                else:
                    break
            if self.n_rounds % n_rounds_min == 0:
                os.system('clear')
                print(self.n_rounds / n_rounds_max)
                # self.fit_chips_history()
                # if self.residual:
                    # print(residual_threshold / (self.residual / self.n_rounds))
                # if self.residual / self.n_rounds < residual_threshold:
                #     break

        print('earning_rate: ', self.earning_rate)


if __name__ == "__main__":
    t = Table()
    t.bot()
