# This file contains the various classes for the intermediate
# representation of the game (Board, Player, Piece...).

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

    # Goes backward through the sentence until it finds a node with
    # the given name or value
    def find_previous_node(self, node_name=None, node_value=None):
        root = self.find_ancestor()
        nodes = root.nodes_in_subtrees()
        start = nodes.index(self)

        for i in range(start-1, -1, -1):
            if node_name != None:
                if node_value != None:
                    if nodes[i].name == node_name and nodes[i].value == node_value:
                        return nodes[i]
                else:
                    if nodes[i].name == node_name:
                        return nodes[i]
            elif node_value != None:
                    if nodes[i].value == node_value:
                        return nodes[i]
            else:
                    return None
            

    # finds the closest distinct node with the desired name and value
    def find_closest_node(self, node_name=None, node_value=None):
        if self.parent:
            nodes = [self.parent]
        else:
            nodes = []
        nodes = nodes + self.children
        visited = [self]

        while nodes:
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

            if node.parent and node.parent not in visited:
                nodes.append(node.parent)
            nodes = nodes + [child for child in node.children if child not in visited]

        return None

    def nodes_in_subtrees(self):
        nodes = [self]
        if self.children:
            for child in self.children:
                nodes = nodes + child.nodes_in_subtrees()
        return nodes

    def find_ancestor(self, node_name=None, node_value=None):
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

        if self.parent == None:
            return self
        else:
            return self.parent.find_ancestor(node_name, node_value)

    def ancestors(self):
        ancestors = self.get_ancestors()
        ancestors.remove(self)
        return ancestors

    def get_ancestors(self):
        if self.parent == None:
            return [self]
        else:
            return [self] + self.parent.get_ancestors()

    def leaves(self):
        leaves = []
        if self.children:
            for child in self.children:
                leaves = leaves + child.leaves()
            return leaves
        else:
            return [self]
            
