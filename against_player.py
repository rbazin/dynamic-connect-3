import numpy as np
from time import time

# We don't use np min and max value to save memory space
MAX_VALUE = 1000
MIN_VALUE = - 1000
MAX_DEPTH = 8
PRUNING = True


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


ai_turns_durations = []


def move(player_type, player_number, board):
    if player_type == "human":
        print("Please choose an action\n")
        action = input()
        eligible = check_eligibility(board, action, player_number)
        while not eligible:
            print("Please select an eligible action\n")
            action = input()
            eligible = check_eligibility(board, action, player_number)
        board = take_action(player_number, board, action)

    elif player_type == "ai":
        start = time()
        if PRUNING == True:
            print("using pruning")
            action, _ = minimax(board, MAX_DEPTH, MIN_VALUE,
                                MAX_VALUE, player_number, player_number)
        else:
            print("not pruning")
            action, _ = minimax_without_prunning(
                board, MAX_DEPTH, player_number, player_number)
        end = time()
        ai_turns_durations.append(end - start)
        print(f"Time to compute minimax : {end - start}s")
        board = take_action(player_number, board, action)

    elif player_type == "other_ai":
        # TODO : Get the action from the server
        board = take_action(player_number, board, action)

    return board


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


def heuristic(board, number_ai_player):
    nbr_runs = [0, 0]

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

    return nbr_runs[number_ai_player] - nbr_runs[(number_ai_player + 1) % 2]


def evaluation_function(board, potential_winner, number_ai_player):

    # Check for winners
    if potential_winner == number_ai_player:
        return 100
    elif potential_winner == (number_ai_player + 1) % 2:
        return -100

    return heuristic(board, number_ai_player)


def minimax_without_prunning(board, depth, player_number, number_ai_player):
    """Minimax function with alpha beta prunning

        Returns
            action : action that leads to the best state evaluated
            value : min or max value evaluated for this action
    """

    potential_winner = check_winner(board)
    if depth == 0 or potential_winner != -1:  # Checks for winner or draw
        return board, evaluation_function(board, potential_winner, number_ai_player)

    if player_number == number_ai_player:
        max_eval = MIN_VALUE
        for action, child_state in get_children_states(board, player_number):
            _, value = minimax_without_prunning(child_state, depth - 1,
                                                (player_number + 1) % 2, number_ai_player)
            if max_eval <= value:
                max_eval = value
                max_action = action

        return max_action, max_eval

    else:
        min_eval = MAX_VALUE
        for action, child_state in get_children_states(board, player_number):
            _, value = minimax_without_prunning(child_state, depth - 1,
                                                (player_number + 1) % 2, number_ai_player)
            if min_eval >= value:
                min_eval = value
                min_action = action

        return min_action, min_eval


def minimax(board, depth, alpha, beta, player_number, number_ai_player):
    """Minimax function with alpha beta prunning

        Returns
            action : action that leads to the best state evaluated
            value : min or max value evaluated for this action
    """

    potential_winner = check_winner(board)
    if depth == 0 or potential_winner != -1:  # Checks for winner or draw
        return board, evaluation_function(board, potential_winner, number_ai_player)

    if player_number == number_ai_player:
        max_eval = MIN_VALUE
        for action, child_state in get_children_states(board, player_number):
            _, value = minimax(child_state, depth - 1,
                               alpha, beta, (player_number + 1) % 2, number_ai_player)
            if max_eval <= value:
                max_eval = value
                max_action = action
            alpha = np.max((alpha, value))
            if beta <= alpha:
                break
        return max_action, max_eval

    else:
        min_eval = MAX_VALUE
        for action, child_state in get_children_states(board, player_number):
            _, value = minimax(child_state, depth - 1,
                               alpha, beta, (player_number + 1) % 2, number_ai_player)
            if min_eval >= value:
                min_eval = value
                min_action = action
            beta = np.min((beta, value))
            if beta <= alpha:
                break
        return min_action, min_eval


def main():
    print("Welcome to dynamic connect-3 !")
    print("Please choose your player (0 = white or 1 = black) :")
    number_human = int(input())
    assert number_human == 0 or number_human == 1, "Please choose between 0 and 1"

    if number_human == 0:
        player0_type = "human"
        player1_type = "ai"
    else:
        player0_type = "ai"
        player1_type = "human"

    print("Please choose the size of the grid (1 for 5x4, 2 for 7x6)")
    number_grid = int(input())
    assert number_grid == 1 or number_grid == 2, "Please choose between 1 and 2"

    if number_grid == 1:
        w, h = 5, 4
    else:
        w, h = 7, 6

    board = initiate_board(w, h)
    print_board(board)

    finished = False

    while not finished:
        board = move(player0_type, 0, board)
        print_board(board)
        if check_winner(board) == 0:
            finished = True
            winner = 0
        else:
            board = move(player1_type, 1, board)
            print_board(board)
            if check_winner(board) == 1:
                finished = True
                winner = 1

    print_board(board)
    winner_color = "black" if winner == 1 else "white"
    print(f"Winner is player {winner_color}, congratulations !")


def graph_time():

    player0_type = "ai"
    player1_type = "ai"

    number_grid = 1

    if number_grid == 1:
        w, h = 5, 4
    else:
        w, h = 7, 6

    board = initiate_board(w, h)
    print_board(board)

    finished = False

    counter = 0

    while not finished:
        board = move(player0_type, 0, board)
        print_board(board)
        counter += 1
        if check_winner(board) == 0:
            finished = True
            winner = 0
        else:
            board = move(player1_type, 1, board)
            print_board(board)
            counter += 1
            if check_winner(board) == 1:
                finished = True
                winner = 1
        if counter == 10:
            print(ai_turns_durations)
            print("Number of turns :", len(ai_turns_durations))
            with open("res.txt", "a") as f:
                for turn_duration in ai_turns_durations:
                    f.write(str(turn_duration) + ",")
                f.write("\n")

    print_board(board)
    winner_color = "black" if winner == 1 else "white"
    print(f"Winner is player {winner_color}, congratulations !")


if __name__ == "__main__":

    graph_time()
