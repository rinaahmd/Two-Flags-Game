import copy

class ChessBoard:
    def __init__(self):
        self.boardArray = [[' ' for _ in range(8)] for _ in range(8)]
        self.initialize_pawns()
        self.last_move = None
        self.last_move_was_two_square = False
        
        # This square marks the potential en passant capture location.
        # For example, if White moves a pawn from (6, col) to (4, col),
        # we set en_passant_target = (5, col). That is where an opposing
        # pawn could capture en passant on the very next move.
        self.en_passant_target = None
        
        # Move history for potential undo functionality
        self.move_history = []

    def initialize_pawns(self):
        """Initialize the board with pawns: White on row 6, Black on row 1."""
        # Place white pawns on row 6
        for col in range(8):
            self.boardArray[6][col] = 'W'
        # Place black pawns on row 1
        for col in range(8):
            self.boardArray[1][col] = 'B'

    def clear_board(self):
        """Clear the board for new setup"""
        self.boardArray = [[' ' for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.last_move_was_two_square = False
        self.en_passant_target = None
        self.move_history = []

    def copy(self):
        """
        Create a deep copy of the board
        
        :return: A new ChessBoard instance with the same state
        """
        new_board = ChessBoard()
        new_board.boardArray = copy.deepcopy(self.boardArray)
        new_board.last_move = copy.deepcopy(self.last_move)
        new_board.last_move_was_two_square = self.last_move_was_two_square
        new_board.en_passant_target = copy.deepcopy(self.en_passant_target)
        new_board.move_history = copy.deepcopy(self.move_history)
        return new_board

    def get_valid_moves(self, row, col):
        """
        Return all valid (to_row, to_col) moves for a pawn located at (row, col).
        This includes:
            - Single-square forward moves (if empty)
            - Two-square forward (if on initial rank and both squares are empty)
            - Normal diagonal captures
            - En passant captures (if self.en_passant_target is set and applicable)
        """
        moves = []
        player = self.boardArray[row][col]
        
        if player not in ('W', 'B'):
            return moves  # No pawn here

        # White moves "up" (row decreases), black moves "down" (row increases)
        direction = -1 if player == 'W' else 1
        
        def on_board(r, c):
            return 0 <= r < 8 and 0 <= c < 8

        # 1) Single-square forward
        one_step_row = row + direction
        if on_board(one_step_row, col) and self.boardArray[one_step_row][col] == ' ':
            moves.append((one_step_row, col))

            # 2) Two-square forward (if on initial rank and path is clear)
            # White pawns start on row 6, black pawns start on row 1
            if (player == 'W' and row == 6) or (player == 'B' and row == 1):
                two_step_row = row + 2 * direction
                if on_board(two_step_row, col) and self.boardArray[two_step_row][col] == ' ':
                    moves.append((two_step_row, col))

        # 3) Normal diagonal captures
        for dc in (-1, 1):  # left diagonal, right diagonal
            diag_row = row + direction
            diag_col = col + dc
            if on_board(diag_row, diag_col):
                target_piece = self.boardArray[diag_row][diag_col]
                # White can capture black, black can capture white
                if (player == 'W' and target_piece == 'B') or (player == 'B' and target_piece == 'W'):
                    moves.append((diag_row, diag_col))

        # 4) En passant capture:
        #    If self.en_passant_target = (r, c), and (r, c) is exactly one diagonal
        #    forward from (row, col), that is a valid en passant capture square.
        if self.en_passant_target:
            en_r, en_c = self.en_passant_target
            # Pawn must move to row+direction, col±1 to match (en_r, en_c).
            if on_board(en_r, en_c):
                if en_r == row + direction and abs(en_c - col) == 1:
                    # The diagonal squares line up, so it's a valid en passant move
                    moves.append((en_r, en_c))

        return moves

    def computeMove(self, move, player):
        """
        Execute a move on the board with comprehensive En Passant handling
        
        :param move: Tuple (from_row, from_col, to_row, to_col)
        :param player: Player color ('W' or 'B')
        :return: True if the move was executed successfully and the game is not over, 
                False if illegal, or 'win' if the move resulted in a win.
        """
        from_row, from_col, to_row, to_col = move
        
        # Save the previous state for potential undo
        previous_state = {
            'board': copy.deepcopy(self.boardArray),
            'last_move': self.last_move,
            'last_move_was_two_square': self.last_move_was_two_square,
            'en_passant_target': self.en_passant_target
        }
        self.move_history.append(previous_state)
        
        # Verify the piece belongs to the player
        if self.boardArray[from_row][from_col] != player:
            return False
        
        self.last_move = move
        piece = self.boardArray[from_row][from_col]
        
        # Check if this is a two-square pawn move
        self.last_move_was_two_square = (abs(from_row - to_row) == 2)
        
        # Determine movement direction
        direction = -1 if player == 'W' else 1

        if self.last_move_was_two_square:
            # If the pawn just moved two squares, set en_passant_target
            # to the middle square behind the pawn.
            mid_row = (from_row + to_row) // 2
            self.en_passant_target = (mid_row, from_col)
        else:
            # Possibly an en passant capture
            is_en_passant = False
            if self.en_passant_target:
                en_r, en_c = self.en_passant_target
                is_en_passant = (
                    (to_row, to_col) == (en_r, en_c)
                    and abs(to_col - from_col) == 1
                    and to_row == from_row + direction
                )
            
            if is_en_passant:
                # Remove the captured pawn
                self.boardArray[from_row][to_col] = ' '
            
            # Reset en_passant_target if move was NOT a two-square advance
            self.en_passant_target = None

        # Place the moving piece on the new square
        self.boardArray[to_row][to_col] = piece
        # Vacate the old square
        self.boardArray[from_row][from_col] = ' '
        
        # Check if the move resulted in a win
        if self.check_win(player):
            return 'win'  # Indicate that the game is over and the player has won
        
        return True

    def undo_move(self):
        """Undo the last move if possible"""
        if not self.move_history:
            return False
            
        previous_state = self.move_history.pop()
        self.boardArray = previous_state['board']
        self.last_move = previous_state['last_move']
        self.last_move_was_two_square = previous_state['last_move_was_two_square']
        self.en_passant_target = previous_state['en_passant_target']
        
        return True

    def check_win(self, player):
        """
        Check if the given player has won the game.
        Win conditions:
        1. Reach the opposite side of the board (row 0 for White, row 7 for Black)
        2. Capture all opponent pieces
        3. Opponent has no legal moves
        
        :param player: Player color ('W' or 'B')
        :return: True if the player has won, False otherwise
        """
        opponent = 'B' if player == 'W' else 'W'
        
        # Win condition 1: Reach the opposite end
        target_row = 0 if player == 'W' else 7
        for col in range(8):
            if self.boardArray[target_row][col] == player:
                return True
                
        # Win condition 2: Capture all opponent pieces
        opponent_count = 0
        for row in range(8):
            for col in range(8):
                if self.boardArray[row][col] == opponent:
                    opponent_count += 1
        
        if opponent_count == 0:
            return True
            
        # Win condition 3: Opponent has no legal moves
        opponent_has_moves = False
        for row in range(8):
            for col in range(8):
                if self.boardArray[row][col] == opponent:
                    if self.get_valid_moves(row, col):
                        opponent_has_moves = True
                        break
            if opponent_has_moves:
                break
                
        if not opponent_has_moves and opponent_count > 0:
            return True
            
        return False
   
    def describe_en_passant_moves(self, row, col):
        """
        Describe possible En Passant moves for a specific pawn.
        """
        moves = []
        player = self.boardArray[row][col]
        
        if player not in ('W', 'B'):
            return moves
            
        if not self.en_passant_target:
            return moves
            
        en_r, en_c = self.en_passant_target
        direction = -1 if player == 'W' else 1
        
        # Check if this pawn can perform an en passant capture
        if en_r == row + direction and abs(en_c - col) == 1:
            moves.append((row, col, en_r, en_c))
            
        return moves

    def count_pawns(self, player):
        """Count the number of pawns for a given player"""
        return sum(row.count(player) for row in self.boardArray)

    def get_pawn_positions(self, player):
        """Get positions of all pawns for a given player"""
        positions = []
        for r in range(8):
            for c in range(8):
                if self.boardArray[r][c] == player:
                    positions.append((r, c))
        return positions

    def print_board(self):
        """
        Print the current board state for debugging
        """
        print("  a b c d e f g h")
        for i, row in enumerate(self.boardArray):
            print(f"{8-i} {' '.join(cell if cell != ' ' else '.' for cell in row)} {8-i}")
        print("  a b c d e f g h")