# This file contains the functions for taking
# the intermediate representation of the game
# and writing the corresponding gdl into a .kif.

import ngdl
import re

# Takes a board object and output file and
# writes gdl code to initialize the board
# in the file
def board(gdl_file, board):
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

# Initialize players
def players(gdl_file, player_list):
    for player in player_list:
        gdl_file.write("(role " + player.name + " )\n")

    gdl_file.write("\n")

    # The embedded loops are for if there is more than 2 players
    for player1 in player_list:
        for player2 in player_list:
            if player1 != player2:
                gdl_file.write("(opponent " + player1.name + " " +
                               player2.name + ")\n")
    gdl_file.write("\n")
        

# This a function that says that cells not involved in
# a legal move do not change from one state to the next
def perpetuate_untouched_cells(gdl_file):
    gdl_file.write("""(<= (next (cell ?col ?row ?cell_player ?occupant))
    (true (cell ?col ?row ?cell_player ?occupant))
    (or
        (does ?move_player (move ?occupant ?src_col ?src_row ?dest_col ?dest_row))
        (does ?move_player (place ?occupant ?dest_col ?dest_row)))
    (distinct_cells ?col ?row ?src_col ?src_row)
    (distinct_cells ?col ?row ?dest_col ?dest_row))\n\n""")    

def place_piece_next_state(gdl_file):
    gdl_file.write("""(<= (next (cell ?col ?row ?player ?occupant))
    (does ?player (place ?occupant ?col ?row))
    (true (cell ?col ?row none none)))""")

# Potentially legal player moves

def noop(gdl_file):
    gdl_file.write("""(<= (legal ?player noop)
    (role ?player)
    (not (true (control ?player))))\n\n""")

def place_occupant(gdl_file, conditions):
    gdl_file.write("(<= (legal ?player (place ?occupant ?col ?row))\n " +
                   insert_conditions(conditions))

########################################################
# This section contains a bunch of different constants #
# or predefined functions that might be necessary      #
########################################################

# We want to keep track of which definition functions we've
# already called so we aren't writing the same code into the
# gdl file multiple times

function_dict = {"less":0,
                 "distinct_cells":0,
                 "adjacent_cells":0,
                 "adjacent_cols":0,
                 "adjacent_rows":0,
                 "successors":0,
                 "board_open":0}

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

def distinct_cells(gdl_file):
    gdl_file.write("(<= (distinct_cells ?col1 ?row1 ?col2 ?row2) (distinct ?col1 ?col2))\n")
    gdl_file.write("(<= (distinct_cells ?col1 ?row1 ?col2 ?row2) (distinct ?row1 ?row2))\n\n")

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
    if function_dict["adjacent_cols"] == 0:
        adjacent_cols(gdl_file)
    if function_dict["adjacent_rows"] == 0:
        adjacent_rows(gdl_file) 

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
    (or (next_column ?col1 ?col2) (next_column ?col2 ?col1))\n\n""")

def adjacent_rows(gdl_file):
    gdl_file.write("""(<= (adjacent_rows ?row1 ?row2)
    (or (next_row ?row1 ?row2) (next_row ?row2 ?row1))\n\n""")

def board_open(gdl_file):
    gdl_file.write("(<= board_open (true (cell ?col ?row ?player none)))\n\n")

# This function is for creating code that tests if x
# number of cells in a row meet a certain condition.
# For now these conditions are either that the cells are
# controlled by the same player or contain the same occupant
# or both. Inputting "" means that condition is irrelavent.
# Inputting "same" means what the condition is doesn't matter
# it just has to be consistant across all the cells.
# Inputting some value means that value has to be true for
# every cell i.e. "none" for unowned or unoccupied cells
def x_in_a_row(gdl_file, x, player="same", occupant=""):
    if player == "same":
        if occupant == "":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row ?player ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " ?player ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")
            
        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row ?player ?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " ?player ?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player ?occupant))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player ?occupant))\n")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row ?player " + occupant + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " ?player " + occupant +"))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player " + occupant + "))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player " + occupant + "))\n")
            gdl_file.write(")\n\n")

    elif player == "":
        if occupant == "":
            # Its not actually undefined, but saying its useless doesn't sound
            # like a real error
            print "Error: undefined output"

        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row ?player" + str(i) + "?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " ?player" + str(i) + "?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player" + str(i) + "?occupant))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player" + str(i) + "?occupant))\n")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row ?player" + str(i) + " " + occupant + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " ?player" + str(i) + " " + occupant +"))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " ?player" + str(i) + " " + occupant + "))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " ?player" + str(i) + " " + occupant + "))\n")
            gdl_file.write(")\n\n")

    else:
        if occupant == "":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + "?row " +
                               player + " ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               player + " ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?player)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               player + " ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                                player + " ?occupant" + str(i) + "))\n")
            gdl_file.write(")\n\n")

        elif occupant == "same":
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row " + player + " ?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                                " " + player + " ?occupant))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                                " " + player + " ?occupant))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row ?occupant)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?x" + str(i) + " ?row" + str((x+1)-i) +
                                " " + player + " ?occupant))\n")
            gdl_file.write(")\n\n")

        else:
            gdl_file.write("(<= (" + str(x) + "_in_a_row)\n")
            write_var_succ(gdl_file, x)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) +
                               " ?row " + player + " " + occupant + "))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)\n")
            write_var_succ(gdl_file, x, 0, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col ?row" + str(i) +
                               " " + player + " " + occupant +"))\n")
            gdl_file.write(")\n\n")
                
            gdl_file.write("(<= (" + str(x) + "_in_a_row)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str(i) +
                               " " + player + " " + occupant + "))\n")
            gdl_file.write(")\n\n")

            gdl_file.write("(<= (" + str(x) + "_in_a_row)\n")
            write_var_succ(gdl_file, x, 1, 1)
            for i in range(1,x+1):
                gdl_file.write("\t(true (cell ?col" + str(i) + " ?row" + str((x+1)-i) +
                               " " + player + " " + occupant + "))\n")
            gdl_file.write(")\n\n")

def write_var_succ(gdl_file, ceiling, x=1, y=0):
    if x == 1 and y == 0:
        for i in range(1,ceiling):
            gdl_file.write("\t(succ ?col" + str(i) +
                           " ?col" + str(i+1) + ")\n")
    if x == 0 and y == 1:
        for i in range(1,ceiling):
            gdl_file.write("\t(succ ?row" + str(i) +
                           " ?row" + str(i+1) + ")\n")
    if x == 1 and y == 1:
        for i in range(1,ceiling):
            gdl_file.write("\t(succ ?col" + str(i) +
                           " ?col" + str(i+1) + ")\n")
            gdl_file.write("\t(succ ?row" + str(i) +
                           " ?row" + str(i+1) + ")\n")

#################################################
# Piece move definitions for pre-defined pieces #
#################################################

# X and O in Tic-Tac-Toe
def marker_move(gdl_file):
    return

###########################################################
# This section is for dealing with the various conditions #
# that might need to be satisfied.                        #
###########################################################

cond_dictionary = (("empty cell", "(true (cell ?col ?row ?player none))"),
                   ("uncontrolled cell", "(true (cell ?col ?row none ?occupant))"),
                   ("board open", "board_open"),
                   ("less"),
                   ("x-in-a-row"),
                   ())

#def insert_conditions(conditions):
#
#    for cond in conditions:
#        
