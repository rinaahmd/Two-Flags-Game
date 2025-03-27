import sys
import socket
import threading
import queue
import time
import pygame
import argparse
from game.board import ChessBoard
from client.UserInterface import UserInterface
from search.ai_agent import AIAgent  # Import the AI agent

class GameClient:
    def __init__(self, use_ai=False, ai_algorithm="minmax"):
        self.socket = socket.socket()
        self.time = 0
        self.color = None
        self.surface = None
        self.UI = None
        self.running = True
        self.is_my_turn = False
        self.message_queue = queue.Queue()
        self.game_over = False
        
        # AI setup
        self.use_ai = use_ai
        self.ai_agent = None
        self.ai_algorithm = ai_algorithm
        
    def connect_to_server(self, host="localhost", port=9999):
        try:
            self.socket.connect((host, port))
            print("Connected to the server!")
            return True
        except ConnectionRefusedError:
            print("Failed to connect to the server. Ensure the server is running.")
            return False

    def handle_network(self):
        while self.running:
            try:
                data = self.socket.recv(1024).decode().strip()
                if not data:
                    print("Server closed the connection.")
                    self.running = False
                    break

                self.message_queue.put(data)
            except Exception as e:
                print(f"Network error: {e}")
                self.running = False
                break


    def process_messages(self):
        try:
            while not self.message_queue.empty():
                data = self.message_queue.get_nowait()

                if data == "Connected to the server":
                    self.socket.send(str.encode("OK"))

                elif data == "White":
                    self.color = "W"
                    self.is_my_turn = True
                    self.UI.set_player_color(self.color)
                    self.UI.is_my_turn = True
                    print("You are playing as White")
                    
                    # Initialize AI agent if enabled
                    if self.use_ai:
                        self.ai_agent = AIAgent(algorithm=self.ai_algorithm)

                elif data == "Black":
                    self.color = "B"
                    self.is_my_turn = False
                    self.UI.set_player_color(self.color)
                    self.UI.is_my_turn = False
                    print("You are playing as Black")
                    
                    # Initialize AI agent if enabled
                    if self.use_ai:
                        self.ai_agent = AIAgent(algorithm=self.ai_algorithm)

                elif data.startswith("Time"):
                    minutes = int(data.split()[1])
                    self.time = minutes * 60
                    self.UI.start_timer(minutes)
                    self.socket.send(str.encode("OK"))
                    
                    # Update AI agent with time limit if enabled
                    if self.use_ai and self.ai_agent:
                        self.ai_agent = AIAgent(algorithm=self.ai_algorithm, time_limit_minutes=minutes)

                elif data.startswith("TIMER"):
                    # Format: "TIMER W:seconds B:seconds"
                    parts = data.split()
                    white_time = int(parts[1].split(':')[1])
                    black_time = int(parts[2].split(':')[1])
                    self.UI.update_times(white_time, black_time)

                elif data.startswith("Setup"):
                    self.handle_setup(data)
                    self.socket.send(str.encode("OK"))

                elif data == "Begin":
                    print("Game is beginning...")
                    if self.color == "W":
                        self.is_my_turn = True
                        self.UI.is_my_turn = True
                        self.UI.active_timer = 'W'
                        
                        # If AI is enabled and it's white's turn, make the first move
                        if self.use_ai:
                            self.make_ai_move()
                    self.UI.drawComponent()

                elif data == "Your turn":
                    print("It's your turn!")
                    self.is_my_turn = True
                    self.UI.is_my_turn = True
                    self.UI.active_timer = self.color
                    self.UI.display_turn_message("Your turn")
                    
                    # If AI is enabled, make a move
                    if self.use_ai:
                        self.make_ai_move()

                elif data.startswith("Waiting for"):
                    print(f"Waiting for {data}")
                    self.is_my_turn = False
                    self.UI.is_my_turn = False
                    opponent_color = 'B' if self.color == 'W' else 'W'
                    self.UI.active_timer = opponent_color
                    self.UI.display_turn_message(f"Waiting for opponent's move")

                elif data.startswith("Game Over"):
                    print(data)
                    if "wins" in data:
                        winner = 'W' if "W wins" in data else 'B'
                        self.handle_game_over(winner)
                    else:
                        self.UI.display_turn_message(data)
                        self.game_over = True

                elif data == "exit":
                    print("Game ended by server")
                    self.running = False

                elif len(data) == 4:  # Move format: e2e4
                    print(f"Opponent's move: {data}")
                    self.handle_opponent_move(data)

        except queue.Empty:
            pass




    # Modify the handle_game_over method in client.py

    def handle_game_over(self, winner):
        """Handle game over with proper win/loss messages and auto-close"""
        self.game_over = True
        
        # Set the game over state in the UI
        self.UI.set_game_over(winner)
        
        # Display winner explicitly
        self.UI.display_winner(winner)
        
        # Display appropriate message
        if winner == self.color:
            print("YOU WIN!")
            self.UI.display_turn_message("Game Over - You Win!")
        else:
            print("YOU LOSE!")
            self.UI.display_turn_message("Game Over - You Lose!")
        
        # Set the turn state to false
        self.is_my_turn = False
        self.UI.is_my_turn = False

        # Make sure the UI has time to draw the final state
        self.UI.drawComponent()
        pygame.display.update()
        
        # Give players time to see the final board state
        pygame.time.delay(5000)  # Wait 5 seconds before closing
        
        # Clean up
        try:
            self.socket.send(str.encode("exit"))
            self.socket.close()
        except:
            pass
        
        pygame.quit()
        sys.exit(0)  # Ensure clean exit


    def make_ai_move(self):
        """Have the AI agent make a move"""
        if not self.ai_agent or not self.is_my_turn or self.game_over:
            return
            
        # Small delay to make the AI's move visible to the user
        time.sleep(0.5)
        
        # Get best move from AI
        move_str = self.ai_agent.get_move(self.UI.chessboard, self.color)
        print(f"AI move: {move_str}")
        
        # Convert algebraic notation to board coordinates
        from_col = ord(move_str[0]) - ord('a')
        from_row = 8 - int(move_str[1])
        to_col = ord(move_str[2]) - ord('a')
        to_row = 8 - int(move_str[3])
        
        # Execute the move locally
        move_coords = [from_row, from_col, to_row, to_col]
        self.UI.chessboard.computeMove(move_coords, self.color)
        
        # Check for win condition
        if self.UI.chessboard.check_win(self.color):
            print(f"AI ({self.color}) has won the game!")
            self.socket.send(f"WIN:{self.color}".encode())
            self.handle_game_over(self.color)
            return
        
        # Update UI
        self.UI.drawComponent()
        
        # Send move to server
        self.socket.send(str.encode(move_str))
        
        # Update turn state
        self.is_my_turn = False
        self.UI.is_my_turn = False
        opponent_color = 'B' if self.color == 'W' else 'W'
        self.UI.active_timer = opponent_color
        self.UI.display_turn_message("Opponent's turn")

    def handle_setup(self, data):
        parts = data.split()[1:]  # Skip "Setup" command
        self.UI.chessboard.clear_board()
        
        for part in parts:
            color = part[0]
            col = ord(part[1].lower()) - ord('a')
            row = 8 - int(part[2])
            self.UI.chessboard.boardArray[row][col] = color
        
        self.UI.drawComponent()

    def handle_opponent_move(self, move):
        from_col = ord(move[0]) - ord('a')
        from_row = 8 - int(move[1])
        to_col = ord(move[2]) - ord('a')
        to_row = 8 - int(move[3])
        
        move_coords = [from_row, from_col, to_row, to_col]
        opponent_color = 'B' if self.color == 'W' else 'W'
        self.UI.chessboard.computeMove(move_coords, opponent_color)
        
        # Check if opponent has won
        if self.UI.chessboard.check_win(opponent_color):
            print(f"Opponent ({opponent_color}) has won the game!")
            self.socket.send(f"WIN:{opponent_color}".encode())
            self.handle_game_over(opponent_color)
            return
            
        self.UI.drawComponent()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.socket.send(str.encode("exit"))
                return

            # If AI is enabled or game is over, ignore mouse clicks for moves
            if self.use_ai or self.game_over:
                continue
                
            if event.type == pygame.MOUSEBUTTONDOWN and self.is_my_turn:
                pos = pygame.mouse.get_pos()
                move = self.UI.handle_click(pos)
                if move:
                    # Create algebraic notation move string
                    move_str = (
                        chr(ord('a') + move[1]) +
                        str(8 - move[0]) +
                        chr(ord('a') + move[3]) +
                        str(8 - move[2])
                    )
                    
                    # Check for win condition
                    if self.UI.chessboard.check_win(self.color):
                        print(f"You ({self.color}) won the game!")
                        self.socket.send(f"WIN:{self.color}".encode())
                        self.handle_game_over(self.color)
                        return
                    
                    # Send move to server
                    self.socket.send(str.encode(move_str))
                    
                    # Update turn state
                    self.is_my_turn = False
                    self.UI.is_my_turn = False
                    opponent_color = 'B' if self.color == 'W' else 'W'
                    self.UI.active_timer = opponent_color
                    self.UI.display_turn_message("Opponent's turn")

    def run(self):
        if not self.connect_to_server():
            return

        try:
            pygame.init()
            self.surface = pygame.display.set_mode([860, 770])
            pygame.display.set_caption('Two Flags Game')
            
            self.UI = UserInterface(self.surface, ChessBoard())
            
            network_thread = threading.Thread(target=self.handle_network)
            network_thread.daemon = True
            network_thread.start()

            clock = pygame.time.Clock()
            while self.running:
                self.handle_events()
                self.process_messages()
                self.UI.drawComponent()
                clock.tick(60)  # 60 FPS

        except Exception as e:
            print(f"Error in game: {e}")
        finally:
            print("Cleaning up...")
            if self.socket:
                try:
                    self.socket.send(str.encode("exit"))
                    self.socket.close()
                except:
                    pass
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description='Two Flags Game Client')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=9999, help='Server port')
    parser.add_argument('--ai', action='store_true', help='Enable AI player')
    parser.add_argument('--algorithm', default='minmax', choices=['minmax'], 
                        help='AI algorithm to use (only minmax is supported)')
    
    args = parser.parse_args()
    
    client = GameClient(use_ai=args.ai, ai_algorithm=args.algorithm)
    client.run()


if __name__ == "__main__":
    main()