"""Pytest configuration — adds the tests directory to sys.path for helpers import."""

import sys
from pathlib import Path

# Allow `from helpers import ...` in test files
sys.path.insert(0, str(Path(__file__).parent))
