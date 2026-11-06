with open('app/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                    (
                        int(request.form['category_id']),
                        brand_id,
                        int(request.form['supplier_id']),
                        request.form['name'].strip(),
                        request.form.get('description', '').strip(),
                        float(request.form['price']),
                        int(request.form['stock_quantity']),
                        1 if request.form.get('is_active') else 0,
                        product_id
                    )
                )"""

insertion = """                    (
                        int(request.form['category_id']),
                        brand_id,
                        int(request.form['supplier_id']),
                        request.form['name'].strip(),
                        request.form.get('description', '').strip(),
                        float(request.form['price']),
                        int(request.form['stock_quantity']),
                        1 if request.form.get('is_active') else 0,
                        product_id
                    )
                )

                # Update or insert perfume details
                gender = request.form.get('gender')
                concentration = request.form.get('concentration')
                bottle_size = request.form.get('bottle_size')
                fragrance_family = request.form.get('fragrance_family')
                top_notes = request.form.get('top_notes')
                heart_notes = request.form.get('heart_notes')
                base_notes = request.form.get('base_notes')
                collection_name = request.form.get('collection_name')
                is_featured = 1 if request.form.get('is_featured') else 0
                is_bestseller = 1 if request.form.get('is_bestseller') else 0
                is_new_arrival = 1 if request.form.get('is_new_arrival') else 0

                if fragrance_family or top_notes or collection_name:
                    cur.execute(\"\"\"
                        INSERT INTO product_perfume_details 
                        (product_id, gender, concentration, bottle_size, fragrance_family, 
                         top_notes, heart_notes, base_notes, collection_name, is_featured, is_bestseller, is_new_arrival)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        gender=VALUES(gender), concentration=VALUES(concentration), bottle_size=VALUES(bottle_size),
                        fragrance_family=VALUES(fragrance_family), top_notes=VALUES(top_notes), heart_notes=VALUES(heart_notes),
                        base_notes=VALUES(base_notes), collection_name=VALUES(collection_name),
                        is_featured=VALUES(is_featured), is_bestseller=VALUES(is_bestseller), is_new_arrival=VALUES(is_new_arrival)
                    \"\"\", (product_id, gender or 'Unisex', concentration or 'Eau de Parfum (EDP)', bottle_size or '100ml',
                          fragrance_family or 'Oriental', top_notes or '', heart_notes or '', base_notes or '',
                          collection_name or 'Mainline Classics', is_featured, is_bestseller, is_new_arrival))"""

if target in text:
    new_text = text.replace(target, insertion, 1)
    with open('app/app.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Admin edit perfume logic successfully added!")
else:
    print("Target not found.")
