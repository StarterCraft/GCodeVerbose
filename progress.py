import sys

class ProgressBar:
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.prev_len = 0

    def update(self, increment: int = 1):
        self._clear()

        self.current += increment
        if (not self.current <= self.total):
            self.current = self.total

        progress = self.current / self.total * 100  # Calculate progress percentage
        bar_length = 64  # Length of the progress bar
        filled_length = int(progress / 100 * bar_length)  # Calculate the filled part of the progress bar

        bar = '#' * filled_length + '-' * (bar_length - filled_length)  # Create the progress bar string
        current_string = '[{}/{}] {} {}% complete'.format(self.current, self.total, bar, int(progress))
        self.prev_len = len(current_string)
        print(current_string, end='\r', flush=True)

    def _clear(self):
        if self.current == 0:
            return

        if sys.stdout.isatty():
            print('\033[K', end='')  # Clear the current line in the console
            sys.stdout.flush()
        else:
            print('')
            