from tictactoe import player, actions, initial_state, result, winner, terminal, utility, minimax, max_value, min_value
X = "X"
O = "O"
EMPTY = None

board = [[X, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY]]

print(winner(board))