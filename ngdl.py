import ngdl_classes
import ngdl_parse
import re
import nltk

def start_dialog():
    game = ngdl_classes.Game()
    print "Welcome to the natural language game creation program for general game playing!"
    print "First we'll work on defining the game environment"
    board_size_dialog(game)
    player_num_dialog(game)
    game_pieces_dialog(game)
    
def board_size_dialog(game):
    print "For now I can only make games that are a grid of squares"
    
    in_board_size = raw_input("What size would you like your game to be?: ")
    valid_input = re.search("([0-9]+)\s?(by|x|X)\s?([0-9]+)", in_board_size)

    while not valid_input:
        print "Sorry, I can't understand that input yet, can you try again?"
        in_board_size = raw_input("What size would you like your game to be?: ")
        valid_input = re.search("([0-9]+)\s?(by|x|X)\s?([0-9]+)", in_board_size)

    board_size = (valid_input.group(1), valid_input.group(3))

    #confirmation = raw_input("To confirm, there will be " + board_size[0] + " columns and " + board_size[1] + " rows?: ")

    game.board = ngdl_classes.Board((int(board_size[0]), int(board_size[1])))

def player_num_dialog(game):
    in_player_num = raw_input("How many players does your game have?: ")
    valid_input = re.search("[0-9]+", in_player_num)

    while not valid_input:
        print "Sorry, I can't understand that input yet, can you try again?"
        in_player_num = raw_input("How many players does your game have?: ")
        valid_input = re.search("[0-9]+", in_player_num)

    num_players = int(valid_input.group())

    for p in range(1,p+1):
        game.players.append(Player(str(i)))

def game_pieces_dialog(game):

    for player in game.players:
        in_piece_names = raw_input("What pieces does " + player.name + " have?: ")
        pieces = re.findall("([0-9]*)\s|^([^\W\d]+)", in_piece_list)

        for p in pieces:
            game.pieces[p[1]] = Piece(p[1])
                
            if p[0] == "" or int(p[0]) > 1:
                p_positions = raw_input("What are the starting positions <col, row> of the " +
                                        p[1] + " that start on the board? (enter to skip): ")
            else:
                p_positions = raw_input("What is the starting position <col, row> of the " +
                                        p[1] + " if it starts on the board? (enter to skip): ")

            positions = re.findall("([0-9]+),\s?([0-9]+)", p_positions)
            if positions:
                for pos in positions:
                    game.board.starting_positions[(int(pos[0]), int(pos[1]))] = player.name + " " + piece.name

#def player_move_dialog(game):

#def piece_move_dialog(game):

def goal_dialog(game):
    win_conditions = raw_input("How does a player win?: ")
    parse_trees = ngdl_parse.parse(win_conditions, 1)

    for nltk_tree in parse_trees:
        tree = translate_tree(nltk_tree)
        result = tree.find_closest_node("RESULT")
        conditions = tree.find_closest_node("COND")

def check_goal_result():
    
        

#def terminal_dialog(game):

def translate_tree(nltk_tree):
    if nltk_tree.height() == 2:
        tree = ngdl_classes.Tree(nltk_tree.node)
        tree.value = nltk_tree[0]
        return tree
        
    tree = ngdl_classes.Tree(nltk_tree.node)
    for subtree in nltk_tree:
        tree.children.append(translate_tree(subtree))
    for subtree in tree.children:
        subtree.parent = tree

    return tree
        

cond_dictionary = {"empty cell": ["(true (cell ?col ?row ?player none))", None],
                   "uncontrolled cell": ["(true (cell ?col ?row none ?occupant))", None],
                   "board open": ["board_open", "board_open"],
                   "less": ["(less {0} {1})", "less"],
                   "x-in-a-row": ["({0}_in_a_row {1} {2})", "x_in_a_row"]
                   }
