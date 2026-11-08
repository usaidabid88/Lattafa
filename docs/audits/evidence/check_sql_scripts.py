import os
import glob

sql_files = sorted(glob.glob('sql/*.sql'))
print(f"Total SQL files: {len(sql_files)}")

for sf in sql_files:
    with open(sf, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    first_few = "".join(lines[:10])
    size = os.path.getsize(sf)
    has_use = any('USE ' in l.upper() for l in lines)
    print(f"File: {sf} ({size} bytes, {len(lines)} lines)")
    print(f"  Has USE statement: {has_use}")
