import os.path
from terminal import Terminal
from colorama import init
from formatting import Formatting

if __name__ == "__main__":
    init()
    if os.path.exists('os.txt'):
        terminal = Terminal('os.txt')
        terminal.run()
    else:
        print('OS does not exist!')
