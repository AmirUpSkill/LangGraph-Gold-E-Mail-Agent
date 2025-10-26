"""
Pytest configuration and fixtures for test suite.
"""

import sys
from pathlib import Path

# Add the agent root to Python path so imports work correctly
agent_root = Path(__file__).parent.parent
sys.path.insert(0, str(agent_root))
