"""
A11yLens Root Runner
Launches the A11yLens Core CLI or API.
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from cli import main

if __name__ == "__main__":
    main()
