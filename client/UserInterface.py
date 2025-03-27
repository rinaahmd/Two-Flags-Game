import pygame
import math
import time

class UserInterface:
    def __init__(self, surface, chessboard):
        self.surface = surface
        self.chessboard = chessboard
        self.playerColor = None
        self.selected_piece = None
        self.valid_moves = []
        self.is_my_turn = False
        self.turn_message = "Waiting for game to start..."
        self.last_update = pygame.time.get_ticks()
        self.game_over = False
        self.winner = None
        self.game_over_time = None  # Will be set when game ends
        self.game_over_duration = 40  # Seconds to show game over screen
        self.winning_square = None  # Store the winning pawn position
        
        # Board layout constants - Adjusted for compact width
        self.SQUARE_SIZE = 75
        self.BOARD_SIZE = self.SQUARE_SIZE * 8
        self.BOARD_MARGIN = 30
        
        # Calculate window size based on board size and margins
        self.WINDOW_WIDTH = self.BOARD_SIZE + (self.BOARD_MARGIN * 2) + 220  # Extra space for timer panel
        # Calculate minimum window height needed
        self.WINDOW_HEIGHT = self.BOARD_SIZE + self.BOARD_MARGIN * 2 + 150  # Space for top message and bottom indicator
        
        # Calculate board position
        self.BOARD_START_X = self.BOARD_MARGIN + 20
        self.BOARD_START_Y = self.BOARD_MARGIN + 60  # Increased top margin
        
        # Colors
        self.BACKGROUND_COLOR = (255, 255, 255)
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.SELECTED_COLOR = (255, 255, 0, 128)
        self.VALID_MOVE_COLOR = (0, 255, 0, 128)
        self.WIN_COLOR = (0, 180, 0)
        self.LOSE_COLOR = (180, 0, 0)
        self.WINNER_HIGHLIGHT = (255, 215, 0)  # Gold color for winner highlight
        
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_victory = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Load images
        try:
            self.white_pawn = pygame.image.load("assets/white_pawn.png")
            self.black_pawn = pygame.image.load("assets/black_pawn.png")
            self.white_pawn = pygame.transform.scale(self.white_pawn, (50, 50))
            self.black_pawn = pygame.transform.scale(self.black_pawn, (50, 50))
        except:
            print("Could not load pawn images, using default shapes")
            self.white_pawn = self._create_default_pawn((255, 255, 255))
            self.black_pawn = self._create_default_pawn((0, 0, 0))

        # Timer initialization
        self.white_time = 0
        self.black_time = 0
        self.timer_running = False
        self.active_timer = None

    def _create_default_pawn(self, color):
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (25, 25), 20)
        return surface

    def set_player_color(self, color):
        self.playerColor = color
        color_name = 'White' if color == 'W' else 'Black'
        pygame.display.set_caption(f'Two Flags Game - {color_name} Player')

    def display_turn_message(self, message):
        self.turn_message = message
        
    def display_winner(self, winner):
        """
        Set up the game state to display the winner and prepare for delayed exit.
        This method focuses on setting state variables, not immediate rendering.
        
        :param winner: The winning player ('W' or 'B')
        """
        # Set the game state
        self.game_over = True
        self.winner = winner
        self.game_over_time = time.time()
        
        # Determine if player won or lost
        is_player_winner = (winner == self.playerColor)
        
        # Set appropriate message
        winner_name = 'White' if winner == 'W' else 'Black'
        if is_player_winner:
            self.turn_message = f"GAME OVER - YOU WIN! ({winner_name})"
        else:
            self.turn_message = f"GAME OVER - {winner_name} WINS!"
        
        # Try to determine the winning square for highlighting
        if not self.winning_square and self.chessboard.last_move:
            from_row, from_col, to_row, to_col = self.chessboard.last_move
            target_row = 0 if winner == 'W' else 7
            if to_row == target_row:
                self.winning_square = (to_row, to_col)
                
        # Update window caption
        pygame.display.set_caption(f'Two Flags Game - Game Over - {winner_name} Wins')
        
        # Log to console for debugging
        print(f"Display winner called: {winner_name} wins!")
        
        # Don't force drawing here - let the main game loop handle it
        # The state variables set above will be used in the next drawComponent() call

    def start_timer(self, minutes):
        self.white_time = minutes * 60
        self.black_time = minutes * 60
        self.timer_running = True
        self.active_timer = 'W'  # White starts first

    def update_times(self, white_time, black_time):
        self.white_time = white_time
        self.black_time = black_time
        if white_time <= 0 or black_time <= 0:
            self.timer_running = False

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def check_auto_close(self):
        """Check if the game over screen has been shown long enough and should auto-close"""
        if self.game_over and self.game_over_time is not None:
            elapsed = time.time() - self.game_over_time
            if elapsed >= self.game_over_duration:
                # Signal the main loop to quit
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return False

    def draw_timer_panel(self):
        panel_x = self.BOARD_START_X + self.BOARD_SIZE + 40
        panel_width = 200
        
        # Draw timer backgrounds
        white_y = self.BOARD_START_Y + self.BOARD_SIZE - 100
        black_y = self.BOARD_START_Y + 50
        
        # Black timer
        text_color = (0, 0, 0)
        bg_color = (220, 220, 220) if self.active_timer == 'B' else self.BACKGROUND_COLOR
        pygame.draw.rect(self.surface, bg_color, (panel_x, black_y, panel_width, 40))
        self.surface.blit(
            self.font_medium.render("Black:", True, text_color),
            (panel_x + 10, black_y + 5)
        )
        self.surface.blit(
            self.font_large.render(self.format_time(self.black_time), True, text_color),
            (panel_x + 80, black_y)
        )
        
        # White timer
        bg_color = (220, 220, 220) if self.active_timer == 'W' else self.BACKGROUND_COLOR
        pygame.draw.rect(self.surface, bg_color, (panel_x, white_y, panel_width, 40))
        self.surface.blit(
            self.font_medium.render("White:", True, text_color),
            (panel_x + 10, white_y + 5)
        )
        self.surface.blit(
            self.font_large.render(self.format_time(self.white_time), True, text_color),
            (panel_x + 80, white_y)
        )

    def draw_coordinates(self):
        # Draw file coordinates (a-h) with proper spacing
        for i in range(8):
            file_letter = chr(ord('a') + (i if self.playerColor == 'W' else 7 - i))
            x = self.BOARD_START_X + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            
            # Draw at top and bottom with minimal spacing
            text = self.font_small.render(file_letter, True, (0, 0, 0))
            
            # Top coordinates - closer to board
            bg_rect = text.get_rect(center=(x, self.BOARD_START_Y - 15))  # Reduced spacing
            bg_rect.inflate_ip(10, 6)
            pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, bg_rect)
            self.surface.blit(text, text.get_rect(center=(x, self.BOARD_START_Y - 15)))
            
            # Bottom coordinates - closer to board
            y_bottom = self.BOARD_START_Y + self.BOARD_SIZE + 15  # Reduced spacing
            bg_rect = text.get_rect(center=(x, y_bottom))
            bg_rect.inflate_ip(10, 6)
            pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, bg_rect)
            self.surface.blit(text, text.get_rect(center=(x, y_bottom)))
        
        # Draw rank coordinates (1-8)
        for i in range(8):
            rank_num = str(8 - (i if self.playerColor == 'W' else 7 - i))
            y = self.BOARD_START_Y + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            
            # Draw on both sides with minimal spacing
            for x in [self.BOARD_START_X - 15, self.BOARD_START_X + self.BOARD_SIZE + 10]:  # Reduced spacing
                text = self.font_small.render(rank_num, True, (0, 0, 0))
                bg_rect = text.get_rect(center=(x, y))
                bg_rect.inflate_ip(6, 10)
                pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, bg_rect)
                self.surface.blit(text, text.get_rect(center=(x, y)))

    def draw_turn_indicator(self):
        """Draw turn indicator strip at the bottom with compact spacing"""
        strip_height = 35  # Reduced height
        # Calculate position to ensure it stays within window bounds
        strip_y = min(self.WINDOW_HEIGHT - strip_height - 5, self.BOARD_START_Y + self.BOARD_SIZE + 35)  # Stay within window
        
        # Use the window width for the indicator
        pygame.draw.rect(self.surface, (240, 240, 240), 
                        (0, strip_y, self.WINDOW_WIDTH, strip_height))
        
        if self.is_my_turn and not self.game_over:
            # Create pulsing effect
            t = pygame.time.get_ticks()
            alpha = int(128 + 127 * abs(math.sin(t * 0.003)))
            
            # Draw pulsing overlay
            overlay = pygame.Surface((self.WINDOW_WIDTH, strip_height), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, alpha))
            self.surface.blit(overlay, (0, strip_y))
            
            # Draw text
            text = self.font_medium.render("YOUR TURN", True, (0, 100, 0))
        else:
            if self.game_over:
                if self.winner == self.playerColor:
                    text = self.font_medium.render("GAME OVER - YOU WIN!", True, self.WIN_COLOR)
                else:
                    text = self.font_medium.render("GAME OVER - YOU LOSE!", True, self.LOSE_COLOR)
            else:
                text = self.font_medium.render("Waiting...", True, (100, 100, 100))
            
        # Center the text in the strip
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, strip_y + strip_height // 2))
        self.surface.blit(text, text_rect)

    def draw_game_over_overlay(self):
        """Draw a game over overlay with victory/defeat message"""
        if not self.game_over or not self.winner:
            return

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.surface.blit(overlay, (0, 0))

        # Determine if player won or lost
        i_won = self.winner == self.playerColor

        # Create message
        if i_won:
            message = "YOU WIN!"
            color = self.WIN_COLOR
        else:
            message = "YOU LOSE!"
            color = self.LOSE_COLOR

        # Draw main message - Large and centered
        text = self.font_victory.render(message, True, color)
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.surface.blit(text, text_rect)

        # Add win reason below if available
        win_reason = self.get_win_reason()
        if win_reason:
            reason_text = self.font_medium.render(f"By {win_reason}", True, color)
            reason_rect = reason_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
            self.surface.blit(reason_text, reason_rect)

        # Add closing message
        close_text = self.font_medium.render("Game will close in a few seconds...", True, (255, 255, 255))
        close_rect = close_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 70))
        self.surface.blit(close_text, close_rect)

        # Update the display immediately
        pygame.display.update()

    def get_win_reason(self):
        """Determine the reason for the win and identify the winning square"""
        if not self.winner:
            return "Unknown"
        
        # Check different win conditions
        target_row = 0 if self.winner == 'W' else 7
        for col in range(8):
            if self.chessboard.boardArray[target_row][col] == self.winner:
                # Set the winning square for highlighting
                self.winning_square = (target_row, col)
                return "Reaching opponent's side"
        
        loser = 'B' if self.winner == 'W' else 'W'
        if self.chessboard.count_pawns(loser) == 0:
            return "Capturing all opponent's pieces"
            
        # Check if loser has any valid moves
        has_moves = False
        for pos in self.chessboard.get_pawn_positions(loser):
            if self.chessboard.get_valid_moves(*pos):
                has_moves = True
                break
                
        if not has_moves:
            return "Opponent has no legal moves"
            
        # If we can't determine, it might be a timeout
        if self.white_time <= 0 or self.black_time <= 0:
            return "Time out"
            
        return "Unknown win condition"

    def drawComponent(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update < 16:  # ~60 FPS
            return
        self.last_update = current_time
        
        if not pygame.get_init():
            return
            
        # Fill background
        self.surface.fill(self.BACKGROUND_COLOR)
        
        # Draw components
        self.draw_board()
        self.draw_coordinates()
        self.draw_timer_panel()
        self.draw_turn_indicator()
        
        # Draw turn message at top with more space
        message_text = self.font_medium.render(self.turn_message, True, (0, 0, 0))
        message_rect = message_text.get_rect(center=(self.WINDOW_WIDTH // 2, 40))  # Increased from 25
        self.surface.blit(message_text, message_rect)
        
        # Draw game over overlay if game is over
        if self.game_over and self.winner:
            self.draw_game_over_overlay()
            self.check_auto_close()
        
        pygame.display.update()

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                board_row = row if self.playerColor == 'W' else 7 - row
                board_col = col if self.playerColor == 'W' else 7 - col
                
                x = self.BOARD_START_X + col * self.SQUARE_SIZE
                y = self.BOARD_START_Y + row * self.SQUARE_SIZE
                
                # Draw square
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                pygame.draw.rect(self.surface, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Special highlight for the winning square
                if self.game_over and self.winning_square and (board_row, board_col) == self.winning_square:
                    # Draw a pulsing gold highlight under the winning piece
                    t = pygame.time.get_ticks()
                    alpha = int(128 + 127 * abs(math.sin(t * 0.005)))
                    highlight = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill((255, 215, 0, alpha))  # Gold with pulsing alpha
                    self.surface.blit(highlight, (x, y))
                    
                    # Draw a crown or star above the piece to indicate it's the winner
                    # Simple star shape as a polygon
                    star_size = 20
                    star_points = 5
                    center_x = x + self.SQUARE_SIZE // 2
                    center_y = y + 15  # Position above the piece
                    
                    points = []
                    for i in range(star_points * 2):
                        angle = (math.pi * 2 * i) / (star_points * 2)
                        radius = star_size if i % 2 == 0 else star_size // 2
                        points.append((
                            center_x + radius * math.sin(angle),
                            center_y + radius * math.cos(angle)
                        ))
                    
                    pygame.draw.polygon(self.surface, (255, 255, 0), points)  # Bright yellow star
                
                # Draw selection highlight
                elif self.selected_piece and (board_row, board_col) == self.selected_piece:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                    s.set_alpha(128)
                    s.fill((255, 255, 0))
                    self.surface.blit(s, (x, y))
                elif (board_row, board_col) in self.valid_moves:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                    s.set_alpha(128)
                    s.fill((0, 255, 0))
                    self.surface.blit(s, (x, y))
                
                # Draw pieces
                piece = self.chessboard.boardArray[board_row][board_col]
                if piece == 'W':
                    self.surface.blit(self.white_pawn, (x + 12, y + 12))
                elif piece == 'B':
                    self.surface.blit(self.black_pawn, (x + 12, y + 12))

    def handle_click(self, pos):
        if not self.is_my_turn or not self.playerColor or self.game_over:
            return None
            
        col = (pos[0] - self.BOARD_START_X) // self.SQUARE_SIZE
        row = (pos[1] - self.BOARD_START_Y) // self.SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return None
            
        if self.playerColor == 'B':
            row = 7 - row
            col = 7 - col
        
        current_piece = self.chessboard.boardArray[row][col]
        
        if not self.selected_piece:
            if current_piece == self.playerColor:
                self.selected_piece = (row, col)
                self.valid_moves = self.chessboard.get_valid_moves(row, col)
                self.drawComponent()
            return None
        else:
            if (row, col) in self.valid_moves:
                move = [self.selected_piece[0], self.selected_piece[1], row, col]
                self.chessboard.computeMove(move, self.playerColor)
                self.selected_piece = None
                self.valid_moves = []
                self.drawComponent()
                return move
            
            self.selected_piece = None
            self.valid_moves = []
            
            if current_piece == self.playerColor:
                self.selected_piece = (row, col)
                self.valid_moves = self.chessboard.get_valid_moves(row, col)
            
            self.drawComponent()
            return None
        
            
    def set_game_over(self, winner=None):
        """Set the game as over with the specified winner"""
        self.game_over = True
        self.winner = winner

        # Find and store the winning position (the pawn that reached the other side or other win condition)
        if winner:
            # Try to determine win reason and set winning_square (if applicable)
            win_reason = self.get_win_reason()
            print(f"Game over! {winner} wins by {win_reason}")

            # If winning square wasn't set by get_win_reason, try to infer it from the last move
            if not self.winning_square and self.chessboard.last_move:
                target_row = 0 if winner == 'W' else 7
                _, _, to_row, to_col = self.chessboard.last_move
                if to_row == target_row:
                    self.winning_square = (to_row, to_col)

            # Create appropriate message
            winner_name = "White" if winner == "W" else "Black"
            
            # Display appropriate message based on whether player won or lost
            if winner == self.playerColor:
                self.turn_message = "Game Over - You Win!"
                # Force an immediate draw of the victory screen
                self.draw_game_over_overlay()
            else:
                self.turn_message = "Game Over - You Lose!"

            # Update window title with game result
            pygame.display.set_caption(f'Two Flags Game - Game Over - {winner_name} Wins')
        else:
            self.turn_message = "Game Over!"

        # Record time when game ended
        self.game_over_time = time.time()

        # Ensure the UI updates to show the final move and winner
        self.drawComponent()
        pygame.display.update()