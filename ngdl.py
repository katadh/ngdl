import ngdl_classes
import ngdl_parse
import re
import nltk

game = ngdl_classes.Game()

def start_dialog():
    print "Welcome to the natural language game creation program for general game playing!"
    print "First we'll work on defining the game environment"
    board_size_dialog()
    player_num_dialog()
    game_pieces_dialog()
    
def board_size_dialog():
    global game
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

def player_num_dialog():
    global game
    in_player_num = raw_input("How many players does your game have?: ")
    valid_input = re.search("[0-9]+", in_player_num)

    while not valid_input:
        print "Sorry, I can't understand that input yet, can you try again?"
        in_player_num = raw_input("How many players does your game have?: ")
        valid_input = re.search("[0-9]+", in_player_num)

    num_players = int(valid_input.group())

    for p in range(1,p+1):
        game.players.append(Player(str(i)))

def game_pieces_dialog():
    global game

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

def goal_dialog():
    global game
    win_conditions = raw_input("How does a player win?: ")
    parse_trees = ngdl_parse.parse(win_conditions, 1)

    for nltk_tree in parse_trees:
        tree = translate_tree(nltk_tree)
        result = tree.find_closest_node("RESULT")
        conditions = tree.find_closest_node("COND")

def process_result(result):
    return

def process_conditions(conds):
    conditions = []
    if "OR" in [child.name for child in conds.children]:
        conditions.append("OR")
        for child in conds.children:
            if child.name == "COND":
                conditions.append(process_condition(child))
    elif "AND" in [child.name for child in conds.children]:
        conditions.append("AND")
        for child in conds.children:
            if child.name == "COND":
                conditions.append(process_condition(child))
    else:
        conditions.append("COND")
        conditions.append(process_condition(conds))

def process_condition(cond_node):
    for leaf in cond_node.leaves():
        if leaf.value in cond_dictionary:
            cond_definition = cond_dictionary[leaf.value]
            slot_values = []
            for slot in cond_definition[0]:
                slot_node = leaf.find_closest_node(slot[0])
                if not slot_node:
                    if len(slot) == 2:
                        slot_values.append(slot[1])
                    else:
                        print "Slot fill error1!"
                elif cond_node not in slot_node.ancestors():
                    if len(slot) == 2:
                        slot_values.append(slot[1])
                    else:
                        print "Slot fill error2!"
                elif slot_node.name == "PLAYER":
                    slot_values.append(process_player(slot_node))
                elif slot_node.name == "BOARD_PART":
                    slot_values.append(process_board_part(slot_node))
                elif slot_node.name == "PIECE":
                    slot_values.append(process_piece(slot_node))
                else:
                    slot_values.append(slot_node.value)
            return cond_definition[1].format(*slot_values)
                    

def process_player(player_node):
    return "?player"

def process_board_part(board_part_node):
    square_equivalents = ["cell"]
    board_part = board_part_node
    while board_part.children:
        index = [child.name for child in board_part.children].index("BOARD_PART")
        board_part = board_part[index]
    if board_part.value in square_equivalents:
        return "square"
    else:
        return board_part.value

def process_piece(piece_node):
    piece = piece_node
    while piece.children:
        index = [child.name for child in piece.children].index("PIECE")
        piece = piece[index]

    if piece.value == "piece":
        return "?piece"
    else:
        return piece.value

#def terminal_dialog(game):

def translate_tree(nltk_tree):
    if nltk_tree.height() == 2:
        tree = ngdl_classes.Tree(nltk_tree.node)
        tree.value = nltk_tree[0]
        return tree
        
    tree = ngdl_classes.Tree(nltk_tree.node)
    for subtree in nltk_tree:
        if type(subtree) == str:
            tree.value = subtree
        else:
            tree.children.append(translate_tree(subtree))

    for subtree in tree.children:
        subtree.parent = tree

    return tree
        

cond_dictionary = {"empty": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(empty {0} {1} {2})", "board_part_empty"],
                   "open": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(open {0} {1} {2})", "board_part_open"],
                   "full": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(not (open {0} {1} {2}))", "board_part_open"],
                   "in-a-row": [[["NUM"], ["PLAYER"], ["PIECE"]], "({0}_in_a_row {1} {2})", "x_in_a_row"]
                   }
