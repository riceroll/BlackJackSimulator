# import os
# import random
#
# from matplotlib import pyplot as plt
# import numpy as np
#
# from Player import Player
#
#
# class Game:
#     def __init__(self, num_decks=6, player_chips=0, penetration_limit=0.0, is_bot=False, BJ_multiple=5/2):
#         # TABLE CONSTANT
#         self.PENETRATION_LIMIT = penetration_limit
#         self.NUM_DECKS = num_decks
#         self.BJ_multiple = BJ_multiple
#
#         # player
#         self.player = Player(self, player_chips, is_bot)
#
#         # info
#         self.n_rounds = 0
#         self.n_rounds_max = 100
#         self.player_chips_history = [self.player.chips]
#         self.expectation_history = []
#
#         self.reshuffle()
#
#     # ================ game ================
#     def play(self):
#
#
#
# if __name__ == "__main__":
#     t = Table()
#     t.bot()
