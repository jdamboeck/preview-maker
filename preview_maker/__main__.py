"""Main entry point for the Preview Maker package.

This module allows running the application as a Python module:
python -m preview_maker
"""

import sys
from preview_maker.app import main

if __name__ == "__main__":
    sys.exit(main())
