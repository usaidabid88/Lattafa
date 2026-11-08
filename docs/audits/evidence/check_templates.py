import os
import re

app_py_path = 'app/app.py'
templates_dir = 'app/templates'

with open(app_py_path, 'r', encoding='utf-8') as f:
    code = f.read()

rendered = set(re.findall(r'render_template\(\s*[\'"]([^\'"]+)[\'"]', code))

existing = set()
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        rel_path = os.path.relpath(os.path.join(root, file), templates_dir).replace('\\', '/')
        existing.add(rel_path)

missing = rendered - existing
unused = existing - rendered

print("=== TEMPLATE AUDIT ===")
print(f"Total template references in app.py: {len(rendered)}")
print(f"Total template files on disk: {len(existing)}")
print(f"Missing templates (referenced but not on disk): {missing}")
print(f"Unused templates (on disk but not referenced directly): {unused}")
