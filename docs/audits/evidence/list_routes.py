import os
import sys
app_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'app')
sys.path.insert(0, app_dir)
from app import app

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
        'rule': str(rule)
    })

routes.sort(key=lambda x: x['rule'])

with open('audits/evidence/app_routes.json', 'w', encoding='utf-8') as f:
    import json
    json.dump(routes, f, indent=2)

print(f"Total application routes registered: {len(routes)}")
for r in routes:
    print(f"  {r['rule']:35} {r['methods']} -> {r['endpoint']}")
