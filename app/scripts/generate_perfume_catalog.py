"""
Backward-compatibility wrapper for generate_perfume_catalog.py.
Canonical location: scripts/maintenance/generate_perfume_catalog.py
"""
import sys
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent.parent.parent / "scripts" / "maintenance" / "generate_perfume_catalog.py"
if __name__ == "__main__":
    runpy.run_path(str(target), run_name="__main__")
