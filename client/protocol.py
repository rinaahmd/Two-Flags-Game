def parse_setup(data):
    # Parse the setup command
    # Example: "Setup Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7"
    parts = data.split()
    setup_data = parts[1:]  # Skip the "Setup" command
    return setup_data

def parse_time(data):
    # Parse the time command
    # Example: "Time 30"
    parts = data.split()
    return int(parts[1])  # Return the time in minutes

def parse_move(data):
    # Parse the move command
    # Example: "e2e4"
    from_pos = (8 - int(data[1]), ord(data[0]) - ord('a'))
    to_pos = (8 - int(data[3]), ord(data[2]) - ord('a'))
    return from_pos, to_pos