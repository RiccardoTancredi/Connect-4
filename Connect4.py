import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
from const import *
import sys
import pygame

board = np.ones((6, 7), dtype=str)
board

moveX = 'X'
moveO = 'O'
# board[0, 0] = moveO

def print_board(board):
    print("-----------------------------")
    rows, cols = board.shape
    board_to_print = board.copy()
    for i in range(rows-1, -1, -1):
        for j in range(cols-1, -1, -1):
            if board[i, j] == "1":
                board_to_print[i, j] = " " 
        print(f"| {board_to_print[i, 0]} | {board_to_print[i, 1]} | {board_to_print[i, 2]} | {board_to_print[i, 3]} | {board_to_print[i, 4]} | {board_to_print[i, 5]} | {board_to_print[i, 6]} |")
    print("-----------------------------")

def possible_move(board, x, y):
    if x > 0 and board[x-1, y] == "1": #and board[x, y] == "1":
        return False
    elif board[x, y] in ["X", "O"]:
        return False
    else:
        return True

def make_move(board, piece, x, y):
    if possible_move(board, x, y):
        board[x, y] = piece
    else:
        return False
    return board

def ending_condition(board, piece):
    # This function must check correctly if there are 4 elements connected somehow
    # players = ["X", "O"]
    rows, cols = board.shape
    # Check horizontal locations for win
    for c in range(cols-3):
        for r in range(rows):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(cols):
        for r in range(rows-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(cols-3):
        for r in range(rows-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(cols-3):
        for r in range(3, rows):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def checktie(board):
    flat = board.flatten()
    if "1" not in flat:
        return True # it's a tie
    return False
def create_board():
    board = np.ones((6, 7), dtype=str)
    return board

# ## The game: Min-Max algorithm
length = 4
player_piece = moveX
AI_piece = moveO
rows, cols = board.shape

def is_valid_location(board, col):
    return board[rows-1][col] == "1"

def get_valid_locations(board):
    valid_locations = []
    for col in range(cols):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def evaluate_window(window, piece):
    score = 0
    opp_piece = player_piece
    if piece == player_piece:
        opp_piece = AI_piece

    if window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 3 and window.count("1") == 1:
        score += 500
    elif window.count(piece) == 2 and window.count("1") == 2:
        score += 20

    if window.count(opp_piece) == 3 and window.count("1") == 1:
        score -= 400

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [i for i in list(board[:, cols//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(rows):
        row_array = [i for i in list(board[r,:])]
        for c in range(cols-3):
            window = row_array[c:c+length]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(cols):
        col_array = [i for i in list(board[:,c])]
        for r in range(rows-3):
            window = col_array[r:r+length]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(rows-3):
        for c in range(cols-3):
            window = [board[r+i][c+i] for i in range(length)]
            score += evaluate_window(window, piece)

    for r in range(rows-3):
        for c in range(cols-3):
            window = [board[r+3-i][c+i] for i in range(length)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return ending_condition(board, player_piece) or ending_condition(board, AI_piece) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if ending_condition(board, AI_piece):
                return (None, 100000000000000)
            elif ending_condition(board, player_piece):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_piece))
    if maximizingPlayer:
        value = -np.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            b_copy = drop_piece(b_copy, row, col, AI_piece)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = np.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            b_copy = drop_piece(b_copy, row, col, player_piece)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_next_open_row(board, col):
    for r in range(rows):
        if board[r][col] == "1":
            return r

def drop_piece(board, row, col, piece):
    board[row, col] = piece
    return board

def pick_best_move(board, piece):

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = np.random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        temp_board = drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

 
#define width and height of board
width = cols * SQUARESIZE
height = (rows+1) * SQUARESIZE
 
size = (width, height)

def draw_board(board):
    for c in range(cols):
        for r in range(rows):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
     
    for c in range(cols):
        for r in range(rows):      
            if board[r][c] == moveX:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == moveO: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

#initalize pygame
pygame.init()
screen = pygame.display.set_mode(size)
#Calling function draw_board again
draw_board(board)
pygame.display.update()
myfont = pygame.font.SysFont("monospace", 75)

run = True
turn = 0
board = create_board()
print_board(board)
while run:
    # player1: X
    # player2: O ----> computer 
    players = [moveX, moveO]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            #print(event.pos)
            # Ask for Player 1 Input
            if turn == 0:
                posx = event.pos[0]
                col = int(np.floor(posx/SQUARESIZE))
                # x, y = col, int(np.floor(posx/SQUARESIZE)) # swap coordinates since we are flipping how we are indexing the board 
                # new_board = make_move(board, players[turn], x, y)
                
                # if type(new_board) != bool:
                #     board = new_board.copy()
                #     # print_board(board)
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    board = drop_piece(board, row, col, moveX)
                    turn += 1
                    turn = turn % 2
                if ending_condition(board, players[turn]):
                    print(f"{players[turn]} won the game!!!")
                    label = myfont.render("Player 1 wins!!", 1, RED)
                    screen.blit(label, (40,10))
                    run = False
                    
                    # # Ask for Player 2 Input
        # else:
            if turn != 0:              
                col, minimax_score = minimax(board, 5, -np.inf, np.inf, True)
 
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    board = drop_piece(board, row, col, moveO) 
                    pygame.draw.circle(screen, YELLOW, (int((row*SQUARESIZE)), int(SQUARESIZE/2)), RADIUS)
                
                pygame.display.update()
                
                if ending_condition(board, AI_piece):
                    print(f"{players[turn]} won the game!!!")
                    run = False
                    # print_board(board)
            
            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2
 
        if not run:
            pygame.time.wait(3000)


# ### Useful resources
# * [Decision tree in Connect Four](https://medium.com/analytics-vidhya/artificial-intelligence-at-play-connect-four-minimax-algorithm-explained-3b5fc32e4a4f)
# * [Connect4 in Python](https://www.askpython.com/python/examples/connect-four-game)
# * [Min Max Algorithm](http://blog.gamesolver.org/solving-connect-four/03-minmax/#:~:text=The%20MinMax%20algorithm,that%20will%20maximize%20your%20score.)


