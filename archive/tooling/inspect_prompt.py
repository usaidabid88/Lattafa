import json

with open('C:/Users/shayy/.gemini/antigravity/brain/8161c124-08ea-427f-a6b9-8d00cf4b55c5/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            if 'PHASE 4' in content:
                for sec in content.split('\n# '):
                    lines = sec.splitlines()
                    title = lines[0] if lines else ''
                    print('SECTION:', title)
                    if any(term in title.upper() for term in ['DELIVERABLE', 'DOCUMENTATION', 'REPORT', 'STOP']):
                        print('\n--- CONTENT ---')
                        print('\n'.join(lines[:40]))
                        print('---------------\n')
