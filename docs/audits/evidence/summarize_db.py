import json

with open('audits/evidence/db_inventory.json', 'r', encoding='utf-8') as f:
    inv = json.load(f)

print('TABLES & ROW COUNTS:')
for t, d in sorted(inv['tables'].items()):
    print(f'  {t:25}: {d["row_count"]} rows')

print('\nVIEWS:')
for v, d in sorted(inv['views'].items()):
    print(f'  {v:25}: {d["status"]} ({d["row_count"]} rows)')

print('\nPROCEDURES:')
for p in sorted(inv['procedures']):
    print(f'  {p}')

print('\nTRIGGERS:')
for tr in sorted(inv['triggers'], key=lambda x: x['TRIGGER_NAME']):
    print(f'  {tr["TRIGGER_NAME"]:40}: {tr["ACTION_TIMING"]} {tr["EVENT_MANIPULATION"]} ON {tr["EVENT_OBJECT_TABLE"]}')
