with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = '<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">'
replacement = target + '\n    <link rel="icon" type="image/svg+xml" href="{{ url_for(\'static\', filename=\'images/branding/brandmark.svg\') }}">'

if target in c and 'rel="icon"' not in c:
    c = c.replace(target, replacement, 1)
    with open('app/templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print("Added brandmark favicon to base.html")
