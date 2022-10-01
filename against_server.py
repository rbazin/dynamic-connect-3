import numpy as np
from time import time
import socket
import argparse
import sys

from utils import initiate_board, print_board, take_action, get_children_states
from heuristics import heuristic

# We don't use np min and max value to save memory space
MAX_VALUE = 1000
MIN_VALUE = - 1000
MAX_DEPTH = 8
TIME_LIMIT = 10  # time limit to play the turn


SERVER = "156trlinux-1.ece.mcgill.ca"
PORT = 12345
BUFFER_SIZE = 1024


def check_eligibility(board, action, player_number):
    x, y, direction = action

    i, j = int(y) - 1, int(x) - 1

    if i < 0 or j < 0 or i > board.shape[0] - 1 or j > board.shape[1] - 1:
        return False

    if board[i, j] != player_number:
        return False

    # Catches pawn already there errors
    if j < board.shape[1] - 2 and direction == "E":
        if board[i, j + 1] != -1:
            return False
        else:
            return True

    if j > 0 and direction == "W":
        if board[i, j - 1] != -1:
            return False
        else:
            return True

    if i > 0 and direction == "N":
        if board[i - 1, j] != -1:
            return False
        else:
            return True

    if i < board.shape[0] - 2 and direction == "S":
        if board[i + 1, j] != -1:
            return False
        else:
            return True

    return False


def check_winner(board):
    """ Checks if someone won the game 

        Returns:
            0 : if player 0 won
            1 : if player 1 won
            -1 : if none won
    """
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            # Check vertical win
            if i <= board.shape[0] - 3:
                if board[i, j] == board[i + 1, j] == board[i + 2, j] != -1:
                    return int(board[i, j])
            # Check vertical win
            if j <= board.shape[1] - 3:
                if board[i, j] == board[i, j + 1] == board[i, j + 2] != -1:
                    return int(board[i, j])
            # Check diagonal wins
            if j <= board.shape[1] - 3 and i <= board.shape[0] - 3:
                if board[i, j] == board[i + 1, j + 1] == board[i + 2, j + 2] != -1:
                    return int(board[i, j])

            if j >= 2 and i <= board.shape[0] - 3:
                if board[i, j] == board[i + 1, j - 1] == board[i + 2, j - 2] != -1:
                    return int(board[i, j])

    return -1


def move(player_type, player_number, board, socket):

    if player_type == "agent":
        start = time()
        remaining_time = TIME_LIMIT - start
        action, _ = minimax(board, MAX_DEPTH, MIN_VALUE,
                            MAX_VALUE, player_number, player_number, remaining_time)
        end = time()

        MESSAGE = action + "\n"
        socket.send(bytes(MESSAGE, "utf-8"))
        _ = socket.recv(BUFFER_SIZE)  # echo of the action

        print("Your action :", action)
        print(f"Time to compute minimax : {end - start}s")

        board = take_action(player_number, board, action)

    elif player_type == "opponent":

        action = socket.recv(BUFFER_SIZE)
        action = action.decode("utf-8")[:-1]

        if not check_eligibility(board, action, player_number):
            print("Opponent's action not legal")

        print("Opponent's action :", action)
        board = take_action(player_number, board, action)

    return board


def evaluation_function(board, potential_winner, number_ai_player):

    # Check for winners
    if potential_winner == number_ai_player:
        return 100
    elif potential_winner == (number_ai_player + 1) % 2:
        return -100

    return heuristic(board, number_ai_player)


def minimax(board, depth, alpha, beta, player_number, number_ai_player, start_time):
    """Minimax function with alpha beta prunning

        Returns
            action : action that leads to the best state evaluated
            value : min or max value evaluated for this action
    """
    print("Depth :", depth)

    potential_winner = check_winner(board)
    if depth == 0 or potential_winner != -1:  # Checks for winner or draw
        return None, evaluation_function(board, potential_winner, number_ai_player)

    if player_number == number_ai_player:
        max_eval = MIN_VALUE
        for action, child_state in get_children_states(board, player_number):

            _, value = minimax(child_state, depth - 1,
                               alpha, beta, (player_number + 1) % 2, number_ai_player, start_time)

            if max_eval <= value:
                max_eval = value
                max_action = action

            now = time()
            remaining_time = TIME_LIMIT - (now - start_time)
            if remaining_time <= 2.0:
                break

            alpha = np.max((alpha, value))

            if beta <= alpha:
                break

        return max_action, max_eval

    else:
        min_eval = MAX_VALUE
        for action, child_state in get_children_states(board, player_number):

            _, value = minimax(child_state, depth - 1,
                               alpha, beta, (player_number + 1) % 2, number_ai_player, start_time)

            if min_eval >= value:
                min_eval = value
                min_action = action

            now = time()
            remaining_time = TIME_LIMIT - (now - start_time)
            if remaining_time <= 2.0:
                break

            beta = np.min((beta, value))

            if beta <= alpha:
                break
        return min_action, min_eval


def get_args():
    parser = argparse.ArgumentParser(
        description='Launch dynamic connect-3 against server')
    parser.add_argument('--game_id', type=str, required=True,
                        help='the game id identifier (Eg : game07)')
    parser.add_argument('--color', type=str, required=True,
                        help='color of the agent (white is represented as 0, black as 1)')
    parser.add_argument('--size_grid', type=int, required=False, default=1,
                        help="size of the grid, select 1 for 5x4 or 2 for 7x6 (default is 5x4)")

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = get_args()
    game_id = args.game_id

    color = args.color
    assert color == "white" or color == "black", "please select either white or black"

    size_grid = args.size_grid
    assert size_grid == 1 or size_grid == 2, "please select 1 or 2 for the size of the grid"

    if color == "white":
        player0_type = "agent"
        player1_type = "opponent"
    else:
        player0_type = "opponent"
        player1_type = "agent"

    if size_grid == 1:
        board = initiate_board(5, 4)
    else:
        board = initiate_board(7, 6)

    print_board(board)

    MESSAGE = str(game_id) + " " + color + "\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))
    s.send(bytes(MESSAGE, "utf-8"))
    # wait for confirmation from the server
    answer = s.recv(BUFFER_SIZE)
    print(answer.decode("utf-8"))

    finished = False

    while not finished:
        board = move(player0_type, 0, board, s)
        print_board(board)
        if check_winner(board) == 0:
            finished = True
            winner = 0
        else:
            board = move(player1_type, 1, board, s)
            print_board(board)
            if check_winner(board) == 1:
                finished = True
                winner = 1

    winner_color = "black" if winner == 1 else "white"
    print(f"Winner is player {winner_color}, congratulations !")
