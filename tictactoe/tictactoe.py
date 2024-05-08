"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Count how many X's and O's are on the board
    num_x = 0
    num_o = 0
    # Iterate through each tile and count X's and O's
    for row in board:
        for tile in row:
            if tile == X:
                num_x += 1
            elif tile == O:
                num_o += 1
    return O if num_x > num_o else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Initialize set for possible actions
    moves = set()
    # Iterate through tiles
    for row in range(len(board)):
        for tile in range(len(board[row])):
            # Count empty tiles and append tuples of location to moves set
            if board[row][tile] == EMPTY:
                moves.add((row, tile))
    return moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Make a copy of the board
    board_copy = copy.deepcopy(board)
    row, column = action
    # Index into copy and make move
    board_copy[row][column] = player(board)
    return board_copy

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check for winner
    rows = check_rows(board)
    if rows != None: return rows
    columns = check_columns(board)
    if columns != None: return columns
    diagonal = check_diagonal(board)
    if diagonal != None: return diagonal
    # If no winner, return None
    return None

                
def check_rows(board):
    for row in range(len(board)):
        tile = board[row][0]
        if tile == X or tile == O:
            if tile == board[row][1] == board[row][2]:
                return tile
    return None

def check_columns(board):
    for column in range(len(board)):
        tile = board[0][column]
        if tile == X or tile == O:
            if tile == board[1][column] == board[2][column]:
                return tile
    return None

def check_diagonal(board):
    top_left, top_right, middle, bottom_left, bottom_right = board[0][0], board[0][2], board[1][1], board[2][0], board[2][2]
    if top_left == middle == bottom_right and top_left != EMPTY:
        return top_left
    elif top_right == middle == bottom_left and top_right != EMPTY:
        return top_right
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == EMPTY:
                return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)
    if result == X:
        return 1
    elif result == O:
        return -1
    return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Return None if game is over
    if terminal(board):
        return None
    # If it is X's turn
    elif player(board) == X:
        # If it is the first move, put X in the center
        if board == initial_state():
            return (1,1)
        options = []
        # Iterate over possible actions
        for action in actions(board):
            value = min_value(result(board, action))
            # Take note of max_value and action, only if value is greater than current value
            options.append([value, action])
        # Return action with the highest max_value
        return sorted(options, key=lambda x: x[0], reverse=True)[0][1]

    # If it is O's turn
    elif player(board) == O:
        options = []
        # Iterate over possible actions
        for action in actions(board):
            value = max_value(result(board, action))
            # Take note of min_value and action
            options.append([value, action])
        # Return action with lowest min_value
        return sorted(options, key=lambda x: x[0])[0][1]

def max_value(board):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v