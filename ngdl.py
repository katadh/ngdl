import ngdl_classes
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
        in_piece_names = raw_input("What pieces does " + player.name " have?: ")
        pieces = re.findall("([0-9]*)\s|^([^\W\d_]+)", in_piece_list)
        for piece in pieces:

