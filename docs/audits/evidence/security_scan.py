import os
import re

app_py = 'app/app.py'

with open(app_py, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. SQL Injection Scan: Look for cur.execute with f-string or % formatting or string concatenation
dangerous_sql_patterns = re.findall(r'(\w+\.execute\s*\(\s*(?:f[\'"][^\'"]*\{[^\'"]*\}[\'"]|[\'"][^\'"]*[\'"]\s*%\s*[^\,\)]+|[\'"][^\'"]*[\'"]\s*\+\s*\w+))', code)
print(f"Dangerous SQL query patterns found in app.py: {len(dangerous_sql_patterns)}")
for p in dangerous_sql_patterns:
    print("  DANGER:", p)

# 2. Check cur.execute calls total vs parameterized
all_executes = re.findall(r'(\w+\.execute\s*\([^;]+?\))', code, re.DOTALL)
print(f"Total execute calls in app.py: {len(all_executes)}")

# 3. CSRF Protection Check
has_csrf_protect = 'CSRFProtect' in code or 'csrf_token' in code
print(f"CSRF tokens or protection present in app.py: {has_csrf_protect}")

# 4. Check forms in templates for csrf_token
template_forms = []
templates_dir = 'app/templates'
csrf_in_templates = 0
total_post_forms = 0
for root, dirs, files in os.walk(templates_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as tf:
                content = tf.read()
                forms = re.findall(r'<form[^>]*method=[\'"]post[\'"][^>]*>', content, re.IGNORECASE)
                total_post_forms += len(forms)
                if 'csrf_token' in content:
                    csrf_in_templates += 1

print(f"Total POST forms in templates: {total_post_forms}")
print(f"Templates containing csrf_token: {csrf_in_templates}")
