class Evaluation:
    def __init__(self):
        """
        Enhanced evaluation with higher weights to reward crucial factors more.
        """
        # Updated weights for stronger play
        self.MATERIAL_WEIGHT = 200       # Heavier emphasis on material
        self.ADVANCEMENT_WEIGHT = 30     # Slightly higher than before
        self.CENTER_CONTROL_WEIGHT = 20  # More importance on center control
        self.PAWN_STRUCTURE_WEIGHT = 25  # Increased for good structure
        self.MOBILITY_WEIGHT = 20        # Encouraging more active positions
        self.SAFETY_WEIGHT = 15          # Pawn safety matters more
        self.ATTACKING_WEIGHT = 15       # Encouraging threats
        self.BREAKTHROUGH_WEIGHT = 20    # Encourage unstoppable pawns
        self.WINNING_POSITION_SCORE = 60000  # Larger for guaranteed wins

    def evaluate(self, board, player: str) -> float:
        """
        Enhanced comprehensive static evaluation function.
        Returns a numeric score indicating how favorable the position is for 'player'.
        """
        opponent = 'B' if player == 'W' else 'W'
        
        # Immediate wins
        if board.check_win(player):
            return self.WINNING_POSITION_SCORE
        if board.check_win(opponent):
            return -self.WINNING_POSITION_SCORE

        # Compute sub-scores
        material_score = self._evaluate_material(board, player)
        advancement_score = self._evaluate_advancement(board, player)
        center_control_score = self._evaluate_center_control(board, player)
        pawn_structure_score = self._evaluate_pawn_structure(board, player)
        mobility_score = self._evaluate_mobility(board, player)
        safety_score = self._evaluate_safety(board, player)
        attacking_score = self._evaluate_attacking_potential(board, player)
        breakthrough_score = self._evaluate_breakthrough_potential(board, player)

        # Combine with updated weights
        total_score = (
            material_score * self.MATERIAL_WEIGHT +
            advancement_score * self.ADVANCEMENT_WEIGHT +
            center_control_score * self.CENTER_CONTROL_WEIGHT +
            pawn_structure_score * self.PAWN_STRUCTURE_WEIGHT +
            mobility_score * self.MOBILITY_WEIGHT +
            safety_score * self.SAFETY_WEIGHT +
            attacking_score * self.ATTACKING_WEIGHT +
            breakthrough_score * self.BREAKTHROUGH_WEIGHT
        )
        return total_score

    def _evaluate_material(self, board, player: str) -> float:
        """Material advantage. Weighted more strongly if fewer pawns remain."""
        opponent = 'B' if player == 'W' else 'W'
        player_pawns = sum(row.count(player) for row in board.boardArray)
        opp_pawns = sum(row.count(opponent) for row in board.boardArray)
        total_pawns = player_pawns + opp_pawns
        
        # Scale up advantage if in late game
        if total_pawns < 10:
            return (player_pawns - opp_pawns) * (16 - total_pawns) / 6.0
        else:
            return player_pawns - opp_pawns

    def _evaluate_advancement(self, board, player: str) -> float:
        """
        Pawn advancement. 
        White ranks: row 6->2 increasingly more valuable, row 1 or 0 extremely valuable
        Black ranks: symmetrical for downward movement.
        """
        score = 0
        opponent = 'B' if player == 'W' else 'W'
        
        # Row-based tables
        white_rank_values = [50, 25, 12, 8, 5, 3, 1, 0]
        black_rank_values = [0, 1, 3, 5, 8, 12, 25, 50]
        
        for row in range(8):
            for col in range(8):
                piece = board.boardArray[row][col]
                if piece == player:
                    if player == 'W':
                        score += white_rank_values[row]
                        # Extra bonus for passers
                        if row < 4 and self._is_passed_pawn(board, row, col, player):
                            score += (4 - row) * 6
                    else:
                        score += black_rank_values[row]
                        # Extra bonus for passers
                        if row > 3 and self._is_passed_pawn(board, row, col, player):
                            score += (row - 3) * 6
                elif piece == opponent:
                    # Subtract for opponent’s advancement
                    if piece == 'W':
                        val = white_rank_values[row]
                        if row < 4 and self._is_passed_pawn(board, row, col, opponent):
                            val += (4 - row) * 6
                        score -= val
                    else:
                        val = black_rank_values[row]
                        if row > 3 and self._is_passed_pawn(board, row, col, opponent):
                            val += (row - 3) * 6
                        score -= val
        return score

    def _is_passed_pawn(self, board, row: int, col: int, player: str) -> bool:
        """No enemy pawns directly ahead on same or adjacent files."""
        opponent = 'B' if player == 'W' else 'W'
        direction = -1 if player == 'W' else 1
        
        for c in range(max(0, col-1), min(8, col+2)):
            r = row + direction
            while 0 <= r < 8:
                if board.boardArray[r][c] == opponent:
                    return False
                r += direction
        return True

    def _evaluate_center_control(self, board, player: str) -> float:
        """Give moderate bonus for controlling center squares."""
        center_value = [
            [0, 1, 1, 2, 2, 1, 1, 0],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [1, 3, 4, 5, 5, 4, 3, 1],
            [2, 3, 5, 7, 7, 5, 3, 2],
            [2, 3, 5, 7, 7, 5, 3, 2],
            [1, 3, 4, 5, 5, 4, 3, 1],
            [1, 2, 3, 3, 3, 3, 2, 1],
            [0, 1, 1, 2, 2, 1, 1, 0]
        ]
        opponent = 'B' if player == 'W' else 'W'
        score = 0
        for r in range(8):
            for c in range(8):
                if board.boardArray[r][c] == player:
                    score += center_value[r][c]
                elif board.boardArray[r][c] == opponent:
                    score -= center_value[r][c]
        return score

    def _evaluate_pawn_structure(self, board, player: str) -> float:
        """Protected pawns, no isolation/doubling, etc."""
        score = 0
        opponent = 'B' if player == 'W' else 'W'
        
        for row in range(8):
            for col in range(8):
                piece = board.boardArray[row][col]
                if piece == player:
                    # Protected
                    if self._is_protected(board, row, col, player):
                        score += 1.5
                    # Isolated
                    if self._is_isolated(board, row, col, player):
                        score -= 1.2
                    # Doubled
                    if self._is_doubled(board, row, col, player):
                        score -= 1.2
                    # Control squares
                    score += self._pawn_controls_key_square(board, row, col, player)
                elif piece == opponent:
                    opp_val = 0
                    if self._is_protected(board, row, col, opponent):
                        opp_val += 1.5
                    if self._is_isolated(board, row, col, opponent):
                        opp_val -= 1.2
                    if self._is_doubled(board, row, col, opponent):
                        opp_val -= 1.2
                    opp_val += self._pawn_controls_key_square(board, row, col, opponent)
                    # Subtract opponent's structure
                    score -= opp_val
        return score

    def _pawn_controls_key_square(self, board, row, col, player) -> float:
        """Small bonus for controlling important squares diagonally."""
        bonus = 0.0
        direction = -1 if player == 'W' else 1
        for dc in (-1, 1):
            rr = row + direction
            cc = col + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                # More bonus for center squares
                if 2 <= rr <= 5 and 2 <= cc <= 5:
                    bonus += 0.5
                # Bonus for controlling promotion row
                if (player == 'W' and rr == 0) or (player == 'B' and rr == 7):
                    bonus += 1.0
        return bonus

    def _evaluate_mobility(self, board, player: str) -> float:
        """Ratio of available moves vs opponent's moves."""
        opponent = 'B' if player == 'W' else 'W'
        player_moves = self._count_legal_moves(board, player)
        opp_moves = self._count_legal_moves(board, opponent)
        
        if opp_moves == 0:
            # Opponent is stuck => big advantage
            return 10.0
        
        ratio = player_moves / max(1, opp_moves)
        return (ratio - 1.0) * 6.0

    def _evaluate_safety(self, board, player: str) -> float:
        """Check threatened pawns and clear paths."""
        score = 0.0
        opponent = 'B' if player == 'W' else 'W'
        
        for row in range(8):
            for col in range(8):
                piece = board.boardArray[row][col]
                if piece == player:
                    if self._is_threatened(board, row, col, player):
                        score -= 1.0
                    if self._has_clear_path(board, row, col, player):
                        score += 0.75
                elif piece == opponent:
                    if self._is_threatened(board, row, col, opponent):
                        score += 1.0
                    if self._has_clear_path(board, row, col, opponent):
                        score -= 0.75
        return score

    def _is_threatened(self, board, row, col, player: str) -> bool:
        """Is this pawn capturable by an opponent pawn next move?"""
        opponent = 'B' if player == 'W' else 'W'
        capture_row = row + (1 if opponent == 'W' else -1)
        if 0 <= capture_row < 8:
            for dcol in [-1, 1]:
                capture_col = col + dcol
                if 0 <= capture_col < 8:
                    if board.boardArray[capture_row][capture_col] == opponent:
                        return True
        return False

    def _has_clear_path(self, board, row, col, player: str) -> bool:
        """Check if the path forward is unobstructed for a few squares."""
        direction = -1 if player == 'W' else 1
        r = row + direction
        steps_checked = 0
        while 0 <= r < 8 and steps_checked < 4:  # Check a few squares ahead
            if board.boardArray[r][col] != ' ':
                return False
            r += direction
            steps_checked += 1
        return True

    def _evaluate_attacking_potential(self, board, player: str) -> float:
        """Pawn's ability to threaten or capture opponent pawns, especially near promotion."""
        score = 0.0
        opponent = 'B' if player == 'W' else 'W'
        
        for row in range(8):
            for col in range(8):
                if board.boardArray[row][col] == player:
                    # Check squares diagonally forward
                    for dcol in (-1, 1):
                        rr = row + (-1 if player == 'W' else 1)
                        cc = col + dcol
                        if 0 <= rr < 8 and 0 <= cc < 8:
                            if board.boardArray[rr][cc] == opponent:
                                score += 1.2
                            # Threat near promotion
                            if (player == 'W' and rr <= 2) or (player == 'B' and rr >= 5):
                                score += 0.5
        return score

    def _evaluate_breakthrough_potential(self, board, player: str) -> float:
        """Chance a pawn can push through to promotion if not blocked by the opponent."""
        score = 0.0
        opponent = 'B' if player == 'W' else 'W'
        
        for col in range(8):
            player_most_advanced = -1
            opp_most_advanced = -1
            for row in range(8):
                piece = board.boardArray[row][col]
                if piece == player:
                    if player == 'W':
                        if player_most_advanced == -1 or row < player_most_advanced:
                            player_most_advanced = row
                    else:
                        if row > player_most_advanced:
                            player_most_advanced = row
                elif piece == opponent:
                    if opponent == 'W':
                        if opp_most_advanced == -1 or row < opp_most_advanced:
                            opp_most_advanced = row
                    else:
                        if row > opp_most_advanced:
                            opp_most_advanced = row

            # If we have a pawn in this file, check if it's blocked
            if player_most_advanced != -1:
                if player == 'W':
                    if player_most_advanced <= 3:
                        # The lower the row, the closer to promotion
                        distance = player_most_advanced
                        if opp_most_advanced == -1 or opp_most_advanced > player_most_advanced:
                            # Not blocked
                            score += (5 - distance) * 2.0
                        else:
                            score += (5 - distance) * 0.7
                else:  # Black
                    if player_most_advanced >= 4:
                        distance = 7 - player_most_advanced
                        if opp_most_advanced == -1 or opp_most_advanced < player_most_advanced:
                            score += (5 - distance) * 2.0
                        else:
                            score += (5 - distance) * 0.7
        return score

    def _is_protected(self, board, row, col, player: str) -> bool:
        """Check if a pawn is protected by another friendly pawn diagonally behind it."""
        protect_row = row + (1 if player == 'B' else -1)
        for dcol in (-1, 1):
            pc = col + dcol
            if 0 <= protect_row < 8 and 0 <= pc < 8:
                if board.boardArray[protect_row][pc] == player:
                    return True
        return False

    def _is_isolated(self, board, row, col, player: str) -> bool:
        """No friendly pawns on adjacent files."""
        for file_ in (col - 1, col + 1):
            if 0 <= file_ < 8:
                for r in range(8):
                    if board.boardArray[r][file_] == player:
                        return False
        return True

    def _is_doubled(self, board, row, col, player: str) -> bool:
        """Another friendly pawn on the same file."""
        for r in range(8):
            if r != row and board.boardArray[r][col] == player:
                return True
        return False

    def _count_legal_moves(self, board, player: str) -> int:
        """Count all moves of a given color."""
        moves_count = 0
        for r in range(8):
            for c in range(8):
                if board.boardArray[r][c] == player:
                    moves_count += len(board.get_valid_moves(r, c))
        return moves_count
