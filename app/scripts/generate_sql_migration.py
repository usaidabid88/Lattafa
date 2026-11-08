"""
Backward-compatibility wrapper for generate_sql_migration.py.
Canonical location: scripts/database/generate_sql_migration.py
"""
import sys
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent.parent.parent / "scripts" / "database" / "generate_sql_migration.py"
if __name__ == "__main__":
    runpy.run_path(str(target), run_name="__main__")
