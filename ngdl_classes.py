# This is the main ngdl file that takes user input
# and then calls the functions from the parse and
# write files to read the semi-natural language
# description and write the corresponding gdl
# description in a .kif. This file also contains
# the various classes for the intermediate
# representation of the game (Board, Player, Piece...).

import ngdl_parse
import ngdl_write

# Game contains players, the board,
# goals/objectives, end conditions,
# and point distribution
class Game:
    
    def __init__(self):
        self.players = []
        self.pieces = {}

# All boards are square and have both a size and a
# list of pieces with starting positions (if there
# are any pieces on the board at the beginning of
# the game)
class Board:

    def __init__(self, insize):
        self.size = insize
    starting_positions = {}

# Players have a list of legal moves and
# a set of pieces
class Player:

    def __init__(self, n):
        self.name = n
        self.pieces = []

    def __eq__(self, other):
        return self.name == other.name

# Pieces have names and move definitions
class Piece:
    
    def __init__(self, n):
        self.name = n

def translate(input_file, output_file):
    nl_file = open(input_file, 'r')
    gdl_file = open(output_file, 'w')
