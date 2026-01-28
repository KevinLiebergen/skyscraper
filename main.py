import sys
import os

# Add src/ directory to the path so modules can be found
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.application import SkyscraperApp

def main():
    app = SkyscraperApp()
    app.run()

if __name__ == "__main__":
    main()
