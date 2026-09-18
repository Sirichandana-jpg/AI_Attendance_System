import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()