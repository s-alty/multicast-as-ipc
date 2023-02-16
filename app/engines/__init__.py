import random

# engine = func(board_state) -> move

def random_move(board_state):
    # TODO actually generate a list of the valid moves based on the board state and choose one at random
    moves = [
        'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
        'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
        'Na3', 'Nc3', 'Nf3', 'Nh3'
    ]
    return random.choice(moves)


ENGINES = {
    "random": random_move,
}
