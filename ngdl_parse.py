# This file is for all the functions relating to taking the
# semi-natural language input and using it to fill in the
# game classes (Board, Player, Pieces etc...).

import ngdl
import nltk

def get_grammar(choice):
    if choice == 1:
        grammar = nltk.parse_cfg("""
        S -> IF COND THEN RESULT | RESULT IF COND | PLAYER ACTION RESULT
        RESULT -> STATE | ACTION
        COND -> COND AND COND | COND OR COND | CONDLIST AND COND | CONDLIST OR COND | STATE | NOT STATE
        CONDLIST -> COND ',' CONDLIST | COND 
        STATE -> ENTITY STATE | ENTITY ACTION | STATE POSITION_RELATION BOARD_PART | ENTITY
        ENTITY -> PLAYER | PIECE | MOD PIECE | NUM PIECE | BOARD_PART | NUM BOARD_PART | TEMPORAL | NUM TEMPORAL | ENTITY PART_RELATION ENTITY 
        BOARD_PART -> MOD BOARD_PART
        ACTION -> NOT ACTION | POSSESS STATE | 'to' ACTION
        IF -> 'if' | 'when' | 'after' | 'by'
        THEN -> 'then' | ','
        NOT -> 'not' | 'neither'
        AND -> 'and'
        OR -> 'or'
        STATE -> 'in-a-row' | 'in-order' | 'full' | 'occupied' | EMPTY
        ACTION -> 'win' | 'lose' | 'end' | 'move' | 'capture' | 'place' | 'mark' 
        POSSESS -> 'get' | 'have'
        BOARD_PART -> 'board' | 'cell' | 'square' | 'row' | 'column' | 'side' | 'diagonal'
        TEMPORAL -> 'turn' | 'game' | 'match' | 'time'
        PLAYER -> 'player' | 'player' NUM | MOD 'player' | 'they' | 'their' | 'opponent' | 'whoever'
        PIECE -> 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king' | 'x' | 'o' | 'disc' | 'piece' | 'it'
        MOD -> 'most' | 'least' | 'first' | 'last' | 'middle' | 'center' | NUM 'x' NUM | NUM 'by' NUM | 'opposite' | 'full' | 'occupied' | EMPTY
        NUM_COMP -> 'more' | 'less' | 'greater' | 'fewer' | 'between' NUM AND NUM
        POSITION_RELATION -> 'on' | 'in' | 'to'
        PART_RELATION -> 'of'
        NUM -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'no' | 'all'
        EMPTY -> 'empty' | 'blank' | 'open'
        """)
    if choice == 2:
        grammar = nltk.parse_cfg("""
        S -> PLAYER ACTION | PLAYER ACTION IF COND | IF COND THEN PLAYER ACTION
        ACTION -> ACTION ENTITY | ACTION ENTITY RELATION ENTITY
        COND -> COND AND COND | COND OR COND | STATE
        STATE -> ENTITY STATE | NOT STATE | STATE RELATION ENTITY | ENTITY
        ENTITY -> PLAYER | PIECE | NUM PIECE | BOARD_PART | NUM BOARD_PART | TEMPORAL
        PIECE -> MOD PIECE
        BOARD_PART -> MOD BOARD_PART
        IF -> 'if' | 'when' | 'after'
        THEN -> 'then' | ','
        NOT -> 'not'
        AND -> 'and' | ','
        OR -> 'or' | ','
        STATE -> 'in-a-row' | 'in-order' | 'full' | 'occupied' | EMPTY
        ACTION -> 'mark' | 'place' | 'drop' | 'move' | 'capture'
        BOARD_PART -> 'board' | 'cell' | 'square' | 'row' | 'column' | 'side' | 'diagonal'
        TEMPORAL -> 'turn' | 'game' | 'time'
        PLAYER -> 'player' | 'player' NUM | MOD 'player' | 'they' | 'their' | 'opponent' | 'whoever'
        PIECE -> 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king' | 'x' | 'o' | 'disc' | 'piece' | 'it'
        MOD -> 'most' | 'least' | 'first' | 'last' | 'middle' | 'center' | NUM 'x' NUM | NUM 'by' NUM | 'opposite' | 'full' | 'occupied' | 'different' | EMPTY
        RELATION -> 'more' | 'less' | 'greater' | 'on' | 'in' | 'of'
        NUM -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'neither' | 'no' | 'all'
        EMPTY -> 'empty' | 'blank' | 'open'
        """)
    if choice == 3:
        grammar = nltk.parse_cfg("""
        S -> PIECE MOVETYPE | IF COND THEN PIECE MOVETYPE | PIECE MOVETYPE IF COND
        COND -> COND AND COND | COND OR COND | STATE
        STATE -> ENTITY STATE | NOT STATE | STATE RELATION ENTITY | ENTITY
        ENTITY -> PIECE | MOD PIECE | NUM PIECE | BOARD_PART | NUM BOARD_PART
        MOVETYPE ->
        IF -> 'if' | 'when' | 'after'
        THEN -> 'then' | ','
        NOT -> 'not'
        AND -> 'and' | ','
        OR -> 'or' | ','
        DIRECTION -> 'forward' | 'backward' | 'left' | 'right' | 'up' | 'down' | 'north' | 'south' | 'east' | 'west' | 'north-east' | 'south-east' | 'north-west' | 'south-west'
        ACTION -> 'move' | 'capture' | 'jump'
        PIECE -> 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king' | 'x' | 'o' | 'disc' | 'piece' | 'it'
        BOARD_PART -> 'board' | 'cell' | 'square' | 'row' | 'column' | 'side' | 'diagonal' | 'turn' | 'game'
        """)
    return grammar

def remove_stopwords(wordlist):
    stopwords = ['the', 'than', 'a', 'an', 'can', 'getting', 'at', '\'s', '\'', '.', 'there', 'be', 'that', 'any', 'who', 'with']

    return [w for w in wordlist if not w in stopwords]

def preprocess_text(sentence):
    lowercase = sentence.lower()
    
    wnl = nltk.WordNetLemmatizer()
    tokens = nltk.word_tokenize(lowercase)

    poslist = nltk.pos_tag(tokens)

    wordnet_tags = {'NN':'n','JJ':'a','VB':'v','RB':'r'}

    lemmas = []
    for t in range(len(tokens)):
        postag = poslist[t][1][:2]
        if postag not in wordnet_tags:
            lemma = wnl.lemmatize(tokens[t])
        else:
            lemma = wnl.lemmatize(tokens[t], wordnet_tags[postag])
        lemmas.append(lemma)

    return remove_stopwords(lemmas)

def parse(sentence, choice):
    grammar = get_grammar(choice)
    wordlist = preprocess_text(sentence)
    
    parser = nltk.ChartParser(grammar)

    trees = parser.nbest_parse(wordlist)

    for tree in trees:
        print tree

    #return trees

def testparser(sentence_file, choice):
    for sentence in open(sentence_file):
        sentence.strip()
        print sentence
        try:
            parse(sentence, choice)
        except ValueError:
            print "Error"

        print "\n"
    
