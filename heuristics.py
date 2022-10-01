import numpy as np

from utils import initiate_board, print_board, get_possible_moves


def distance_from_center(i, j, center_i, center_j):
    return np.sqrt((i - center_i) * (i - center_i) + (j - center_j) * (j - center_j))


def heuristic(board, number_ai_player):
    nbr_runs = [0, 0]
    total_distance = [0, 0]
    nbr_moves = [0, 0]

    center_i = board.shape[0] / 2
    center_j = board.shape[1] / 2

    # Count number of 2-pawn runs for each player
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            # Checks runs horizontally
            if j <= board.shape[1] - 2:
                if board[i, j] == board[i, j + 1] != -1:
                    nbr_runs[int(board[i, j])] += 1

            # Checks runs vertically
            if i <= board.shape[0] - 2:
                if board[i, j] == board[i + 1, j] != -1:
                    nbr_runs[int(board[i, j])] += 1

            # Check runs diagonally
            if i <= board.shape[0] - 2 and j <= board.shape[1] - 2:
                if board[i, j] == board[i + 1, j + 1] != -1:
                    nbr_runs[int(board[i, j])] += 1
            if i <= board.shape[0] - 2 and j >= 1:
                if board[i, j] == board[i + 1, j - 1] != -1:
                    nbr_runs[int(board[i, j])] += 1

            if board[i, j] != -1:
                # Compute distance from center
                total_distance[int(
                    board[i, j])] += distance_from_center(i, j, center_i, center_j)

                # Computer number of moves available
                nbr_moves[int(board[i, j])
                          ] += len(get_possible_moves(i, j, board))

    # heuristic of 2-runs
    h_runs = nbr_runs[number_ai_player] - nbr_runs[(number_ai_player + 1) % 2]

    # heuristic of total distance from center
    h_distance = 1 / (1 + total_distance[number_ai_player]) - \
        1 / (1 + total_distance[(number_ai_player + 1) % 2])

    # heuristic of number of moves available
    h_moves = nbr_moves[number_ai_player] - \
        nbr_moves[(number_ai_player + 1) % 2]

    return h_runs + h_distance + h_moves


if __name__ == "__main__":
    board = initiate_board(5, 4)
    board[1, 0] = -1
    board[0, 0] = 1
    board[1, 1] = 0
    print_board(board)
    h = heuristic(board, 0)
    print(h)
