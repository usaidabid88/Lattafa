import re

with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any hex codes starting with a digit in base.html with rgb(...)
replacements = {
    '#17181f': 'rgb(23, 24, 31)',
    '#845d19': 'rgb(132, 93, 25)',
    '#18191e': 'rgb(24, 25, 30)',
    '#7d786e': 'rgb(125, 120, 110)',
    '#0d0e12': 'rgb(13, 14, 18)',
    '#12110f': 'rgb(18, 17, 15)',
    '#0b0c0f': 'rgb(11, 12, 15)',
    '#10b981': 'rgb(16, 185, 129)',
    '#065f46': 'rgb(6, 95, 70)',
    '#991b1b': 'rgb(153, 27, 27)',
    '#ef4444': 'rgb(239, 68, 68)',
    '#161513': 'rgb(22, 21, 19)',
    '#1c1a18': 'rgb(28, 26, 24)',
    '#262421': 'rgb(38, 36, 33)'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('app/templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Updated base.html hex codes starting with digits to rgb()")
