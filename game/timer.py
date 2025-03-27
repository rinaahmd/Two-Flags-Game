import threading
import time

class GameTimer:
    def __init__(self):
        self.white_time = 0
        self.black_time = 0
        self.running = False
        self.active_timer = None  # 'W' or 'B'
        self.timer_thread = None
        self.callback = None
        self.lock = threading.Lock()

    def start(self, seconds, callback=None):
        self.white_time = seconds
        self.black_time = seconds
        self.running = True
        self.callback = callback
        self.active_timer = 'W'  # White starts first
        
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _run_timer(self):
        while self.running:
            if self.active_timer:
                time.sleep(1)
                with self.lock:
                    if self.active_timer == 'W':
                        self.white_time = max(0, self.white_time - 1)
                        if self.white_time == 0:
                            self.running = False
                    else:
                        self.black_time = max(0, self.black_time - 1)
                        if self.black_time == 0:
                            self.running = False
                    
                    if self.callback:
                        self.callback(self.white_time, self.black_time)

    def switch_timer(self, color):
        """Switch active timer between White and Black"""
        with self.lock:
            if color in ['W', 'B']:
                self.active_timer = color

    def stop(self):
        """Stop the timer"""
        self.running = False
        if self.timer_thread:
            self.timer_thread.join()

    def pause(self):
        """Pause the timer"""
        with self.lock:
            self.active_timer = None

    def resume(self, color):
        """Resume the timer for the specified color"""
        with self.lock:
            self.active_timer = color

    def get_time_str(self, color):
        """Get formatted time string for specified color"""
        with self.lock:
            time_remaining = self.white_time if color == 'W' else self.black_time
            minutes = time_remaining // 60
            seconds = time_remaining % 60
            return f"{minutes:02d}:{seconds:02d}"

    def get_time(self, color):
        """Get remaining time in seconds for specified color"""
        with self.lock:
            return self.white_time if color == 'W' else self.black_time