import ngdl_classes

initialized = False

def init():
    global write_queue
    global game
    global initialized
    write_queue = [["noop", []], ["goals", []], ["terminal", []], ["successors", [50]]]
    game = ngdl_classes.Game()
    initialized = True
