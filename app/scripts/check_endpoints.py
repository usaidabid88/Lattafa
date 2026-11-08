"""
Backward-compatibility wrapper for check_endpoints.py.
Canonical location: scripts/development/check_endpoints.py
"""
import sys
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent.parent.parent / "scripts" / "development" / "check_endpoints.py"
if __name__ == "__main__":
    runpy.run_path(str(target), run_name="__main__")
