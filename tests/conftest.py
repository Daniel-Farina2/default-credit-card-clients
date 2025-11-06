import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    # Ensure application package is importable when tests run from any CWD.
    sys.path.insert(0, str(PROJECT_ROOT))
