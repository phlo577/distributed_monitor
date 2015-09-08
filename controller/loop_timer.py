import threading

# Periodic loop timer class
class LoopTimer:
    def __init__(self, period, callback, *args, **kwargs):
        self.period = period
        self.stopped = True
        self.callback = callback
        self.count = 0
        self.timer = None
        self.args = args
        self.kwargs = kwargs

    def restart(self):
        # Function restarts timer only if it was stopped
        if not self.stopped:
            self.timer = threading.Timer(self.period, self.callback, *self.args, **self.kwargs)
            self.timer.start()
        else:
            pass
    
    def start(self):
        # First start of timer
        self.stopped = False
        self.restart()
        
    def stop(self):
        self.stopped = True
        try:
            self.timer.cancel()
        except AttributeError:
            # Timer cancel attempt when timer is not started
            pass
