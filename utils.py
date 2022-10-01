import numpy as np


def initiate_board(w, h):
    board = -1 * np.ones((h, w))
    if (h, w) == (6, 7):
        board[0 + 1, 0 + 1] = 0
        board[0 + 1, w - 1 - 1] = 1
        board[1 + 1, 0 + 1] = 1
        board[1 + 1, w - 1 - 1] = 0
        board[2 + 1, 0 + 1] = 0
        board[2 + 1, w - 1 - 1] = 1
        board[3 + 1, 0 + 1] = 1
        board[3 + 1, w - 1 - 1] = 0
    else:
        board[0, 0] = 0
        board[0, w - 1] = 1
        board[1, 0] = 1
        board[1, w - 1] = 0
        board[2, 0] = 0
        board[2, w - 1] = 1
        board[3, 0] = 1
        board[3, w - 1] = 0

    return board


def print_board(board):
    for i in range(board.shape[0]):
        line_str = ''
        for j in range(board.shape[1]):
            if board[i, j] == -1:
                line_str += ' '
            elif board[i, j] == 0:
                line_str += "0"
            elif board[i, j] == 1:
                line_str += "1"

            if j != board.shape[1] - 1:
                line_str += ","
        print(line_str)


def get_possible_moves(i, j, board):
    possible_moves = []

    if i <= board.shape[0] - 2:
        if board[i + 1][j] == -1:
            possible_moves.append(f"{j + 1}{i + 1}S")
    if i >= 1:
        if board[i - 1][j] == -1:
            possible_moves.append(f"{j + 1}{i + 1}N")
    if j <= board.shape[1] - 2:
        if board[i][j + 1] == -1:
            possible_moves.append(f"{j + 1}{i + 1}E")
    if j >= 1:
        if board[i][j - 1] == -1:
            possible_moves.append(f"{j + 1}{i + 1}W")

    return possible_moves


def get_children_states(board, player_number):
    actions_and_children_states = []
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if board[i][j] == player_number:
                possible_moves = get_possible_moves(i, j, board)
                for possible_move in possible_moves:
                    child = take_action(player_number, board, possible_move)
                    actions_and_children_states.append((possible_move, child))
    return actions_and_children_states


def take_action(player_number, board, action):
    """ Creates a new board based on the action provided. 
    Assumes the action is possible
    """

    x, y, direction = action
    i, j = int(y) - 1, int(x) - 1
    new_board = board.copy()
    new_board[i, j] = -1

    if direction == "E":
        new_board[i, j + 1] = player_number
    elif direction == "W":
        new_board[i, j - 1] = player_number
    elif direction == "N":
        new_board[i - 1, j] = player_number
    elif direction == "S":
        new_board[i + 1, j] = player_number

    return new_board
