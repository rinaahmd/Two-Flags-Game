import subprocess
import sys
import time
import re
import os
from search.minmax import Minmax
from game.board import ChessBoard
from search.ai_agent import AIAgent

# ANSI color codes for terminal
class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

def colorize_text(text):
    """Add colors to specific parts of the output"""
    colored_text = text
    colored_text = colored_text.replace("your turn", f"{Colors.BRIGHT_GREEN}your turn{Colors.RESET}")
    colored_text = colored_text.replace("external agent move", f"{Colors.BRIGHT_MAGENTA}external agent move{Colors.RESET}")
    colored_text = colored_text.replace(" W ", f" {Colors.BRIGHT_WHITE}W{Colors.RESET} ")
    colored_text = colored_text.replace(" B ", f" {Colors.BRIGHT_RED}B{Colors.RESET} ")
    if "A    B    C    D    E    F    G    H" in text:
        colored_text = colored_text.replace("        A    B    C    D    E    F    G    H",
                                            f"{Colors.BRIGHT_CYAN}A    B    C    D    E    F    G    H{Colors.RESET}")
    return colored_text

def colorize_move(move):
    """Color the AI's move"""
    return f"{Colors.BRIGHT_YELLOW}{move}{Colors.RESET}"

def print_chess_board(board):
    """Print the chess board in a visually appealing way"""
    print(f"{Colors.BRIGHT_CYAN}        A    B    C    D    E    F    G    H{Colors.RESET}")
    for row in range(8):
        print(f"    {8 - row} ", end="")
        for col in range(8):
            piece = board.boardArray[row][col]
            if piece == 'W':
                print(f"  {Colors.BRIGHT_WHITE}W{Colors.RESET}  ", end="")
            elif piece == 'B':
                print(f"  {Colors.BRIGHT_RED}B{Colors.RESET}  ", end="")
            else:
                print("  *  ", end="")
        print(f" {8 - row}")
    print(f"{Colors.BRIGHT_CYAN}        A    B    C    D    E    F    G    H{Colors.RESET}")

def print_final_board(board, winner):
    """Print the final board with a highlighted winner"""
    border = f"{Colors.BRIGHT_CYAN}╔════════════════════════════════════════════════════════╗{Colors.RESET}"
    print("\n" + border)
    
    title_color = Colors.BRIGHT_GREEN if winner == 'W' else Colors.BRIGHT_RED
    title = f"{title_color}               FINAL BOARD POSITION                {Colors.RESET}"
    print(title)
    
    print_chess_board(board)
    
    win_text = f"Winner: {'WHITE' if winner == 'W' else 'BLACK'}"
    winner_text = f"{title_color}                    {win_text}                      {Colors.RESET}"
    print(winner_text)
    
    print(f"{Colors.BRIGHT_CYAN}╚════════════════════════════════════════════════════════╝{Colors.RESET}\n")

def check_win_condition(board, current_player):
    """
    Check if the game has been won
    1. If one player has no pieces left
    2. If a player's piece reaches the opponent's side (row 0 for white, row 7 for black)
    """
    white_pieces = 0
    black_pieces = 0
    white_reached_top = False
    black_reached_bottom = False
    
    for row in range(8):
        for col in range(8):
            piece = board.boardArray[row][col]
            if piece == 'W':
                white_pieces += 1
                if row == 0:
                    white_reached_top = True
            elif piece == 'B':
                black_pieces += 1
                if row == 7:
                    black_reached_bottom = True
    
    if white_pieces == 0:
        return 'B'
    elif black_pieces == 0:
        return 'W'
    elif white_reached_top:
        return 'W'
    elif black_reached_bottom:
        return 'B'
    
    return None

def print_win_message(winner):
    """Print a message indicating which player has won"""
    if winner == 'W':
        print(f"\n{Colors.BRIGHT_GREEN}==========================================={Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}🏆 WHITE HAS WON THE GAME! 🏆{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}==========================================={Colors.RESET}\n")
    else:
        print(f"\n{Colors.BRIGHT_RED}==========================================={Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}🏆 BLACK HAS WON THE GAME! 🏆{Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}==========================================={Colors.RESET}\n")

def main():
    """Main function to play against the external EXE"""

    if len(sys.argv) < 2:
        print(f"{Colors.BRIGHT_RED}Usage: python play_against_exe.py <path_to_exe>{Colors.RESET}")
        return
        
    exe_path = sys.argv[1]
    
    print(f"{Colors.BRIGHT_CYAN}=== Two Flags Game - AI vs External Agent ==={Colors.RESET}")
    
    print(f"{Colors.BRIGHT_YELLOW}Choose your color:{Colors.RESET}")
    print(f"1. {Colors.BRIGHT_WHITE}White{Colors.RESET}")
    print(f"-1. {Colors.BRIGHT_RED}Black{Colors.RESET}")
    
    color_choice = input("Enter your choice (1 or -1): ").strip()
    print(f"\n{Colors.BRIGHT_YELLOW}Set time limit for the game:{Colors.RESET}")
    time_limit = input("Enter time limit in minutes: ").strip()

    board = ChessBoard()
    
    process = None
    try:
        process = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        initial_text = read_until_prompt(process, "black")
        send_command(process, color_choice)
        
        time_prompt = read_until_prompt(process, "minutes")
        send_command(process, time_limit)
        
        ai_agent = AIAgent(algorithm="minmax", time_limit_minutes=int(time_limit))
        
        player_color = 'W' if color_choice == "1" else 'B'
        opponent_color = 'B' if player_color == 'W' else 'W'
        
        if player_color == 'W':
            # White goes first
            initial_board = read_until_prompt(process, "turn")
            
            board = extract_board_state(initial_board) or board
            print(f"\n{Colors.BRIGHT_CYAN}Initial board setup:{Colors.RESET}")
            print_chess_board(board)
            
            board_tracker = BoardState()
            board_tracker.update_from_text(initial_board)
            
            game_over = False
            winner = None
            
            while not game_over:
                winner = check_win_condition(board, player_color)
                if winner:
                    print_win_message(winner)
                    print_final_board(board, winner)
                    game_over = True
                    break
                    
                # -------------------------------------------
                # AI picks White's move
                # -------------------------------------------
                print("_____________________________________________________________________________________")
                move_str = ai_agent.get_move(board, player_color)
                print(f"{Colors.BRIGHT_GREEN}Your agent move is: {colorize_move(move_str)}{Colors.RESET}")
                
                from_col = ord(move_str[0]) - ord('a')
                from_row = 8 - int(move_str[1])
                to_col = ord(move_str[2]) - ord('a')
                to_row = 8 - int(move_str[3])
                move = (from_row, from_col, to_row, to_col)
                board.computeMove(move, player_color)
                
                print_chess_board(board)
                
                winner = check_win_condition(board, opponent_color)
                if winner:
                    print_win_message(winner)
                    print_final_board(board, winner)
                    game_over = True
                    break
                
                # Send White's move to external engine
                try:
                    send_command(process, move_str)
                    
                    # External agent's turn
                    print("_____________________________________________________________________________________")
                    print(f"{Colors.BRIGHT_MAGENTA}External agent move !!!!!!!!!!!!!!!!!!!!!!!{Colors.RESET}")
                    print("Thinking...")
                    
                    # <<<< ADDED >>>>
                    response = read_until_prompt(process, "turn")

                    # Parse the board from external agent's new move
                    updated_board = extract_board_state(response)
                    if updated_board:
                        board = updated_board
                        print_chess_board(board)


                    # Check for any "win"/"lose" messages
                    if "win" in response.lower() or "lose" in response.lower():
                        if "you win" in response.lower():
                            winner = player_color
                        else:
                            winner = opponent_color
                        print_win_message(winner)
                        
                        if updated_board:
                            board = updated_board
                        print_final_board(board, winner)
                        game_over = True
                        break

                    board_tracker.update_from_text(response)
                    
                except Exception as e:
                    print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                    break

        else:
            # Black goes second
            print(f"{Colors.BRIGHT_CYAN}You're playing as Black. Waiting for White's move...{Colors.RESET}")
            
            board_tracker = BoardState()
            game_over = False
            winner = None
            
            while not game_over:
                # External agent's move (White)
                response = read_until_prompt(process, "turn")

                updated_board = extract_board_state(response)
                if updated_board:
                    board = updated_board
                    print(f"\n{Colors.BRIGHT_CYAN}After opponent's move:{Colors.RESET}")
                    print_chess_board(board)


                board_tracker.update_from_text(response)
                
                winner = check_win_condition(board, player_color)
                if winner:
                    print_win_message(winner)
                    print_final_board(board, winner)
                    game_over = True
                    break
                
                if "win" in response.lower() or "lose" in response.lower():
                    if "you win" in response.lower():
                        winner = player_color
                    else:
                        winner = opponent_color
                    print_win_message(winner)
                    print_final_board(board, winner)
                    game_over = True
                    break
                
                # -------------------------------------------
                # AI picks Black's move
                # -------------------------------------------
                print("_____________________________________________________________________________________")
                move_str = ai_agent.get_move(board, player_color)
                print(f"{Colors.BRIGHT_GREEN}Your agent move is: {colorize_move(move_str)}{Colors.RESET}")
                
                from_col = ord(move_str[0]) - ord('a')
                from_row = 8 - int(move_str[1])
                to_col = ord(move_str[2]) - ord('a')
                to_row = 8 - int(move_str[3])
                move = (from_row, from_col, to_row, to_col)
                board.computeMove(move, player_color)
                
                print_chess_board(board)
                
                winner = check_win_condition(board, opponent_color)
                if winner:
                    print_win_message(winner)
                    print_final_board(board, winner)
                    game_over = True
                    break
                
                # Send Black's move to external engine
                try:
                    send_command(process, move_str)
                except Exception as e:
                    print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
                    break
        
        if game_over:
            print(f"{Colors.BRIGHT_CYAN}Game has ended. Thanks for playing!{Colors.RESET}")
            print(f"\n{Colors.BRIGHT_YELLOW}Press Enter to exit...{Colors.RESET}")
            input()
        
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error occurred: {e}{Colors.RESET}")
        print(f"\n{Colors.BRIGHT_YELLOW}Press Enter to exit...{Colors.RESET}")
        input()
    finally:
        try:
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
        except:
            if process and process.poll() is None:
                process.kill()

def extract_board_lines(text):
    """Extract only the board representation lines from the text"""
    lines = text.strip().split('\n')
    board_lines = []
    header_index = -1
    for i, line in enumerate(lines):
        if "A" in line and "B" in line and "C" in line and "D" in line:
            header_index = i
            board_lines.append(line)
            break
    if header_index >= 0:
        for i in range(header_index + 1, min(header_index + 9, len(lines))):
            if i < len(lines) and re.match(r'^\s*\d+\s+', lines[i]):
                board_lines.append(lines[i])
    return board_lines

def format_response(text):
    """Format the response to ensure consistent board coordinates and remove unnecessary info"""
    lines = text.strip().split('\n')
    result = []
    
    for i, line in enumerate(lines):
        if "time" in line.lower() or "depth" in line.lower() or "clock" in line.lower():
            continue
        if re.match(r'\s*[A-H](\s+[A-H])+', line, re.IGNORECASE):
            result.append("              A   B   C   D   E   F   G   H")
            continue
        result.append(line)
    
    return '\n'.join(result)

class BoardState:
    """Track the board state"""
    def __init__(self):
        self.board = [['*' for _ in range(8)] for _ in range(8)]
        
    def update_from_text(self, text):
        lines = text.strip().split('\n')
        board_lines = []
        
        for line in lines:
            if re.match(r'^\s*\d+\s+', line) and ('*' in line or 'B' in line or 'W' in line):
                board_lines.append(line.strip())
        
        if len(board_lines) == 0:
            return
            
        for line in board_lines:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
                
            try:
                row_num = int(parts[0])
                row_index = 8 - row_num
                for col in range(8):
                    if col + 1 < len(parts):
                        self.board[row_index][col] = parts[col + 1]
            except (ValueError, IndexError):
                continue

def send_command(process, command):
    """Send a command to the external process"""
    try:
        if process.poll() is not None:
            raise Exception("Process has terminated")
        if os.name == 'nt':
            command_bytes = (command + '\r\n').encode('utf-8')
        else:
            command_bytes = (command + '\n').encode('utf-8')
        process.stdin.buffer.write(command_bytes)
        process.stdin.buffer.flush()
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error sending command: {e}{Colors.RESET}")
        raise

def read_until_prompt(process, pattern, timeout=60):
    """Read output until a specific pattern is found"""
    start_time = time.time()
    output = ""
    
    while time.time() - start_time < timeout:
        try:
            if process.poll() is not None:
                break
            if process.stdout.readable():
                line = process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                # Here, you collect lines into 'output'
                output += line
                if pattern in line:
                    return output
            else:
                time.sleep(0.1)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error reading output: {e}{Colors.RESET}")
            time.sleep(0.1)
    return output

def extract_board_state(text):
    """Extract board state from text and create a new board instance"""
    lines = text.strip().split('\n')
    board_lines = []
    for line in lines:
        if re.match(r'^\s*\d+\s+', line) and ('*' in line or 'B' in line or 'W' in line):
            board_lines.append(line.strip())
    if len(board_lines) == 0:
        return None
    
    new_board = ChessBoard()
    
    for line in board_lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        try:
            row_num = int(parts[0])
            row_index = 8 - row_num
            for col in range(8):
                if col + 1 < len(parts):
                    piece = parts[col + 1]
                    if piece == 'W':
                        new_board.boardArray[row_index][col] = 'W'
                    elif piece == 'B':
                        new_board.boardArray[row_index][col] = 'B'
                    else:
                        new_board.boardArray[row_index][col] = ' '
        except (ValueError, IndexError):
            continue
    return new_board

if __name__ == "__main__":
    main()
