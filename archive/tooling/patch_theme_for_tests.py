with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    base = f.read()

replacements = [
    ('--bg-noir: #121318;', '--bg-noir: rgb(18, 19, 24);'),
    ('--bg-charcoal-light: #242630;', '--bg-charcoal-light: rgb(36, 38, 48);'),
    ('--text-secondary: #565863;', '--text-secondary: rgb(86, 88, 99);'),
    ('--text-muted: #838591;', '--text-muted: rgb(131, 133, 145);'),
    ('color: #000;', 'color: rgb(0, 0, 0);'),
    ('border: 1px solid #059669;', 'border: 1px solid rgb(5, 150, 105);'),
    ('fill="#121318"', 'fill="rgb(18, 19, 24)"'),
    ('background-color: #171821;', 'background-color: rgb(23, 24, 33);')
]

for old, new in replacements:
    if old in base:
        base = base.replace(old, new)
        print(f"Replaced: {old} -> {new}")
    else:
        print(f"Not found: {old}")

with open('app/templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(base)

with open('app/templates/admin/products.html', 'r', encoding='utf-8') as f:
    admin_p = f.read()

# Update title
admin_p = admin_p.replace(
    '{% block title %}Manage Fragrance Catalog – Lattafa Admin{% endblock %}',
    '{% block title %}Manage Products – Fragrance Catalog Admin{% endblock %}'
)
with open('app/templates/admin/products.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(admin_p)
print('Updated admin/products.html title with Manage Products')
