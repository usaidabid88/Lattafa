import os
import sys
import re
import glob

sys.path.insert(0, os.path.abspath('.'))
from app.app import app

rule_names = set(app.view_functions.keys())
rule_names.add('static')

found_issues = False
for path in glob.glob('app/templates/**/*.html', recursive=True):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    endpoints = re.findall(r"url_for\(\s*['\"]([^'\"]+)['\"]", content)
    missing = [e for e in set(endpoints) if e not in rule_names]
    if missing:
        found_issues = True
        print(f"Missing in {path}: {missing}")

if not found_issues:
    print("ALL template url_for endpoints are valid!")
