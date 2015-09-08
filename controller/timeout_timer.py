import threading

# Timer class that monitors elapsed time from request to response.
# Expires after timer_value seconds
class TimeoutTimer:

    # Initialize object
    def __init__(self, timer_value, callback):
        self.value = timer_value
        self.callback = callback
        self.timer = None

    # Start timeout timer
    def start(self):
        self.timer = threading.Timer(self.value, self.callback)
        self.timer.start()

    # Stop timeout timer
    def stop(self):
        try:
            self.timer.cancel()
        except AttributeError:
            # Timer cancel attempt when timer is not started
            pass