# This file is for all the functions relating to taking the
# semi-natural language input and using it to fill in the
# game classes (Board, Player, Pieces etc...).

import ngdl
import nltk

def get_grammar(choice):
    if choice == 1:
        grammar = nltk.parse_cfg("""
        S -> IF COND THEN RESULT | RESULT IF COND | ENTITY COND RESULT
        RESULT -> STATE
        COND -> COND AND COND | COND OR COND | STATE
        STATE -> ENTITY STATE | NOT STATE | STATE RELATION ENTITY | ENTITY
        ENTITY -> PLAYER | PIECE | MOD PIECE | NUM PIECE | BOARD_PART | NUM BOARD_PART
        BOARD_PART -> MOD BOARD_PART
        IF -> 'if' | 'when' | 'after'
        THEN -> 'then' | ','
        NOT -> 'not'
        AND -> 'and' | ','
        OR -> 'or' | ','
        STATE -> 'in-a-row' | 'in-order' | 'empty' | 'blank' | 'open' | 'full' | 'occupied' | 'win' | 'lose' | 'end' | 'move' | 'capture'
        BOARD_PART -> 'board' | 'cell' | 'square' | 'row' | 'column' | 'side' | 'diagonal' | 'turn' | 'game'
        PLAYER -> 'player' | 'player' NUM | MOD 'player' | 'they' | 'opponent' | 'whoever'
        PIECE -> 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king' | 'x' | 'o' | 'disc' | 'piece' | 'it'
        MOD -> 'most' | 'least' | 'first' | 'last' | 'middle' | 'center' | NUM 'x' NUM | NUM 'by' NUM | 'opposite' | 'empty' | 'blank' | 'open' | 'full' | 'occupied'
        RELATION -> 'more' | 'less' | 'greater' | 'on' | 'in' | 'of'
        NUM -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'neither' | 'no' | 'all'
        """)
    if choice == 2:
        grammar = nltk.parse_cfg("""
        S -> PLAYER ACTION | PLAYER ACTION IF COND | IF COND THEN PLAYER ACTION
        ACTION -> ACTION ENTITY | ACTION ENTITY RELATION ENTITY
        COND -> COND AND COND | COND OR COND | STATE
        STATE -> ENTITY STATE | NOT STATE | STATE RELATION ENTITY | ENTITY
        ENTITY -> PLAYER | PIECE | MOD PIECE | NUM PIECE | BOARD_PART | NUM BOARD_PART
        BOARD_PART -> MOD BOARD_PART
        IF -> 'if' | 'when' | 'after'
        THEN -> 'then' | ','
        NOT -> 'not'
        AND -> 'and' | ','
        OR -> 'or' | ','
        STATE -> 'in-a-row' | 'in-order' | 'empty' | 'blank' | 'open' | 'full' | 'occupied'
        ACTION -> 'mark' | 'place' | 'drop' | 'move' | 'capture'
        BOARD_PART -> 'board' | 'cell' | 'square' | 'row' | 'column' | 'side' | 'diagonal' | 'turn' | 'game'
        PLAYER -> 'player' | 'player' NUM | MOD 'player' | 'they' | 'their' | 'opponent' | 'whoever'
        PIECE -> 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king' | 'x' | 'o' | 'disc' | 'piece' | 'it'
        MOD -> 'most' | 'least' | 'first' | 'last' | 'middle' | 'center' | NUM 'x' NUM | NUM 'by' NUM | 'opposite' | 'empty' | 'blank' | 'open' | 'full' | 'occupied'
        RELATION -> 'more' | 'less' | 'greater' | 'on' | 'in' | 'of'
        NUM -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'neither' | 'no' | 'all'
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

def remove_stopwords(wordlist, choice):
    if choice == 1:
        stopwords = ['the', 'than', 'a', 'an', 'can', 'get', 'at', '\'s', '\'', '.', 'to', 'there', 'be', 'that']
    if choice == 2:
        stopwords = ['the', 'than', 'a', 'an', 'can', 'get', 'at', '\'s', '\'', '.', 'to', 'there', 'be', 'that', 'any']

    return [w for w in wordlist if not w in stopwords]

def preprocess_text(sentence, choice):
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

    return remove_stopwords(lemmas, choice)

def parse(sentence, choice):
    grammar = get_grammar(choice)
    wordlist = preprocess_text(sentence, choice)
    
    parser = nltk.ChartParser(grammar)

    trees = parser.nbest_parse(wordlist)

    for tree in trees:
        print tree

    return trees
