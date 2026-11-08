"""
Backward-compatibility wrapper for import_catalog.py.
Canonical location: scripts/database/import_catalog.py
"""
import sys
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent.parent.parent / "scripts" / "database" / "import_catalog.py"
if __name__ == "__main__":
    runpy.run_path(str(target), run_name="__main__")
