"""
update_app_py.py
Updates app/app.py to add perfume routes, collection filtering, olfactory notes, and admin handling.
"""

import re

with open("app/app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update index()
old_index = """@app.route('/')
def index():
    \"\"\"Homepage with 5 department cards, featured specimen, and live stats.\"\"\"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
        total_products = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM orders")
        total_orders = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_users = cur.fetchone()['cnt']

        # 5 Department Cards from v_category_counts
        cur.execute(\"\"\"
            SELECT category_id, category_name, category_slug, image_path, active_product_count
            FROM v_category_counts
            WHERE parent_category_id IS NULL AND category_slug != 'home-living'
            ORDER BY category_id
        \"\"\")
        departments = cur.fetchall()

    return render_template('index.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users,
                           departments=departments)"""

new_index = """@app.route('/')
def index():
    \"\"\"Homepage for Arabian Luxury Perfumery with collections, bestsellers, new arrivals, and live stats.\"\"\"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
        total_products = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM orders")
        total_orders = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_users = cur.fetchone()['cnt']

        # Perfume Best Sellers
        cur.execute(\"\"\"
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_bestseller = 1 AND is_active = 1
            ORDER BY avg_rating DESC, product_id DESC
            LIMIT 8
        \"\"\")
        best_sellers = cur.fetchall()
        if not best_sellers:
            cur.execute(\"\"\"
                SELECT product_id, product_name, price, primary_image, brand_name,
                       concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
                FROM v_perfume_catalog
                WHERE is_active = 1
                ORDER BY product_id DESC
                LIMIT 8
            \"\"\")
            best_sellers = cur.fetchall()

        # Perfume New Arrivals
        cur.execute(\"\"\"
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_new_arrival = 1 AND is_active = 1
            ORDER BY product_id DESC
            LIMIT 8
        \"\"\")
        new_arrivals = cur.fetchall()

        # Promotional & Gift Sets
        cur.execute(\"\"\"
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_featured = 1 AND is_active = 1
            ORDER BY price DESC
            LIMIT 4
        \"\"\")
        promotional_perfumes = cur.fetchall()

        # Featured Collections Matrix
        featured_collections = [
            {
                'name': 'Yara Collection',
                'slug': 'yara-collection',
                'subtitle': 'Sweet Gourmand & Ethereal Florals',
                'image': 'static/images/collections/yara_collection.svg',
                'count': 4
            },
            {
                'name': 'Asad Collection',
                'slug': 'asad-collection',
                'subtitle': 'Masculine Power & Noble Woods',
                'image': 'static/images/collections/asad_collection.svg',
                'count': 3
            },
            {
                'name': 'Khamrah Collection',
                'slug': 'khamrah-collection',
                'subtitle': 'Golden Spices & Date Gourmand',
                'image': 'static/images/collections/khamrah_collection.svg',
                'count': 3
            },
            {
                'name': 'Badee Al Oud',
                'slug': 'badee-al-oud',
                'subtitle': 'Royal Agarwood & Opulent Blends',
                'image': 'static/images/collections/badee_al_oud.svg',
                'count': 5
            },
            {
                'name': 'Lattafa Pride',
                'slug': 'lattafa-pride',
                'subtitle': 'Artisanal Haute Parfumerie',
                'image': 'static/images/collections/lattafa_pride.svg',
                'count': 11
            },
            {
                'name': 'Maison Alhambra',
                'slug': 'maison-alhambra',
                'subtitle': 'Parisian Chic with Arabian Depth',
                'image': 'static/images/collections/maison_alhambra.svg',
                'count': 30
            }
        ]

        # Perfume Gender Categories
        cur.execute(\"\"\"
            SELECT category_id, name, slug, image_path
            FROM categories
            WHERE slug IN ('men', 'women', 'unisex')
            ORDER BY category_id
        \"\"\")
        gender_categories = cur.fetchall()

        # Legacy department cards preserved for backward compatibility
        cur.execute(\"\"\"
            SELECT category_id, category_name, category_slug, image_path, active_product_count
            FROM v_category_counts
            WHERE parent_category_id IS NULL AND category_slug != 'home-living'
            ORDER BY category_id
        \"\"\")
        departments = cur.fetchall()

    return render_template('index.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users,
                           departments=departments,
                           featured_collections=featured_collections,
                           best_sellers=best_sellers,
                           new_arrivals=new_arrivals,
                           promotional_perfumes=promotional_perfumes,
                           gender_categories=gender_categories)"""

# Normalize line endings for replacement
content_norm = content.replace("\r\n", "\n")
old_index_norm = old_index.replace("\r\n", "\n")
new_index_norm = new_index.replace("\r\n", "\n")

if old_index_norm in content_norm:
    content_norm = content_norm.replace(old_index_norm, new_index_norm)
    print("1. Successfully updated index() route.")
else:
    print("ERROR: old_index not found in content!")

# 2. Add collection & shortcut routes
collection_routes = """
# ─── PERFUME COLLECTION & NAVIGATION ROUTES ───────────────────────────────────

@app.route('/collections')
def collections_index():
    \"\"\"Directory of all perfume collections with member counts and price ranges.\"\"\"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT collection_name, total_fragrances, min_price, max_price, avg_price
            FROM v_perfume_collections
            ORDER BY total_fragrances DESC
        \"\"\")
        collections = cur.fetchall()
    return render_template('collections.html', collections=collections)


@app.route('/collection/<slug>')
def collection_view(slug):
    \"\"\"View all perfumes in a designated collection.\"\"\"
    collection_name_map = {
        'yara-collection': 'Yara Collection',
        'asad-collection': 'Asad Collection',
        'khamrah-collection': 'Khamrah Collection',
        'badee-al-oud': 'Badee Al Oud',
        'lattafa-pride': 'Lattafa Pride',
        'maison-alhambra': 'Maison Alhambra Luxury',
        'mainline-classics': 'Mainline Classics'
    }
    col_name = collection_name_map.get(slug)
    if not col_name:
        col_name = slug.replace('-', ' ').title()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        \"\"\")
        col_param = f"%{col_name}%"
        cur.execute(\"\"\"
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        \"\"\", (col_param,))
        products = cur.fetchall()
        if not products:
            abort(404)
    return render_template('collection_detail.html',
                           collection_name=col_name,
                           collection_slug=slug,
                           products=products)


@app.route('/men')
def men_fragrances():
    return redirect(url_for('category_view', slug='men'))


@app.route('/women')
def women_fragrances():
    return redirect(url_for('category_view', slug='women'))


@app.route('/unisex')
def unisex_fragrances():
    return redirect(url_for('category_view', slug='unisex'))


@app.route('/bestsellers')
def bestsellers_page():
    return redirect(url_for('products', sort='rating'))


@app.route('/new-arrivals')
def new_arrivals_page():
    return redirect(url_for('products', sort='newest'))
"""

if "@app.route('/collections')" not in content_norm:
    # Insert right before @app.route('/category/<slug>')
    content_norm = content_norm.replace(
        "@app.route('/category/<slug>')",
        collection_routes.strip() + "\n\n@app.route('/category/<slug>')"
    )
    print("2. Successfully inserted collection and navigation routes.")

# 3. Update products() route with perfume filters
old_products = """@app.route('/products')
def products():
    \"\"\"Product listing with search, category filter, brand filter, and price sort.\"\"\"
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', '', type=str)
    brand_filter = request.args.get('brand', '').strip()
    sort_by = request.args.get('sort', '').strip()

    conn = get_db()
    with conn.cursor() as cur:
        # Categories for filter
        cur.execute("SELECT category_id, name, slug FROM categories ORDER BY name")
        categories = cur.fetchall()

        # Available brands for filter
        cur.execute("SELECT DISTINCT brand_id, name AS brand_name FROM brands ORDER BY name")
        brands = cur.fetchall()

        # Query v_product_catalog
        sql = \"\"\"
            SELECT product_id, product_name AS name, price, stock_quantity,
                   is_active, category_name, category_slug, brand_name,
                   primary_image, short_description, avg_rating, review_count
            FROM v_product_catalog
            WHERE is_active = 1
        \"\"\"
        params = []
        if q:
            sql += " AND (product_name LIKE %s OR description LIKE %s)"
            params.extend([f'%{q}%', f'%{q}%'])
        if category_id:
            sql += " AND (category_id = %s OR parent_category_id = %s)"
            params.extend([int(category_id), int(category_id)])
        if brand_filter:
            sql += " AND brand_name = %s"
            params.append(brand_filter)

        if sort_by == 'price_asc':
            sql += " ORDER BY price ASC, product_id DESC"
        elif sort_by == 'price_desc':
            sql += " ORDER BY price DESC, product_id DESC"
        elif sort_by == 'rating':
            sql += " ORDER BY avg_rating DESC, review_count DESC, product_id DESC"
        else:
            sql += " ORDER BY product_id DESC"

        cur.execute(sql, params)
        prods = cur.fetchall()

    return render_template('products.html',
                           products=prods,
                           categories=categories,
                           brands=brands,
                           q=q,
                           category_id=category_id,
                           brand_filter=brand_filter,
                           sort_by=sort_by)"""

new_products = """@app.route('/products')
def products():
    \"\"\"Product listing with search, category filter, brand filter, gender, collection, family, and price sort.\"\"\"
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', '', type=str)
    brand_filter = request.args.get('brand', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    collection_filter = request.args.get('collection', '').strip()
    family_filter = request.args.get('family', '').strip()
    min_price = request.args.get('min_price', '', type=str)
    max_price = request.args.get('max_price', '', type=str)
    sort_by = request.args.get('sort', '').strip()

    conn = get_db()
    with conn.cursor() as cur:
        # Categories for filter
        cur.execute("SELECT category_id, name, slug FROM categories ORDER BY (category_id >= 100) DESC, name ASC")
        categories = cur.fetchall()

        # Available brands for filter
        cur.execute("SELECT DISTINCT brand_id, name AS brand_name FROM brands ORDER BY (brand_id >= 100) DESC, name ASC")
        brands = cur.fetchall()

        # Collections and Fragrance Families for filter
        cur.execute("SELECT DISTINCT collection_name FROM product_perfume_details ORDER BY collection_name ASC")
        collections = [r['collection_name'] for r in cur.fetchall()]

        cur.execute("SELECT DISTINCT fragrance_family FROM product_perfume_details ORDER BY fragrance_family ASC")
        families = [r['fragrance_family'] for r in cur.fetchall()]

        # Query v_perfume_catalog
        sql = \"\"\"
            SELECT product_id, product_name AS name, price, stock_quantity,
                   is_active, category_name, category_slug, brand_name,
                   primary_image, short_description, avg_rating, review_count,
                   gender, concentration, bottle_size, fragrance_family,
                   collection_name, is_featured, is_bestseller, is_new_arrival
            FROM v_perfume_catalog
            WHERE is_active = 1
        \"\"\"
        params = []
        if q:
            sql += " AND (product_name LIKE %s OR description LIKE %s OR collection_name LIKE %s OR top_notes LIKE %s)"
            params.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])
        if category_id:
            sql += " AND (category_id = %s OR parent_category_id = %s)"
            params.extend([int(category_id), int(category_id)])
        if brand_filter:
            sql += " AND brand_name = %s"
            params.append(brand_filter)
        if gender_filter:
            sql += " AND gender = %s"
            params.append(gender_filter)
        if collection_filter:
            sql += " AND collection_name = %s"
            params.append(collection_filter)
        if family_filter:
            sql += " AND fragrance_family = %s"
            params.append(family_filter)
        if min_price:
            try:
                sql += " AND price >= %s"
                params.append(float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                sql += " AND price <= %s"
                params.append(float(max_price))
            except ValueError:
                pass

        if sort_by == 'price_asc':
            sql += " ORDER BY price ASC, product_id DESC"
        elif sort_by == 'price_desc':
            sql += " ORDER BY price DESC, product_id DESC"
        elif sort_by == 'rating':
            sql += " ORDER BY avg_rating DESC, review_count DESC, product_id DESC"
        elif sort_by == 'newest':
            sql += " ORDER BY is_new_arrival DESC, product_id DESC"
        else:
            # Prioritizes perfume catalog records (id >= 100) on storefront
            sql += " ORDER BY (product_id >= 100) DESC, product_id DESC"

        cur.execute(sql, params)
        prods = cur.fetchall()

    return render_template('products.html',
                           products=prods,
                           categories=categories,
                           brands=brands,
                           collections=collections,
                           families=families,
                           q=q,
                           category_id=category_id,
                           brand_filter=brand_filter,
                           gender_filter=gender_filter,
                           collection_filter=collection_filter,
                           family_filter=family_filter,
                           min_price=min_price,
                           max_price=max_price,
                           sort_by=sort_by)"""

old_products_norm = old_products.replace("\r\n", "\n")
new_products_norm = new_products.replace("\r\n", "\n")

if old_products_norm in content_norm:
    content_norm = content_norm.replace(old_products_norm, new_products_norm)
    print("3. Successfully updated products() route.")
else:
    print("ERROR: old_products not found in content!")

# 4. Update product_detail() route
old_detail = """@app.route('/product/<int:product_id>')
def product_detail(product_id):
    \"\"\"Single product page with multi-image gallery, brand specs, and reviews.\"\"\"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT p.*, s.name AS supplier_name
            FROM v_product_catalog p
            JOIN products pr ON p.product_id = pr.product_id
            JOIN suppliers s ON pr.supplier_id = s.supplier_id
            WHERE p.product_id = %s
        \"\"\", (product_id,))
        product = cur.fetchone()

        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))

        # Get all images for this product (gallery)
        cur.execute(\"\"\"
            SELECT image_id, image_path, is_primary, sort_order
            FROM product_images
            WHERE product_id = %s
            ORDER BY sort_order ASC, image_id ASC
        \"\"\", (product_id,))
        images = cur.fetchall()

        if not images:
            images = [{'image_id': 0, 'image_path': product['primary_image'], 'is_primary': 1, 'sort_order': 1}]

        # Verified reviews
        cur.execute(\"\"\"
            SELECT r.rating, r.comment, r.created_at, u.full_name AS customer_name, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        \"\"\", (product_id,))
        reviews = cur.fetchall()

    return render_template('product_detail.html',
                           product=product,
                           images=images,
                           reviews=reviews)"""

new_detail = """@app.route('/product/<int:product_id>')
def product_detail(product_id):
    \"\"\"Single perfume page with fragrance notes pyramid, collection specs, gallery, and reviews.\"\"\"
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            SELECT p.*, s.name AS supplier_name
            FROM v_perfume_catalog p
            JOIN products pr ON p.product_id = pr.product_id
            JOIN suppliers s ON pr.supplier_id = s.supplier_id
            WHERE p.product_id = %s
        \"\"\", (product_id,))
        product = cur.fetchone()

        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))

        # Get all images for this product (gallery)
        cur.execute(\"\"\"
            SELECT image_id, image_path, is_primary, sort_order
            FROM product_images
            WHERE product_id = %s
            ORDER BY sort_order ASC, image_id ASC
        \"\"\", (product_id,))
        images = cur.fetchall()

        if not images:
            images = [{'image_id': 0, 'image_path': product['primary_image'], 'is_primary': 1, 'sort_order': 1}]

        # Related perfumes from same collection or category
        cur.execute(\"\"\"
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count
            FROM v_perfume_catalog
            WHERE (collection_name = %s OR category_id = %s) AND product_id != %s AND is_active = 1
            ORDER BY RAND() LIMIT 4
        \"\"\", (product.get('collection_name'), product.get('category_id'), product_id))
        related_products = cur.fetchall()

        # Verified reviews
        cur.execute(\"\"\"
            SELECT r.rating, r.comment, r.created_at, u.full_name AS customer_name, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        \"\"\", (product_id,))
        reviews = cur.fetchall()

    return render_template('product_detail.html',
                           product=product,
                           images=images,
                           reviews=reviews,
                           related_products=related_products)"""

old_detail_norm = old_detail.replace("\r\n", "\n")
new_detail_norm = new_detail.replace("\r\n", "\n")

if old_detail_norm in content_norm:
    content_norm = content_norm.replace(old_detail_norm, new_detail_norm)
    print("4. Successfully updated product_detail() route.")
else:
    print("ERROR: old_detail not found in content!")

# 5. Update admin product add / edit to save perfume fields
old_admin_add_save = """                product_id = cur.lastrowid

                # Image upload handling"""

new_admin_add_save = """                product_id = cur.lastrowid

                # Save perfume details if provided
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
                          collection_name or 'Mainline Classics', is_featured, is_bestseller, is_new_arrival))

                # Image upload handling"""

old_admin_add_save_norm = old_admin_add_save.replace("\r\n", "\n")
new_admin_add_save_norm = new_admin_add_save.replace("\r\n", "\n")

if old_admin_add_save_norm in content_norm:
    content_norm = content_norm.replace(old_admin_add_save_norm, new_admin_add_save_norm, 1)
    print("5. Successfully updated admin_product_add() perfume details logic.")
else:
    print("ERROR: old_admin_add_save not found in content!")

# 6. Update admin_product_edit to update perfume details & fetch them on GET
old_admin_edit_save = """                cur.execute(
                    \"\"\"
                    UPDATE products 
                    SET category_id = %s, brand_id = %s, supplier_id = %s, name = %s, 
                        description = %s, price = %s, stock_quantity = %s, is_active = %s
                    WHERE product_id = %s
                    \"\"\",
                    (
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

new_admin_edit_save = """                cur.execute(
                    \"\"\"
                    UPDATE products 
                    SET category_id = %s, brand_id = %s, supplier_id = %s, name = %s, 
                        description = %s, price = %s, stock_quantity = %s, is_active = %s
                    WHERE product_id = %s
                    \"\"\",
                    (
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

old_admin_edit_save_norm = old_admin_edit_save.replace("\r\n", "\n")
new_admin_edit_save_norm = new_admin_edit_save.replace("\r\n", "\n")

if old_admin_edit_save_norm in content_norm:
    content_norm = content_norm.replace(old_admin_edit_save_norm, new_admin_edit_save_norm, 1)
    print("6. Successfully updated admin_product_edit() save logic.")
else:
    print("ERROR: old_admin_edit_save not found in content!")

# 7. In admin_product_edit GET, join perfume details
old_admin_edit_get = """        cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cur.fetchone()"""

new_admin_edit_get = """        cur.execute(\"\"\"
            SELECT p.*, ppd.gender, ppd.concentration, ppd.bottle_size, ppd.fragrance_family,
                   ppd.top_notes, ppd.heart_notes, ppd.base_notes, ppd.collection_name,
                   ppd.is_featured, ppd.is_bestseller, ppd.is_new_arrival
            FROM products p
            LEFT JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
            WHERE p.product_id = %s
        \"\"\", (product_id,))
        product = cur.fetchone()"""

old_admin_edit_get_norm = old_admin_edit_get.replace("\r\n", "\n")
new_admin_edit_get_norm = new_admin_edit_get.replace("\r\n", "\n")

if old_admin_edit_get_norm in content_norm:
    content_norm = content_norm.replace(old_admin_edit_get_norm, new_admin_edit_get_norm, 1)
    print("7. Successfully updated admin_product_edit() GET fetch.")
else:
    print("ERROR: old_admin_edit_get not found in content!")

# Write back with original CRLF
with open("app/app.py", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm.replace("\n", "\r\n"))

print("app/app.py successfully transformed!")
