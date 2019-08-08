import sys
import random


class Table:
    def __init__(self, num_decks=6, player_chips=100, penetration_limit=0):
        # TABLE CONSTANT
        self.POKER = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'J': 10, 'Q': 10, 'K': 10}
        self.PENETRATION_LIMIT = penetration_limit
        self.NUM_DECKS = num_decks

        # table var
        self.shoe = []
        self.discards = []
        self.dealer_hand = []
        self.player_hands = [[]]
        self.betting_box = [0]

        # player
        self.BET_DEFAULT = 10
        self.player_chips = player_chips

        self.reshuffle()

    # ================ game ================
    def penetrated(self):
        if len(self.shoe) / (len(self.shoe) + len(self.discards)) <= self.PENETRATION_LIMIT:
            return True
        return False

    def reshuffle(self):
        self.shoe.clear()
        self.discards.clear()
        self.shoe = list(self.POKER.keys()) * 4 * self.NUM_DECKS
        random.shuffle(self.shoe)

    # ================ turn ================
    def bet(self, i_player_hand, bet):
        self.player_chips -= bet
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
        b = input("bet: ")
        if b:
            b = int(b)
        else:
            b = self.BET_DEFAULT
        self.bet(0, b)

    # ================ round ================
    def display(self, round_ended=False):
        sys.stdout.flush()
        print("dealer hand: ")
        if round_ended:
            print(self.dealer_hand)
        else:
            print(self.dealer_hand[:1])
        print("player hands: ", self.player_hands)
        print(self.player_hands)
        print("betting box:  ", self.betting_box)
        if round_ended:
            print("chips remaining: ", self.player_chips)

    def sum(self, hand):
        hand = [self.POKER[card] for card in hand]
        while 11 in hand:
            if sum(hand) > 21:
                hand[hand.index(11)] = 1
            else:
                break
        return sum(hand)

    def settle(self):
        # return winner 0: dealer; 1: draw; 2: player;
        multiples = []
        for player_hand in self.player_hands:
            if self.sum(player_hand) > 21:
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
        self.discards += self.dealer_hand
        self.dealer_hand.clear()

        for hand in self.player_hands:
            self.discards += hand
            hand.clear()
        self.player_hands = [[]]

        print('b:', self.betting_box)
        self.player_chips += sum(self.betting_box)
        self.betting_box = [0]

    # ================ play ================
    def play_round(self):
        self.init_bet()
        self.init_draw()

        for i_player_hand, player_hand in enumerate(self.player_hands):     # player's turn
            while True:     # player round
                if self.sum(player_hand) >= 21:
                    break
                self.display()
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

        return self.player_chips
