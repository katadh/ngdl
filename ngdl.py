import re
import nltk
import ngdl_classes
import global_vars
import ngdl_parse
import ngdl_write

def start_dialog(output_file="test.txt"):
    if not global_vars.initialized:
        global_vars.init()
    else:
        reset_global_vars()

    output = open(output_file, "w")
    print "Welcome to the natural language game creation program for general game playing!"
    #print "First we'll work on defining the game environment"
    board_size_dialog()
    player_num_dialog()
    game_pieces_dialog()
    player_move_dialog()
    goal_dialog()
    terminal_dialog()
    ngdl_write.write_gdl_file(output)
    output.close()

def reset_global_vars():
    global_vars.write_queue = [["noop", []], ["goals", []], ["terminal", []], ["distinct_cells", []], ["successors", [50]]]
    global_vars.game = ngdl_classes.Game()
    
def board_size_dialog():
    in_board_size = raw_input("What size would you like your board to be?: ")
    valid_input = re.search("([0-9]+)\s?(by|x|X)\s?([0-9]+)", in_board_size)

    while not valid_input:
        print "Sorry, I can't understand that input yet, can you try again?"
        in_board_size = raw_input("What size would you like your game to be?: ")
        valid_input = re.search("([0-9]+)\s?(by|x|X)\s?([0-9]+)", in_board_size)

    board_size = (valid_input.group(1), valid_input.group(3))

    #confirmation = raw_input("To confirm, there will be " + board_size[0] + " columns and " + board_size[1] + " rows?: ")

    global_vars.game.board = ngdl_classes.Board((int(board_size[0]), int(board_size[1])))
    global_vars.write_queue.append(["board" , []])

def player_num_dialog():
    in_player_num = raw_input("How many players does your game have?: ")
    valid_input = re.search("[0-9]+", in_player_num)

    while not valid_input:
        print "Sorry, I can't understand that input yet, can you try again?"
        in_player_num = raw_input("How many players does your game have?: ")
        valid_input = re.search("[0-9]+", in_player_num)

    num_players = int(valid_input.group())

    for p in range(1,num_players+1):
        global_vars.game.players.append(ngdl_classes.Player("player" + str(p)))

    global_vars.write_queue.append(["players", []])

def game_pieces_dialog():

    for player in global_vars.game.players:
        in_piece_names = raw_input("What types of pieces does " + player.name + " have?: ")
        pieces = re.findall("([0-9]*)\s|^([^\W\d]+)", in_piece_names)

        for p in pieces:
            global_vars.game.pieces[p[1]] = ngdl_classes.Piece(p[1])

        on_board_response = raw_input("Do any of " + player.name + "'s pieces start on the board?: ")
        on_board_response = on_board_response.lower()
        if not re.match("[no|n]", on_board_response):
            for p in pieces:

                if p[0] == "" or int(p[0]) > 1:
                    p_positions = raw_input("What are the starting positions <col, row> of the " +
                                            p[1] + " that start on the board? (enter to skip): ")
                else:
                    p_positions = raw_input("What is the starting position <col, row> of the " +
                                            p[1] + " if it starts on the board? (enter to skip): ")

                positions = re.findall("([0-9]+),\s?([0-9]+)", p_positions)
                if positions:
                    for pos in positions:
                        global_vars.game.board.starting_positions[(int(pos[0]), int(pos[1]))] = player.name + " " + piece.name
                

def player_move_dialog():
    move_conditions = raw_input("What can a player do on their turn?: ")
    parse_trees = ngdl_parse.parse(move_conditions, 2)
        
    nltk_tree = parse_trees[0]
    tree = translate_tree(nltk_tree)

    conditions = process_condition(tree)
    
    action = tree.find_closest_node("ACTION")
    while action.children:
        index = [child.name for child in action.children].index("ACTION")
        action = action[index]

    if action.value == "drop":
        drop_response = raw_input("By 'drop', do you mean dropping a piece like in Connect-4, or placing a piece like in Shogi?: ")        
        drop_response.lower()
        if re.match("[connect\-4|drop]", drop_response):
            global_vars.write_queue.append(["drop_occupant_conditions", [[conditions]]])
            global_vars.write_queue.append(["perpetuate_untouched_cells", [["drop"]]])
        else:
            global_vars.write_queue.append(["place_occupant_conditions", [[conditions]]])
            global_vars.write_queue.append(["perpetuate_untouched_cells", [["place"]]])
    elif action.value in ["place", "mark"]:
        global_vars.write_queue.append(["place_occupant_conditions", [[conditions]]])
        global_vars.write_queue.append(["perpetuate_untouched_cells", [["place"]]])
            


#def piece_move_dialog():

def goal_dialog():
    win_conditions = raw_input("How does a player win?: ")
    parse_trees = ngdl_parse.parse(win_conditions, 1)

    nltk_tree = parse_trees[0]
    tree = translate_tree(nltk_tree)

    #result = tree.find_closest_node("RESULT")
    conditions_tree = tree.find_closest_node("COND")
    conditions = process_condition(conditions_tree)
    global_vars.write_queue.append(["win_conditions", [[conditions], ""]])

def terminal_dialog():
    game_end_conditions = raw_input("Aside from a player winning, how does the game end?: ")
    parse_trees = ngdl_parse.parse(game_end_conditions, 1)

    nltk_tree = parse_trees[0]
    tree = translate_tree(nltk_tree)

    conditions_tree = tree.find_closest_node("COND")
    conditions = process_condition(conditions_tree)
    global_vars.write_queue.append(["game_end_conditions", [[conditions]]])

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
    return conditions

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

            if cond_definition[-1]:
                global_vars.write_queue.append([cond_definition[2], slot_values])
            else:
                global_vars.write_queue.append([cond_definition[2], []])
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
        

cond_dictionary = {"empty": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(empty {0} {1} {2})", "board_part_empty", False],
                   "open": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(open {0} {1} {2})", "board_part_open", False],
                   "full": [[["NUM", "?col"], ["NUM", "?row"], ["BOARD_PART"]], "(full {0} {1} {2})", "board_part_full", False],
                   "in-a-row": [[["NUM"], ["PLAYER", "?player"], ["PIECE", "?piece"]], "({0}_in_a_row {1} {2})", "x_in_a_row", True]
                   }
