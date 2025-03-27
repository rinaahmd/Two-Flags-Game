import sys
import time
import argparse
import pygame
import threading
from game.board import ChessBoard
from game.timer import GameTimer
from client.UserInterface import UserInterface
from search.ai_agent import AIAgent


def initialize_game(args):
    """Initialize the game board, UI, and timer based on command-line arguments."""
    try:
        # Initialize pygame
        pygame.init()

        # Create game board
        board = ChessBoard()

        # Create game display
        surface = pygame.display.set_mode([860, 770])
        pygame.display.set_caption('Two Flags Game - Local Mode')

        # Create UI
        ui = UserInterface(surface, board)

        # Set up the board
        board.clear_board()
        parts = args.setup.split()
        for part in parts:
            if len(part) == 3:
                color = part[0]
                col = ord(part[1].lower()) - ord('a')
                row = 8 - int(part[2])
                if 0 <= row < 8 and 0 <= col < 8:
                    board.boardArray[row][col] = color

        # Initialize timer
        timer = GameTimer()
        time_minutes = args.time

        # Determine human player color (if any)
        human_player_color = None
        if args.white == "human":
            human_player_color = 'W'
        elif args.black == "human":
            human_player_color = 'B'

        # Set player color in UI
        if human_player_color:
            ui.set_player_color(human_player_color)
            # Set window title to show player color clearly
            pygame.display.set_caption(f'Two Flags Game - You are {("White" if human_player_color == "W" else "Black")}')
        else:
            # AI vs AI mode
            pygame.display.set_caption('Two Flags Game - AI vs AI')

        # Set up UI with timer
        ui.start_timer(time_minutes)
        timer.start(time_minutes * 60, ui.update_times)  # Start the timer with callback

        # Set initial UI state
        ui.is_my_turn = human_player_color == 'W'  # Human is active if playing white
        ui.active_timer = 'W'  # White goes first
        timer.switch_timer('W')  # Start white's timer

        # Display initial turn message
        if args.white == "human":
            ui.display_turn_message("YOUR TURN (White)")
        else:
            ui.display_turn_message("AI is thinking (White)...")

        # Initialize AI agents
        white_ai = None
        black_ai = None

        if args.white == "ai":
            white_ai = AIAgent(algorithm=args.white_algorithm, time_limit_minutes=args.time)

        if args.black == "ai":
            black_ai = AIAgent(algorithm=args.black_algorithm, time_limit_minutes=args.time)

        return board, surface, ui, timer, white_ai, black_ai, human_player_color

    except Exception as e:
        print(f"Error in initialize_game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


def main():
    """Main function with human vs AI victory improvements."""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description='Two Flags Game - Local Mode')
        parser.add_argument('--white', default='human', choices=['human', 'ai'],
                           help='White player type (human or ai)')
        parser.add_argument('--black', default='ai', choices=['human', 'ai'],
                           help='Black player type (human or ai)')
        parser.add_argument('--white-algorithm', default='minmax', choices=['minmax'],
                           help='Algorithm for white AI (minmax)')
        parser.add_argument('--black-algorithm', default='minmax', choices=['minmax'],
                           help='Algorithm for black AI (minmax)')
        parser.add_argument('--time', type=int, default=30, help='Time limit in minutes')
        parser.add_argument('--setup', help='Initial board setup string')
        parser.add_argument('--debug', action='store_true', help='Enable debug output')

        args = parser.parse_args()
        debug = args.debug or True

        if debug:
            print("Command-line arguments:", args)

        # Default setup if none provided
        if not args.setup:
            args.setup = "Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7"

        # Initialize game components
        board, surface, ui, timer, white_ai, black_ai, human_player_color = initialize_game(args)

        # Game state
        current_player = 'W'  # White starts first in chess rules
        running = True
        game_over = False
        winner = None  # Variable to store the winner

        # Function to let AI make a move in a separate thread
        def ai_move_thread():
            nonlocal current_player, game_over, winner

            ai = white_ai if current_player == 'W' else black_ai
            if not ai:
                return

            print(f"AI ({current_player}) is thinking...")

            try:
                # Get AI move
                move_str = ai.get_move(board, current_player)

                # Parse the move
                from_col = ord(move_str[0]) - ord('a')
                from_row = 8 - int(move_str[1])
                to_col = ord(move_str[2]) - ord('a')
                to_row = 8 - int(move_str[3])

                move_coords = [from_row, from_col, to_row, to_col]
                print(f"AI chose move: {move_str}")

                # Apply the move
                board.computeMove(move_coords, current_player)

                # Update UI to ensure the move is visible
                ui.drawComponent()
                pygame.display.update()

                # Check win condition
                if board.check_win(current_player):
                    print(f"Game over! {current_player} wins by reaching the opponent's side!")
                    
                    # Add a small delay to make the final move visible before showing game over
                    pygame.time.delay(500)  # 500ms delay
                    
                    # Critical: Set game state first, then update UI
                    game_over = True
                    winner = current_player
                    
                    # Update game state in UI
                    ui.set_game_over(winner)
                    
                    # Explicitly draw the winner message
                    ui.display_winner(winner)
                    
                    # Stop the timer
                    timer.stop()
                    
                    # Force another UI update to ensure the winner is displayed
                    ui.drawComponent()
                    pygame.display.update()
                    
                    # Set timer for delayed exit AFTER updating the UI
                    pygame.time.set_timer(pygame.USEREVENT, 5000)  # 5 second delay before auto-close
                else:
                    # Switch turns
                    current_player = 'B' if current_player == 'W' else 'W'
                    timer.switch_timer(current_player)  # Switch timer when turns change
                    ui.active_timer = current_player
                    ui.is_my_turn = (current_player == human_player_color)

                    # Update turn message with clearer indication if it's the human's turn
                    if human_player_color and current_player == human_player_color:
                        ui.display_turn_message(f"YOUR TURN ({'White' if current_player == 'W' else 'Black'})")
                    else:
                        ui.display_turn_message(f"AI is thinking ({'White' if current_player == 'W' else 'Black'})...")

            except Exception as e:
                print(f"Error during AI move: {e}")
                import traceback
                traceback.print_exc()

        # AI moves need to happen in a separate thread so the UI remains responsive
        ai_thread = None

        # Main game loop
        clock = pygame.time.Clock()
        print("Starting game loop...")

        last_timer_update = time.time()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    timer.stop()  # Stop the timer when quitting
                    break

                # Handle timer event for delayed exit after game over
                if event.type == pygame.USEREVENT and game_over:
                    print("Game over timer triggered - exiting game")
                    running = False
                    break

                # Handle human moves only if game is not over
                if not game_over:
                    is_human_turn = (current_player == human_player_color)

                    if is_human_turn and event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        move = ui.handle_click(pos)

                        if move:
                            from_row, from_col, to_row, to_col = move
                            move_str = f"{chr(from_col + ord('a'))}{8 - from_row}{chr(to_col + ord('a'))}{8 - to_row}"
                            print(f"Human made move: {move_str}")

                            # Apply the move
                            board.computeMove(move, current_player)

                            # Update UI immediately to show the move
                            ui.drawComponent()
                            pygame.display.update()

                            # Check win condition
                            if board.check_win(current_player):
                                # Add a small delay to make sure the final move is visible
                                pygame.time.delay(500)

                                game_over = True
                                winner = current_player
                                ui.set_game_over(winner)
                                ui.display_winner(winner)
                                timer.stop()  # Stop the timer on game over
                                print(f"Game over! {winner} wins!")

                                # Force UI update to show the winner
                                ui.drawComponent()
                                pygame.display.update()

                                # Set timer for delayed exit
                                pygame.time.set_timer(pygame.USEREVENT, 5000)  # Wait for 5 seconds
                            else:
                                # Switch turns
                                current_player = 'B' if current_player == 'W' else 'W'
                                timer.switch_timer(current_player)  # Switch timer when turns change
                                ui.active_timer = current_player
                                ui.is_my_turn = (current_player == human_player_color)

                                # Update turn message
                                ui.display_turn_message(f"AI is thinking ({'White' if current_player == 'W' else 'Black'})...")

            # Handle timer updates only if game is not over
            if not game_over:
                current_time = time.time()
                if current_time - last_timer_update >= 1.0:
                    # Update UI timers
                    white_time = timer.get_time('W')
                    black_time = timer.get_time('B')
                    ui.update_times(white_time, black_time)

                    # Check for time-out
                    if white_time <= 0 or black_time <= 0:
                        if white_time <= 0:
                            winner = 'B'
                            print("White ran out of time! Black wins!")
                        else:
                            winner = 'W'
                            print("Black ran out of time! White wins!")

                        game_over = True
                        ui.set_game_over(winner)
                        ui.display_winner(winner)
                        timer.stop()

                        # Force UI update to show the winner
                        ui.drawComponent()
                        pygame.display.update()

                        # Set timer for delayed exit
                        pygame.time.set_timer(pygame.USEREVENT, 5000)

                    last_timer_update = current_time

            # Handle AI moves only if game is not over
            if not game_over:
                is_ai_turn = current_player != human_player_color

                if is_ai_turn and (ai_thread is None or not ai_thread.is_alive()):
                    ai_thread = threading.Thread(target=ai_move_thread)
                    ai_thread.daemon = True
                    ai_thread.start()

            # Update the UI (always, even if game is over)
            ui.drawComponent()
            pygame.display.update()  # Explicitly update the display
            clock.tick(60)  # 60 FPS
            
            # For debugging, occasionally print game state when game is over
            if game_over and int(time.time()) % 3 == 0:  # Every 3 seconds
                print(f"Game over state active. Winner: {winner}")

        # Clean up
        timer.stop()
        pygame.quit()
        print("Game ended!")

    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()

        # Clean up pygame
        try:
            pygame.quit()
        except:
            pass


if __name__ == "__main__":
    print("Starting script...")
    main()