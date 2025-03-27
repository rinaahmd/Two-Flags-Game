import socket
import threading
import sys
import time

class GameServer:
    def __init__(self, host='localhost', port=9999):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Add socket reuse option to prevent "address already in use" errors
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = []
        self.client_colors = {}
        self.running = True
        self.time_limit = 0
        self.current_turn = 'W'  # White starts
        self.white_time = 0
        self.black_time = 0
        self.timer_thread = None
        self.game_over = False

    def start(self):
        try:
            print("Starting Two Flags Game Server...")
            self.server_socket.bind((self.host, self.port))
            print(f"Server socket bound with IP {self.host} and port {self.port}")
            self.server_socket.listen(2)
            print("Server is listening for connections...")

            # Accept two clients
            for i in range(2):
                client_socket, address = self.server_socket.accept()
                print(f"Client {i+1} connected from {address}")
                self.clients.append(client_socket)

            # Assign colors and initialize game
            self.initialize_game()

        except Exception as e:
            print(f"Error starting server: {e}")
            self.cleanup()

    def update_timers(self):
        last_update = time.time()
        while self.running and not self.game_over:
            current_time = time.time()
            if current_time - last_update >= 1.0:  # Update every second
                if self.current_turn == 'W':
                    self.white_time -= 1
                else:
                    self.black_time -= 1
                
                # Send timer updates to both clients
                timer_msg = f"TIMER W:{self.white_time} B:{self.black_time}"
                for client in self.clients:
                    try:
                        client.send(timer_msg.encode())
                    except:
                        pass

                if self.white_time <= 0 or self.black_time <= 0:
                    winner = 'B' if self.white_time <= 0 else 'W'
                    self.end_game(f"Game Over - {winner} wins by time")
                    break

                last_update = current_time

    def initialize_game(self):
        try:
            print("Assigning colors...")
            self.client_colors[self.clients[0]] = 'W'
            self.client_colors[self.clients[1]] = 'B'

            self.clients[0].send("White".encode())
            self.clients[1].send("Black".encode())

            print("Setting time limit...")
            self.time_limit = int(input("Enter time limit (in minutes): "))
            self.white_time = self.time_limit * 60
            self.black_time = self.time_limit * 60

            for client in self.clients:
                time_msg = f"Time {self.time_limit}"
                client.send(time_msg.encode())
                response = client.recv(1024).decode()
                if response != "OK":
                    raise Exception("Client did not acknowledge time limit")

            print("Sending board setup...")
            setup = "Setup Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7"
            for client in self.clients:
                client.send(setup.encode())
                response = client.recv(1024).decode()
                if response != "OK":
                    raise Exception("Client did not acknowledge setup")

            print("Starting the game...")
            self.clients[0].send("Begin".encode())
            self.clients[1].send("Begin".encode())

            print("Game started!")

            # Start timer thread
            self.timer_thread = threading.Thread(target=self.update_timers)
            self.timer_thread.daemon = True
            self.timer_thread.start()

            # Create threads for each client
            for client in self.clients:
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.daemon = True
                thread.start()

            while self.running:
                time.sleep(1)

        except Exception as e:
            print(f"Error initializing game: {e}")
            self.cleanup()

    def handle_client(self, client):
        try:
            while self.running and not self.game_over:
                move = client.recv(1024).decode()
                if not move:
                    break

                if move == "exit":
                    print(f"Client {self.client_colors[client]} disconnected")
                    self.running = False
                    break
                
                if move.startswith("WIN"):
                    # Handle win notification from client
                    winner = move.split(":")[1]
                    loser = 'B' if winner == 'W' else 'W'
                    self.end_game(f"Game Over - {winner} wins!")
                    break

                if len(move) == 4:  # Move format: e2e4
                    player = self.client_colors[client]
                    print(f"Received move {move} from {player}")
                    
                    # Switch turns
                    self.current_turn = 'B' if self.current_turn == 'W' else 'W'
                    
                    # Send move to other client
                    other_client = [c for c in self.clients if c != client][0]
                    other_client.send(move.encode())
                    
                    # Send turn notifications
                    client.send(f"Waiting for {self.current_turn}'s turn".encode())
                    other_client.send("Your turn".encode())

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.handle_client_disconnect(client)
  
    def end_game(self, message):
        print(message)
        self.game_over = True
        for client in self.clients:
            try:
                client.send(message.encode())
            except:
                pass
        self.running = False

    def handle_client_disconnect(self, client):
        if client in self.clients:
            try:
                client.close()
                self.clients.remove(client)
            except:
                pass
            
        if len(self.clients) == 0:
            self.running = False

    def cleanup(self):
        print("Cleaning up server resources...")
        self.running = False
        for client in self.clients:
            try:
                client.send("exit".encode())
                client.close()
            except:
                pass
        
        try:
            self.server_socket.close()
        except:
            pass
        
        print("Server closed")
        sys.exit(1)

if __name__ == "__main__":
    # Support command-line arguments for port
    port = 9999
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 9999.")
    
    server = GameServer(port=port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer shutdown requested...")
    finally:
        server.cleanup()