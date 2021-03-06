# This file contains the functions for taking
# the intermediate representation of the game
# and writing the corresponding gdl into a .kif.

import re
import sys
import ngdl_classes
import global_vars

# This these are the other functions that must be called
# for each function to work correctly.

func_prereqs = {"board":[],
                "players":[],
                "perpetuate_untouched_cells":[],
                "place_occupant":["place_occupant_conditions"],
                "drop_occupant":["drop_occupant_conditions", "lowest_open_cell"],
                "noop":[],
                "place_occupant_conditions":["place_occupant"],
                "drop_occupant_conditions":["drop_occupant", "lowest_open_cell"],
                "goals":["win_conditions", "game_end_conditions"],
                "terminal":["game_end_conditions"],
                "win_conditions":[],
                "game_end_conditions":[],
                "less":["successors"],
                "successors":[],
                "lowest_open_cell":["successors"],
                "distinct_cells":[],
                "adjacent_cells":["adjacent_cols", "adjacent_rows"],
                "adjacent_cols":[],
                "adjacent_rows":[],
                "board_part_open":[],
                "board_part_full":["board_part_open"],
                "board_part_empty":[],
                "x_in_a_row":[]}

# We want to keep track of which definition functions we've
# already called so we aren't writing the same code into the
# gdl file multiple times

func_call_tracker = {"board":False,
                     "players":False,
                     "perpetuate_untouched_cells":False,
                     "place_occupant":False,
                     "drop_occupant":False,
                     "noop":False,
                     "place_occupant_conditions":False,
                     "drop_occupant_conditions":False,
                     "goals":False,
                     "terminal":False,
                     "win_conditions":False,
                     "game_end_conditions":False,
                     "less":False,
                     "lowest_open_cell":False,
                     "distinct_cells":False,
                     "adjacent_cells":False,
                     "adjacent_cols":False,
                     "adjacent_rows":False,
                     "successors":False,
                     "board_part_open":False,
                     "board_part_full":False,
                     "board_part_empty":False,
                     "make_true":False,
                     "x_in_a_row":False}


def write_gdl_file(gdl_file):
    print "Now writing file..."
    ngdl_write_object = sys.modules[__name__]

    for func in func_call_tracker:
        func_call_tracker[func] = False

    while global_vars.write_queue:
        [func_name, args] = global_vars.write_queue.pop(0)

        for prereq in func_prereqs[func_name]:
            if prereq not in [func[0] for func in global_vars.write_queue] and not func_call_tracker[prereq]:
                global_vars.write_queue.append([prereq, []])                

        if not func_call_tracker[func_name]:
            func = getattr(ngdl_write_object, func_name)
            func(gdl_file, *args)
            func_call_tracker[func_name] = True
        

def insert_conditions(conditions):

    code = ""
    for cond in conditions:
        code = code + "\t" + cond + "\n "

    code = code[:-2]
    return code

# Takes a board object and output file and
# writes gdl code to initialize the board
# in the file
def board(gdl_file):
    board = global_vars.game.board
    for col in range(1, board.size[0] + 1):
        for row in range(1, board.size[1] + 1):
            if (col, row) in board.starting_positions:
                gdl_file.write("(init (cell " +
                               str(col) + " " + str(row) + " " +
                               board.starting_positions[(col, row)] +
                               "))\n")
            else:
                gdl_file.write("(init (cell " +
                               str(col) + " " + str(row) + " " +
                               "none none))\n")
    gdl_file.write("\n")
    
    for col in range(1, board.size[0]):
        gdl_file.write("(next_column " + str(col) + " " + str(col+1) + ")\n")
    gdl_file.write("\n")

    for col in range(1, board.size[0] + 1):
        gdl_file.write("(is_column " + str(col) + ")\n")
    gdl_file.write("\n")

    for row in range(1, board.size[1]):
        gdl_file.write("(next_row " + str(row) + " " + str(row+1) + ")\n")
    gdl_file.write("\n")

    for row in range(1, board.size[1] + 1):
        gdl_file.write("(is_row " + str(row) + ")\n")
    gdl_file.write("\n")

    gdl_file.write("""(<= (base (cell ?col ?row ?player ?occupant))
    (is_column ?col)
    (is_row ?row)
    (role ?player)
    (owns ?player ?occupant))\n\n""")

    gdl_file.write("""(<= (base (cell ?col ?row none none))
    (is_column ?col)
    (is_row ?row))\n\n""")

    gdl_file.write("""(board_part row)
(board_part column)
(board_part square)
(board_part board)\n\n""")

# Initialize players
def players(gdl_file):
    player_list = global_vars.game.players
    for player in player_list:
        gdl_file.write("(role " + player.name + ")\n")
    gdl_file.write("\n")

    for player in player_list:
        gdl_file.write("(base (control " + player.name + "))\n")
    gdl_file.write("\n")

    gdl_file.write("(init (control " + player_list[0].name + "))\n\n")

    # The embedded loops are for if there is more than 2 players
    # Currently does not handle teams
    for player1 in player_list:
        for player2 in player_list:
            if player1 != player2:
                gdl_file.write("(opponent " + player1.name + " " +
                               player2.name + ")\n")
    gdl_file.write("\n")

    # Switch control of players
    for player_num in range(len(player_list)):
        next_player_num = player_num + 1
        if next_player_num == len(player_list):
            next_player_num = 0
        gdl_file.write("(<= (next (control " + player_list[player_num].name + "))\n" +
                       "\t(true (control " + player_list[next_player_num].name + ")))\n")
    gdl_file.write("\n")

    for player in player_list:
        for piece in player.pieces:
            gdl_file.write("(owns " + player.name + " " + piece + ")\n")
    gdl_file.write("\n")
        

# This a function that says that cells not involved in
# a legal move do not change from one state to the next
def perpetuate_untouched_cells(gdl_file, available_actions):
    for action in available_actions:
        if action == "move":
            gdl_file.write("""(<= (next (cell ?col ?row ?cell_player ?occupant))
            (true (cell ?col ?row ?cell_player ?occupant))
            (does ?move_player (move ?occupant ?src_col ?src_row ?dest_col ?dest_row))
            (distinct_cells ?col ?row ?src_col ?src_row)
            (distinct_cells ?col ?row ?dest_col ?dest_row))\n\n""")    
            global_vars.write_queue.append(["distinct_cells", []])
        if action == "place":
            gdl_file.write("""(<= (next (cell ?col ?row ?cell_player ?occupant))
            (true (cell ?col ?row ?cell_player ?occupant))
            (does ?move_player (place ?occupant ?dest_col ?dest_row))
            (distinct_cells ?col ?row ?dest_col ?dest_row))\n\n""")    
            global_vars.write_queue.append(["distinct_cells", []])
        if action == "drop":
            gdl_file.write("""(<= (next (cell ?col ?row ?cell_player ?occupant))
            (true (cell ?col ?row ?cell_player ?occupant))
            (does ?move_player (drop ?occupant ?dest_col))
            (or
                (distinct ?col ?dest_col)
                (not (lowest_open_cell ?col ?row))))\n\n""")    
            

def place_occupant(gdl_file):
    gdl_file.write("""(<= (next (cell ?col ?row ?player ?occupant))
    (does ?player (place ?occupant ?col ?row)))""")

def drop_occupant(gdl_file):
    gdl_file.write("""(<= (next (cell ?col ?row ?player ?occupant))
    (does ?player (drop ?occupant ?col))
    (lowest_open_cell ?col ?row))\n\n""")
        

##############################################################
# Piece move (next state) definitions for pre-defined pieces #
##############################################################


##################################
# Potentially legal player moves #
##################################

def noop(gdl_file):
    gdl_file.write("""(<= (legal ?player noop)
    (role ?player)
    (not (true (control ?player))))\n\n""")
    gdl_file.write("""(<= (input ?player noop)
    (role ?player))\n\n""")

def place_occupant_conditions(gdl_file, conditions):
    gdl_file.write("(<= (legal ?player (place ?occupant ?col ?row))\n " +
                   "\t(owns ?player ?occupant)\n" + 
                   "\t(true (control ?player))\n" + 
                   insert_conditions(conditions) + ")\n\n")
    gdl_file.write("""(<= (input ?player (place ?occupant ?col ?row))
    (role ?player)
    (is_column ?col)
    (is_row ?row)
    (owns ?player ?occupant))\n\n""")

def drop_occupant_conditions(gdl_file, conditions):
    gdl_file.write("(<= (legal ?player (drop ?occupant ?col))\n" +
                   "\t(owns ?player ?occupant)\n" +
                   "\t(true (control ?player))\n" +
                   insert_conditions(conditions) + ")\n\n")
    gdl_file.write("""(<= (input ?player (drop ?occupant ?col))
    (role ?player)
    (is_column ?col)
    (owns ?player ?occupant))""")

############################
# Goal and Terminal States #
############################

def goals(gdl_file):
    gdl_file.write("""(<= (goal ?player 100)
    (win ?player))\n\n""")
    gdl_file.write("""(<= (goal ?player 50)
    (not (win ?player))
    (opponent ?player ?opponent)
    (not (win ?opponent))
    game_end)\n\n""")
    gdl_file.write("""(<= (goal ?player 0)
    (opponent ?player ?opponent)
    (win ?opponent))\n\n""")

def terminal(gdl_file):
    gdl_file.write("""(<= terminal
    game_end)\n\n""")

def win_conditions(gdl_file, conditions, player=""):
    if player == "":
        gdl_file.write("(<= (win ?player)\n" +
                       insert_conditions(conditions) + ")\n\n")
    else:
        gdl_file.write("(<= (win " + player + ")\n" +
                       insert_conditions(conditions) +  ")\n\n")

def game_end_conditions(gdl_file, conditions):
    gdl_file.write("""(<= game_end
    (win ?player))\n\n""")
    if conditions:
        gdl_file.write("(<= game_end\n" + insert_conditions(conditions) + ")\n\n")

########################################################
# This section contains a bunch of different constants #
# or predefined functions that might be necessary      #
########################################################


def less(gdl_file):
    gdl_file.write("""(<= (less ?x ?y)
    (succ ?x ?y))\n\n""")
    gdl_file.write("""(<= (less ?x ?z)
    (succ ?x ?y)
    (less ?y ?z))\n\n""")

def successors(gdl_file, ceiling):
    for i in range(ceiling+1):
        gdl_file.write("(succ " + str(i) + " " + str(i+1) + ")\n")
    gdl_file.write("\n")

# Assumes column is filled from bottom with no gaps
def lowest_open_cell(gdl_file):
    gdl_file.write("""(<= (lowest_open_cell ?col ?row2)
    (true (cell ?col ?row2 ?any none))
    (succ ?row1 ?row2)
    (not (true (cell ?col ?row1 ?any none))))\n\n""")

def distinct_cells(gdl_file):
    gdl_file.write("""(<= (distinct_cells ?col1 ?row1 ?col2 ?row2)
    (true (cell ?col1 ?row1 ?any ?any2))
    (true (cell ?col2 ?row2 ?any ?any2))
    (or (distinct ?col1 ?col2)
        (distinct ?row1 ?row2)))\n\n""")

# Cardinal Directions
#def north(gdl_file):
#    gdl_file.write("(<= (north_neighbor ?col1 ?row1 ?col2 ?row2)\n" +
#                   "\t(true (cell ?col1 ?row1 ?player1 ?occupant1))\n" +
#                   "\t(true (cell ?col2 ?row2 ?player2 ?occupant2))\n" +
#                   "\t(not (distinct ?col1 ?col2))\n" +
#                   "\t(succ ?row2 ?row1))\n")
#
#def north_east(gdl_file):
#    gdl_file.write("(<= (north_east_of ?col1 ?row1 ?col2 ?row2)\n" +
#                   "\t())")

# Are two cells (x1, y1) and (x2, y2) adjacent?
# This will return true for both orthognal adjacency
# and diagonal adjacency.
def adjacent_cells(gdl_file):
    gdl_file.write("""(<= (adjacent_cells ?col1 ?row1 ?col2 ?row2)
    (adjacent_cols ?col1 ?col2)
    (not (distinct ?row1 ?row2)) 
    (is_row ?row1)
    (is_row ?row2))\n\n""")
    gdl_file.write("""(<= (adjacent_cells ?col1 ?row1 ?col2 ?row2)
    (adjacent_rows ?row1 ?row2)
    (not (distinct ?col1 ?col2))
    (is_column ?col1)
    (is_column ?col2))\n\n""")
    gdl_file.write("""(<= (adjacent_cells ?col1 ?row1 ?col2 ?row2)
    (adjacent_cols ?col1 ?col2)
    (adjacent_rows ?row1 ?row2))\n\n""")
                   

def adjacent_cols(gdl_file):
    gdl_file.write("""(<= (adjacent_cols ?col1 ?col2)
    (or (next_column ?col1 ?col2) (next_column ?col2 ?col1)))\n\n""")

def adjacent_rows(gdl_file):
    gdl_file.write("""(<= (adjacent_rows ?row1 ?row2)
    (or (next_row ?row1 ?row2) (next_row ?row2 ?row1)))\n\n""")

def board_part_open(gdl_file):
    gdl_file.write("""(<= (open column ?col ?row)
    (is_row ?row)
    (true (cell ?col ?any ?player none)))\n\n""")
    gdl_file.write("""(<= (open row ?col ?row)
    (is_column ?col)
    (true (cell ?any ?row ?player none)))\n\n""")
    gdl_file.write("""(<= (open square ?col ?row)
    (true (cell ?col ?row ?player none)))\n\n""")
    gdl_file.write("""(<= (open board ?col ?row)
    (is_column ?col)
    (is_row ?row)
    (true (cell ?any ?any2 ?player none)))\n\n""")

def board_part_full(gdl_file):
    gdl_file.write("""(<= (full ?part ?col ?row)
    (is_column ?col)
    (is_row ?row)
    (board_part ?part)
    (not (open ?part ?col ?row)))\n\n""")

def board_part_empty(gdl_file):
    board = global_vars.game.board
    gdl_file.write("""(<= (empty ?col ?row column)
    (make_true ?row)""")
    for row in range(1, board.size[1] + 1):
        gdl_file.write("\n\t(true (cell ?col " + row + " ?player none))")
    gdl_file.write(")\n\n")

    gdl_file.write("""(<= (empty ?col ?row row)
    (make_true ?col)""")
    for col in range(1, board.size[1] + 1):
        gdl_file.write("\n\t(true (cell " + col + " ?row ?player none))")
    gdl_file.write(")\n\n")

    gdl_file.write("""(<= (empty ?col ?row square)
    (true (cell ?col ?row ?player none)))""")

    gdl_file.write("""(<= (empty ?col ?row board)
    (make_true ?col)
    (make_true ?row)""")
    for col in range(1, board.size[1] + 1):
        gdl_file.write("\n\t(empty " + col + " column)")
    gdl_file.write(")\n\n")

# This function is for creating code that tests if x
# number of cells in a row meet a certain condition.
# For now these conditions are either that the cells are
# controlled by the same player or contain the same occupant
# or both. Inputting some value means that value has to be true for
# every cell i.e. "none" for uncontrolled or unoccupied cells
def x_in_a_row(gdl_file, x, player="?player", occupant="?piece"):
    if type(x) == str:
        x = int(x)

    if player == "?player":
        if occupant == "?piece":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?piece)\n")
            gdl_file.write("\t(owns ?player ?piece)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row ?player ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?piece)\n")
            gdl_file.write("\t(owns ?player ?piece)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " ?player ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?piece)\n")
            gdl_file.write("\t(owns ?player ?piece)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?piece)\n")
            gdl_file.write("\t(owns ?player ?piece)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")
            
        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row ?player ?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " ?player ?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player ?occupant))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player ?occupant))")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row ?player " + occupant + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " ?player " + occupant +"))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player " + occupant + "))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player " + occupant + "))")
            gdl_file.write(")\n\n")

    # This would mean that all sets of x squares in-a-row would satisfy the conditions
    elif player == "":
        if occupant == "?piece":
            print "Error: Not valid input"

        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row ?player" + str(i) + "?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " ?player" + str(i) + "?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player" + str(i) + "?occupant))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player" + str(i) + "?occupant))")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row ?player" + str(i) + " " + occupant + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " ?player" + str(i) + " " + occupant +"))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player" + str(i) + " " + occupant + "))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player" + str(i) + " " + occupant + "))")
            gdl_file.write(")\n\n")

    else:
        if occupant == "?piece":
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + "?row " +
                               player + " ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               player + " ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               player + " ?occupant" + str(i) + "))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                                player + " ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")

        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row " + player + " ?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                                " " + player + " ?occupant))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                                " " + player + " ?occupant))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?x" + str(i) + " ?row" + str((x+1)-i) +
                                " " + player + " ?occupant))")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) +
                               " ?row " + player + " " + occupant + "))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col ?row" + str(i) +
                               " " + player + " " + occupant +"))")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " " + player + " " + occupant + "))")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row)")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\n\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " " + player + " " + occupant + "))")
            gdl_file.write(")\n\n")

def write_var_succ(gdl_file, ceiling, x=1, y=0):
    if x == 1 and y == 0:
        for i in range(1,ceiling):
            gdl_file.write("\n\t(succ ?col" + str(i) +
                           " ?col" + str(i+1) + ")")
    if x == 0 and y == 1:
        for i in range(1,ceiling):
            gdl_file.write("\n\t(succ ?row" + str(i) +
                           " ?row" + str(i+1) + ")")
    if x == 1 and y == 1:
        for i in range(1,ceiling):
            gdl_file.write("\n\t(succ ?col" + str(i) +
                           " ?col" + str(i+1) + ")")
            gdl_file.write("\n\t(succ ?row" + str(i) +
                           " ?row" + str(i+1) + ")")




