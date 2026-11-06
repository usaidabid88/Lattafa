with open('app/app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()

app_py = app_py.replace('ppd.bottle_size_ml', 'ppd.bottle_size')
with open('app/app.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(app_py)
print('Updated app/app.py with ppd.bottle_size')

with open('app/templates/admin/products.html', 'r', encoding='utf-8') as f:
    admin_prod = f.read()

admin_prod = admin_prod.replace('p.bottle_size_ml', 'p.bottle_size')
with open('app/templates/admin/products.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(admin_prod)
print('Updated app/templates/admin/products.html with p.bottle_size')

with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

base_html = base_html.replace(
    'MUET DBMS CEP &bull; Academic Demonstration',
    'MUET Shop &bull; DBMS CEP Perfume Edition'
)

with open('app/templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(base_html)
print('Updated announcement bar in base.html with MUET Shop')
