with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("url_for('track_order_page')", "url_for('track_order_lookup')")
with open('app/templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(c)
print('Fixed track_order_page in base.html')
