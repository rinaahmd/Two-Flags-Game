class Rules:
    @staticmethod
    def get_valid_moves(board, row, col):
        """
        Get all valid moves for a pawn, including comprehensive captures and En Passant
        
        :param board: The game board
        :param row: Current row of the pawn
        :param col: Current column of the pawn
        :return: List of valid move tuples (to_row, to_col)
        """
        # Validate input and piece
        if (row < 0 or row >= 8 or col < 0 or col >= 8):
            return []

        piece = board.boardArray[row][col]
        if piece not in ['W', 'B']:
            return []

        moves = []
        
        # Determine movement parameters based on color
        if piece == 'W':
            direction = -1  # White moves up (negative row)
            start_rank = 6
            en_passant_rank = 3
            opponent = 'B'
        else:  # Black
            direction = 1   # Black moves down (positive row)
            start_rank = 1
            en_passant_rank = 4
            opponent = 'W'
        
        # Forward moves
        new_row = row + direction
        
        # Forward one square
        if 0 <= new_row < 8 and board.boardArray[new_row][col] == ' ':
            moves.append((new_row, col))
            
            # Initial two-square move
            if row == start_rank:
                two_square_row = row + 2 * direction
                if board.boardArray[two_square_row][col] == ' ' and \
                   board.boardArray[row + direction][col] == ' ':
                    moves.append((two_square_row, col))
        
        # Diagonal captures (including En Passant targets)
        diagonal_captures = [
            (row + direction, col - 1),  # Left diagonal
            (row + direction, col + 1)   # Right diagonal
        ]
        
        for new_row, new_col in diagonal_captures:
            # Check bounds
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Regular capture of opponent's pawn
                target = board.boardArray[new_row][new_col]
                
                # Capture conditions
                capture_conditions = (
                    # Capture an opponent's pawn
                    (target != ' ' and target != piece) or
                    # En Passant capture
                    (board.en_passant_target and 
                     new_col == board.en_passant_target[1] and 
                     row == en_passant_rank)
                )
                
                if capture_conditions:
                    moves.append((new_row, new_col))
        
        return moves

    @staticmethod
    def is_valid_move(board, from_pos, to_pos, player):
        """
        Validate a specific move for a pawn
        
        :param board: The game board
        :param from_pos: Tuple (from_row, from_col)
        :param to_pos: Tuple (to_row, to_col)
        :param player: Player color ('W' or 'B')
        :return: Boolean indicating if the move is valid
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Validate the piece belongs to the player
        if board.boardArray[from_row][from_col] != player:
            return False

        # Get all valid moves for this pawn
        valid_moves = Rules.get_valid_moves(board, from_row, from_col)
        
        # Check if the proposed move is in the list of valid moves
        return (to_row, to_col) in valid_moves

    @staticmethod
    def is_win(board, player):
        """
        Check if a player has won the game
        
        :param board: The game board
        :param player: Player color ('W' or 'B')
        :return: Boolean indicating if the player has won
        """
        opponent = 'B' if player == 'W' else 'W'
        
        # Win condition 1: Reach the opposite end
        target_row = 0 if player == 'W' else 7
        for col in range(8):
            if board.boardArray[target_row][col] == player:
                return True

        # Win condition 2: Capture all opponent's pawns
        opponent_pawns = sum(row.count(opponent) for row in board.boardArray)
        if opponent_pawns == 0:
            return True

        # Win condition 3: Opponent has no legal moves
        has_moves = False
        for row in range(8):
            for col in range(8):
                if board.boardArray[row][col] == opponent:
                    # Check all possible moves
                    moves = Rules.get_valid_moves(board, row, col)
                    if moves:
                        has_moves = True
                        break
                if has_moves:
                    break
        
        return not has_moves

    @staticmethod
    def describe_move(board, from_pos, to_pos):
        """
        Provide a description of a move
        
        :param board: The game board
        :param from_pos: Tuple (from_row, from_col)
        :param to_pos: Tuple (to_row, to_col)
        :return: String describing the move
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = board.boardArray[from_row][from_col]
        
        # Basic move description
        move_desc = f"{piece} pawn moves from {chr(from_col + 97)}{8-from_row} to {chr(to_col + 97)}{8-to_row}"
        
        # Check for captures
        if board.boardArray[to_row][to_col] != ' ':
            move_desc += f" (captures {board.boardArray[to_row][to_col]} pawn)"
        
        # Check for en passant
        if board.en_passant_target and to_col == board.en_passant_target[1]:
            move_desc += " (En Passant capture)"
        
        return move_desc