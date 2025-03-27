from game.board import Board
from search.minmax import Minmax

def main():
    board = Board()
    board.print_board()
    minmax = Minmax()
    best_move = minmax.get_best_move(board, 'W')
    print("Best move:", best_move)

if __name__ == "__main__":
    main()