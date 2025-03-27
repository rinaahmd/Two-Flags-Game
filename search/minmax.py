import time
import copy
from typing import Tuple, List, Optional
from search.evaluation import Evaluation

class Minmax:
    def __init__(self, total_time_minutes=30):
        """
        Minimax with time-based cutoff, deeper search, and safer fallback checks.
        Also includes side-to-move in transposition table hashing to prevent stale entries.
        """
        self.total_time = total_time_minutes * 60
        self.remaining_time = self.total_time
        self.nodes_visited = 0

        # Large forced-win values
        self.MAX_SCORE = 1_000_000
        self.MIN_SCORE = -1_000_000

        self.start_time = None

        # If you keep a TT between moves, be cautious about storing "side to move."
        # The best fix is to store (hash, sideToMove) => (depth, eval).
        self.transposition_table = {}

        self.evaluator = Evaluation()

        self.max_depth_reached = 0
        self.current_depth = 0

        self.DEFAULT_MAX_DEPTH = 20  # Deep default

    def get_best_move(self, board, player: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Iterative deepening, with time-based cutoff, plus final validity check.
        """
        self.start_time = time.time()
        self.nodes_visited = 0

        estimated_moves_left = self._estimate_remaining_moves(board)
        time_for_move = max(1.0, self.remaining_time / (estimated_moves_left + 2))
        allowed_time = time_for_move * 0.85

        best_move = None
        best_value = self.MIN_SCORE

        all_moves = self._get_all_moves(board, player)
        if not all_moves:
            return None
        if len(all_moves) == 1:
            return all_moves[0]

        sorted_moves = self._pre_sort_moves(board, player, all_moves)

        for current_depth in range(1, self.DEFAULT_MAX_DEPTH + 1):
            if (time.time() - self.start_time) >= allowed_time:
                break

            self.current_depth = current_depth
            current_best_move = None
            current_best_value = self.MIN_SCORE
            alpha = self.MIN_SCORE
            beta = self.MAX_SCORE

            # Reinsert best_move from previous iteration at front
            if best_move and best_move in sorted_moves:
                sorted_moves.remove(best_move)
                sorted_moves.insert(0, best_move)

            for move in sorted_moves:
                if (time.time() - self.start_time) >= allowed_time:
                    break

                # Copy board, make move
                board_copy = self._copy_board(board)
                self._make_move(board_copy, move, player)

                # Next ply is minimizing
                value = self._minmax(
                    board_copy,
                    depth=current_depth - 1,
                    maximizing_player=False,
                    alpha=alpha,
                    beta=beta,
                    root_player=player
                )

                if value > current_best_value:
                    current_best_value = value
                    current_best_move = move

                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            # Check validity of the new best move
            if current_best_move and self._is_valid_move(board, current_best_move, player):
                best_move = current_best_move
                best_value = current_best_value
                # Possibly break if near forced win
                if best_value >= self.MAX_SCORE * 0.9:
                    break

            self.max_depth_reached = current_depth

            # reorder for next iteration
            if current_depth < self.DEFAULT_MAX_DEPTH:
                sorted_moves = self._get_sorted_moves(board, player)

        elapsed = time.time() - self.start_time
        self.remaining_time -= elapsed

        # -------------
        # Final check
        # -------------
        if best_move and not self._is_valid_move(board, best_move, player):
            # If final best move is invalid, remove from TT and fallback
            board_hash = self._get_board_hash(board, player)
            if board_hash in self.transposition_table:
                del self.transposition_table[board_hash]

            print("[Minmax] WARNING: final chosen move is invalid. Falling back.")
            # fallback to any valid move
            for m in all_moves:
                if self._is_valid_move(board, m, player):
                    best_move = m
                    break
            else:
                # If truly no valid moves, return None
                best_move = None


        return best_move

    def _minmax(self, board, depth: int, maximizing_player: bool, alpha: float, beta: float, root_player: str) -> float:
        self.nodes_visited += 1
        board_hash = self._get_board_hash(board, root_player if maximizing_player else ('B' if root_player=='W' else 'W'))
        # Check transposition table
        if board_hash in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return stored_value

        # depth or terminal check
        if self._is_terminal(board):
            val = self._evaluate_terminal(board, root_player)
            return val
        if depth == 0:
            return self._evaluate(board, root_player)

        # Determine the current side to move
        current_player = root_player if maximizing_player else ('B' if root_player=='W' else 'W')
        moves = self._get_all_moves(board, current_player)
        if not moves:
            return self.MIN_SCORE if maximizing_player else self.MAX_SCORE

        moves = self._pre_sort_moves(board, current_player, moves)

        if maximizing_player:
            value = self.MIN_SCORE
            for move in moves:
                board_copy = self._copy_board(board)
                self._make_move(board_copy, move, current_player)
                val = self._minmax(board_copy, depth-1, False, alpha, beta, root_player)
                value = max(value, val)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            self.transposition_table[board_hash] = (depth, value)
            return value
        else:
            value = self.MAX_SCORE
            for move in moves:
                board_copy = self._copy_board(board)
                self._make_move(board_copy, move, current_player)
                val = self._minmax(board_copy, depth-1, True, alpha, beta, root_player)
                value = min(value, val)
                beta = min(beta, value)
                if alpha >= beta:
                    break

            self.transposition_table[board_hash] = (depth, value)
            return value

    # -------------- Evaluation helpers --------------

    def _evaluate(self, board, player: str) -> float:
        return self.evaluator.evaluate(board, player)

    def _evaluate_terminal(self, board, player: str) -> float:
        if board.check_win(player):
            return self.MAX_SCORE
        elif board.check_win('B' if player=='W' else 'W'):
            return self.MIN_SCORE
        return 0

    def _is_terminal(self, board) -> bool:
        return board.check_win('W') or board.check_win('B')

    # -------------- Move generation / ordering --------------

    def _pre_sort_moves(self, board, player: str, moves: List[Tuple[int,int,int,int]]) -> List[Tuple[int,int,int,int]]:
        scored = []
        for (fr,fc,tr,tc) in moves:
            sc = 0
            # Bonus for captures
            if board.boardArray[tr][tc] != ' ':
                sc += 50
            # Encourage promotion
            if player=='W':
                sc += (7 - tr)
                if tr==0: sc += 100
            else:
                sc += tr
                if tr==7: sc += 100

            scored.append(((fr,fc,tr,tc), sc))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [mv for mv,_ in scored]

    def _get_sorted_moves(self, board, player: str) -> List[Tuple[int,int,int,int]]:
        mv_list = self._get_all_moves(board, player)
        if not mv_list:
            return []
        out = []
        for m in mv_list:
            (fr,fc,tr,tc) = m
            copy_b = self._copy_board(board)
            self._make_move(copy_b, m, player)
            sc = self._evaluate(copy_b, player)
            if copy_b.check_win(player):
                sc = self.MAX_SCORE
            out.append((m, sc))
        out.sort(key=lambda x: x[1], reverse=True)
        return [m for m,_ in out]

    # -------------- Board / Move helpers --------------

    def _get_board_hash(self, board, side_to_move:str) -> str:
        """
        Combine board layout + side to move for TT key.
        """
        layout_str = ''.join(''.join(cell if cell!=' ' else '-' for cell in row) for row in board.boardArray)
        return side_to_move + ":" + layout_str

    def _estimate_remaining_moves(self, board) -> int:
        # same logic as before
        white_pawns = sum(row.count('W') for row in board.boardArray)
        black_pawns = sum(row.count('B') for row in board.boardArray)
        total_pawns = white_pawns + black_pawns
        return max(6, total_pawns * 2)

    def _copy_board(self, board):
        return board.copy()

    def _make_move(self, board, move: tuple, player: str):
        board.computeMove(move, player)

    def _is_valid_move(self, board, move: tuple, player: str) -> bool:
        fr, fc, tr, tc = move
        if board.boardArray[fr][fc] != player:
            return False
        valid = board.get_valid_moves(fr, fc)
        return (tr, tc) in valid

    def _get_all_moves(self, board, player: str) -> List[Tuple[int,int,int,int]]:
        out = []
        for r in range(8):
            for c in range(8):
                if board.boardArray[r][c] == player:
                    for (tr,tc) in board.get_valid_moves(r, c):
                        out.append((r,c,tr,tc))
        return out
