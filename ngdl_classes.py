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

class Tree:

    def __init__(self, n):
        self.name = n
        self.value = ""
        self.children = []
        self.parent = None

    def __str__(self, n=0):
        n = n + 1
        string = "(" + self.name + " " + self.value
        if self.children:
            string = string + "\n"
            for child in self.children:
                string = string + "\t"*n + child.__str__(n) + "\n"
            return string[:-1] + ")"
        else:
            return string + ")"

    def __getitem__(self, index):
        return self.children[index]

    def __setitem__(self, index, value):
        self.children[index] = value

    # finds the closest distinct node with the desired name and value
    def find_closest_node(self, node_name=None, node_value=None):
        nodes = [self.parent]
        nodes = nodes + self.children
        visited = [self]

        while len(nodes) > 0:
            node = nodes.pop()
            visited.append(node)

            if node_name != None:
                if node_value != None:
                    if node.name == node_name and node.value == node_value:
                        return node
                else:
                    if node.name == node_name:
                        return node
            elif node_value != None:
                    if node.value == node_value:
                        return node
            else:
                    return None

            if node.parent not in visited:
                nodes.append(node.parent)
            nodes = nodes + [child for child in node.children if child not in visited]

        return None

    def nodes_in_subtrees(self):
        nodes = [self]
        if self.children:
            for child in self.children:
                nodes = nodes + child.nodes_in_subtrees()
        return nodes


    def root(self):
        if self.parent == None:
            return self
        else:
            return self.parent.root()

    def leaves(self):
        leaves = []
        if self.children:
            for child in self.children:
                leaves = leaves + child.leaves()
            return leaves
        else:
            return [self]
            
