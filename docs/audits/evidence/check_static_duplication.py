import os
import filecmp

dir1 = 'static'
dir2 = 'app/static'

def get_files(base):
    res = {}
    for root, dirs, files in os.walk(base):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, base)
            res[rel] = full
    return res

f1 = get_files(dir1)
f2 = get_files(dir2)

print(f"Files in root static/: {len(f1)}")
print(f"Files in app/static/: {len(f2)}")

diff_keys = set(f1.keys()) ^ set(f2.keys())
print(f"Keys difference: {len(diff_keys)}")

identical = 0
differing = 0
for k in set(f1.keys()) & set(f2.keys()):
    if filecmp.cmp(f1[k], f2[k], shallow=False):
        identical += 1
    else:
        differing += 1

print(f"Identical files: {identical}")
print(f"Differing files: {differing}")
