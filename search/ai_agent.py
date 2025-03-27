"""
Enhanced AI Agent module for the Two Flags game.
With an added double-check if we get None from Minimax.
"""

import time
import random

class AIAgent:
    def __init__(self, algorithm="minmax", time_limit_minutes=30):
        """
        Initialize a stronger AI agent for the Two Flags game.
        
        Args:
            algorithm (str): The search algorithm to use (only "minmax" is supported)
            time_limit_minutes (int): Time limit for the entire game in minutes
        """
        self.algorithm = "minmax"  # Always use minmax
        self.time_limit = time_limit_minutes * 60
        print(f"[AI Agent] Initialized with {self.algorithm} algorithm and a total time of {time_limit_minutes} minutes.")
        
        try:
            from search.minmax import Minmax
            self.search_engine = Minmax(total_time_minutes=time_limit_minutes)
        except ImportError:
            print("Error: Minmax algorithm not available.")
            raise

    def get_move(self, board, player_color):
        start_time = time.time()
        print(f"[AI Agent] Thinking... (Player = {player_color})")

        move = self.search_engine.get_best_move(board, player_color)

        if move is None:
            # The engine didn't find a best move, so let's see if there really are no moves
            all_moves = self.search_engine._get_all_moves(board, player_color)
            if not all_moves:
                # Indeed no moves => We are truly stuck
                print("[AI Agent] No moves exist. Using fallback.")
                return "a2a3" if player_color == 'W' else "a7a6"
            else:
                # We do have moves but Minimax returned None => likely a transient sync issue
                print("[AI Agent] Minimax returned None, but moves exist. Picking a fallback from the real moves.")
                fallback = random.choice(all_moves)
                return self._move_to_algebraic(fallback)
        
        # If we did get a valid move from Minimax, we’re fine:
        end_time = time.time()
        move_algebraic = self._move_to_algebraic(move)
        return move_algebraic



    def _move_to_algebraic(self, move):
        """Convert numeric move (from_row, from_col, to_row, to_col) to algebraic notation."""
        from_row, from_col, to_row, to_col = move
        from_algebraic = chr(from_col + ord('a')) + str(8 - from_row)
        to_algebraic = chr(to_col + ord('a')) + str(8 - to_row)
        return from_algebraic + to_algebraic

    def _get_random_move(self, board, player_color):
        """
        Example of a random-move generator (fallback).
        Typically not used unless no better move was found.
        """
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if board.boardArray[row][col] == player_color:
                    moves = board.get_valid_moves(row, col)
                    valid_moves.extend((row, col, to_row, to_col) for to_row, to_col in moves)
        
        if valid_moves:
            move = random.choice(valid_moves)
            return self._move_to_algebraic(move)
        
        # If no valid moves, return a default
        return "a2a3" if player_color == 'W' else "a7a6"
 