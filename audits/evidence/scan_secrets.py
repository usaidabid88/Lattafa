import os
import re

ignore_dirs = {'.git', 'venv', '__pycache__', '.pytest_cache'}
secret_patterns = [
    (r'(?i)(?:api[_-]?key|secret[_-]?key|private[_-]?key)\s*=\s*[\'"][^\'"]{8,}[\'"]', 'Potential Secret Key'),
    (r'(?i)password\s*=\s*[\'"][^\'"]{6,}[\'"]', 'Potential Hardcoded Password'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
    (r'AIza[0-9A-Za-z-_]{35}', 'Google API Key'),
]

findings = []

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        if file.endswith(('.py', '.sql', '.json', '.html', '.md', '.yml', '.yaml', '.txt')):
            path = os.path.join(root, file)
            # Skip .env and .env.example
            if file in {'.env', '.env.example'}:
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_no, line in enumerate(f, 1):
                    for pattern, desc in secret_patterns:
                        if re.search(pattern, line):
                            # Filter out test passwords or sample passwords in seed scripts
                            if 'AdminPass123!' in line or 'StaffPass123!' in line or 'CustomerPass123!' in line or 'password123' in line:
                                continue
                            if 'fallback-dev-secret-key' in line or 'muet-dbs-production-secret-2026' in line:
                                findings.append((path, line_no, desc, 'Fallback Default Secret Key'))
                            elif 'rootpassword' in line or 'shoppass123' in line:
                                findings.append((path, line_no, desc, 'Default Compose Password'))
                            else:
                                findings.append((path, line_no, desc, 'Unclassified'))

print(f"Total secret scanner alerts: {len(findings)}")
for f in findings:
    print(f"  {f[0]}:{f[1]} -> {f[2]} ({f[3]})")
