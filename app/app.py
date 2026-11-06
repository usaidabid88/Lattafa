"""
app.py – Main Flask Application for Online Shopping System
WHY: Provides the web interface (routes, session management, form handling) on
     top of the MySQL 8 database. All SQL uses parameterized queries (%s).
     Credentials loaded from .env via db.py. Passwords hashed with Werkzeug.
"""

import os
import time
import shutil
import functools
import secrets
import datetime
import json
from decimal import Decimal
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

try:
    from app.db import get_connection
except ImportError:
    from db import get_connection

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

INSECURE_SECRET_PLACEHOLDERS = {
    'default_dev_key',
    'fallback-dev-secret-key',
    'change_this_to_a_random_string',
    'your_secret_key_here',
    'secret',
    'secret_key',
    'changeme',
    'admin',
    'password',
    '123456',
    'flask_secret_key',
    'muet-dbs-production-secret-2026',
    'muet_secret_key',
}

def resolve_app_environment():
    """Resolve active environment using APP_ENV, FLASK_ENV, or runtime indicators."""
    app_env = os.getenv('APP_ENV')
    if app_env:
        return app_env.strip().lower()
    flask_env = os.getenv('FLASK_ENV')
    if flask_env:
        return flask_env.strip().lower()
    if os.getenv('PRODUCTION', '0') == '1':
        return 'production'
    if os.getenv('TESTING', '0') == '1':
        return 'testing'
    return 'development'

def configure_secret_key(app_instance):
    """Configure cryptographically secure secret key with strict environment enforcement."""
    env = resolve_app_environment()
    raw_key = os.getenv('FLASK_SECRET_KEY', '').strip()

    if env == 'testing' or app_instance.config.get('TESTING'):
        app_instance.secret_key = raw_key or 'test-isolated-secret-key-for-test-suite-only-never-use-in-prod'
        return

    if env in ('production', 'prod'):
        if not raw_key:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: FLASK_SECRET_KEY is missing or empty in production mode. "
                "A cryptographically secure secret key (min 16 characters) must be set in the deployment environment."
            )
        lowered = raw_key.lower()
        if lowered in INSECURE_SECRET_PLACEHOLDERS or any(p in lowered for p in ('change_this', 'your_secret', 'placeholder')):
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: FLASK_SECRET_KEY is set to a known insecure placeholder. "
                "Provide a private, random secret key in production."
            )
        if len(raw_key) < 16:
            raise RuntimeError(
                f"CRITICAL SECURITY CONFIGURATION ERROR: FLASK_SECRET_KEY is too short ({len(raw_key)} chars) for "
                f"production. Minimum required length is 16 characters."
            )
        app_instance.secret_key = raw_key
        return

    # Development mode: use key from .env if present, otherwise generate secure ephemeral key
    if raw_key and raw_key.lower() not in INSECURE_SECRET_PLACEHOLDERS:
        app_instance.secret_key = raw_key
    else:
        app_instance.secret_key = secrets.token_hex(32)

app = Flask(__name__)
configure_secret_key(app)

# Initialize CSRF protection across all forms (Work Package A)
csrf = CSRFProtect(app)

# Production security configuration (Phase 13A)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
if resolve_app_environment() == 'production' or os.getenv('SESSION_COOKIE_SECURE', '0') == '1':
    app.config['SESSION_COOKIE_SECURE'] = True

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_db():
    """Return a per-request DB connection stored on Flask g."""
    if 'db' not in g:
        g.db = get_connection(database=app.config.get('DB_NAME'))
    return g.db


@app.teardown_appcontext
def close_db(exc):
    """Close DB connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: restrict to admin role."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') not in ('admin', 'staff'):
            flash('Access denied. Admin or staff privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_user():
    """Make session user data available to all templates."""
    return dict(
        logged_in='user_id' in session,
        current_user_id=session.get('user_id'),
        current_user_name=session.get('full_name'),
        current_role=session.get('role')
    )


# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Homepage for Arabian Luxury Perfumery with collections, bestsellers, new arrivals, and live stats."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
        total_products = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM orders")
        total_orders = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_users = cur.fetchone()['cnt']

        # Perfume Best Sellers
        cur.execute("""
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_bestseller = 1 AND is_active = 1
            ORDER BY avg_rating DESC, product_id DESC
            LIMIT 8
        """)
        best_sellers = cur.fetchall()
        if not best_sellers:
            cur.execute("""
                SELECT product_id, product_name, price, primary_image, brand_name,
                       concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
                FROM v_perfume_catalog
                WHERE is_active = 1
                ORDER BY product_id DESC
                LIMIT 8
            """)
            best_sellers = cur.fetchall()

        # Perfume New Arrivals
        cur.execute("""
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_new_arrival = 1 AND is_active = 1
            ORDER BY product_id DESC
            LIMIT 8
        """)
        new_arrivals = cur.fetchall()

        # Promotional & Gift Sets
        cur.execute("""
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count, stock_quantity
            FROM v_perfume_catalog
            WHERE is_featured = 1 AND is_active = 1
            ORDER BY price DESC
            LIMIT 4
        """)
        promotional_perfumes = cur.fetchall()

        # Featured Collections Matrix
        featured_collections = [
            {
                'name': 'Yara Collection',
                'slug': 'yara-collection',
                'subtitle': 'Sweet Gourmand & Ethereal Florals',
                'image': 'static/images/perfume/collection-yara.jpg',
                'count': 4
            },
            {
                'name': 'Asad Collection',
                'slug': 'asad-collection',
                'subtitle': 'Masculine Power & Noble Woods',
                'image': 'static/images/perfume/collection-asad.jpg',
                'count': 3
            },
            {
                'name': 'Khamrah Collection',
                'slug': 'khamrah-collection',
                'subtitle': 'Golden Spices & Date Gourmand',
                'image': 'static/images/perfume/collection-khamrah.jpg',
                'count': 3
            },
            {
                'name': 'Badee Al Oud',
                'slug': 'badee-al-oud',
                'subtitle': 'Royal Agarwood & Opulent Blends',
                'image': 'static/images/perfume/collection-oud.jpg',
                'count': 5
            },
            {
                'name': 'Lattafa Pride',
                'slug': 'lattafa-pride',
                'subtitle': 'Artisanal Haute Parfumerie',
                'image': 'static/images/perfume/collection-pride.jpg',
                'count': 11
            },
            {
                'name': 'Maison Alhambra',
                'slug': 'maison-alhambra',
                'subtitle': 'Parisian Chic with Arabian Depth',
                'image': 'static/images/perfume/collection-alhambra.jpg',
                'count': 30
            }
        ]

        # Perfume Gender Categories with accurate live perfume counts
        cur.execute("""
            SELECT c.category_id, c.name, c.slug, c.image_path, COUNT(p.product_id) AS count
            FROM categories c
            LEFT JOIN products p ON p.category_id = c.category_id AND p.is_active = 1
            WHERE c.slug IN ('men', 'women', 'unisex')
            GROUP BY c.category_id, c.name, c.slug, c.image_path
            ORDER BY c.category_id
        """)
        gender_categories = cur.fetchall()

        # Legacy department cards preserved for backward compatibility
        cur.execute("""
            SELECT category_id, category_name, category_slug, image_path, active_product_count
            FROM v_category_counts
            WHERE parent_category_id IS NULL AND category_slug != 'home-living'
            ORDER BY category_id
        """)
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
                           gender_categories=gender_categories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration with hashed password."""
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm_password']
        phone = request.form.get('phone', '').strip()

        if not full_name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (full_name, email, password_hash, phone, role) "
                    "VALUES (%s, %s, %s, %s, 'customer')",
                    (full_name, email, pw_hash, phone or None)
                )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            if 'Duplicate entry' in str(e):
                flash('An account with this email already exists.', 'danger')
            else:
                flash(f'Registration failed: {e}', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with password verification."""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, full_name, email, password_hash, role "
                "FROM users WHERE email = %s", (email,)
            )
            user = cur.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['full_name']
            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['role'] = user['role']

            # Merge anonymous guest cart into user's account cart (FR-03, AC-08.2)
            if session.get('cart_token'):
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "CALL sp_merge_carts(%s, %s, @p_merged_count)",
                            (session['cart_token'], user['user_id'])
                        )
                    conn.commit()
                    session.pop('cart_token', None)
                except Exception as merge_err:
                    conn.rollback()

            flash(f'Welcome back, {user["full_name"]}!', 'success')
            if user['role'] in ('admin', 'staff'):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('products'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear session and redirect to homepage."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─── PRODUCT CATALOG ──────────────────────────────────────────────────────────

# ─── PERFUME COLLECTION & NAVIGATION ROUTES ───────────────────────────────────

@app.route('/collections')
def collections_index():
    """Directory of all perfume collections with member counts and price ranges."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT collection_name, total_fragrances, min_price, max_price, avg_price
            FROM v_perfume_collections
            ORDER BY total_fragrances DESC
        """)
        collections = cur.fetchall()
    return render_template('collections.html', collections=collections)


@app.route('/collection/<slug>')
def collection_view(slug):
    """View all perfumes in a designated collection."""
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
        col_param = f"%{col_name}%"
        cur.execute("""
            SELECT * FROM v_perfume_catalog
            WHERE collection_name LIKE %s AND is_active = 1
            ORDER BY is_featured DESC, price ASC
        """, (col_param,))
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

@app.route('/category/<slug>')
def category_view(slug):
    """Category browsing page with sub-category chips, brand/price filters, sorting, and pagination."""
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    per_page = 12
    offset = (page - 1) * per_page

    brand_filter = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', '', type=str)
    max_price = request.args.get('max_price', '', type=str)
    sort_by = request.args.get('sort', 'newest').strip()
    search_q = request.args.get('q', '').strip()
    sub_slug = request.args.get('sub', '').strip()

    conn = get_db()
    with conn.cursor() as cur:
        # 1. Fetch current category details
        cur.execute("""
            SELECT category_id, name, slug, parent_category_id, image_path
            FROM categories
            WHERE slug = %s
        """, (slug,))
        current_cat = cur.fetchone()

        if not current_cat:
            abort(404)

        # 2. Determine hierarchy (top-level department vs child subcategory)
        if current_cat['parent_category_id'] is None:
            parent_cat = None
            cur.execute("""
                SELECT category_id, name, slug
                FROM categories
                WHERE parent_category_id = %s
                ORDER BY name
            """, (current_cat['category_id'],))
            subcategories = cur.fetchall()
            target_cat_ids = [current_cat['category_id']] + [s['category_id'] for s in subcategories]
        else:
            cur.execute("""
                SELECT category_id, name, slug
                FROM categories
                WHERE category_id = %s
            """, (current_cat['parent_category_id'],))
            parent_cat = cur.fetchone()

            cur.execute("""
                SELECT category_id, name, slug
                FROM categories
                WHERE parent_category_id = %s
                ORDER BY name
            """, (current_cat['parent_category_id'],))
            subcategories = cur.fetchall()
            target_cat_ids = [current_cat['category_id']]

        # If user clicked a sub-category chip while browsing top-level
        if sub_slug:
            cur.execute("SELECT category_id FROM categories WHERE slug = %s", (sub_slug,))
            sub_match = cur.fetchone()
            if sub_match:
                target_cat_ids = [sub_match['category_id']]

        # 3. Available brands for sidebar filter
        format_strings = ','.join(['%s'] * len(target_cat_ids))
        cur.execute(f"""
            SELECT DISTINCT b.brand_id, b.name AS brand_name, COUNT(p.product_id) AS product_count
            FROM products p
            JOIN brands b ON p.brand_id = b.brand_id
            WHERE p.is_active = 1 AND p.category_id IN ({format_strings})
            GROUP BY b.brand_id, b.name
            ORDER BY b.name
        """, target_cat_ids)
        available_brands = cur.fetchall()

        # 4. Build query on v_product_catalog
        where_clauses = ["is_active = 1"]
        params = []

        where_clauses.append(f"category_id IN ({format_strings})")
        params.extend(target_cat_ids)

        if brand_filter:
            where_clauses.append("brand_name = %s")
            params.append(brand_filter)

        if min_price:
            try:
                where_clauses.append("price >= %s")
                params.append(Decimal(min_price))
            except Exception:
                pass

        if max_price:
            try:
                where_clauses.append("price <= %s")
                params.append(Decimal(max_price))
            except Exception:
                pass

        if search_q:
            where_clauses.append("(product_name LIKE %s OR description LIKE %s)")
            params.extend([f"%{search_q}%", f"%{search_q}%"])

        where_sql = " AND ".join(where_clauses)

        # Count total matching products for pagination
        count_sql = f"SELECT COUNT(*) AS total FROM v_product_catalog WHERE {where_sql}"
        cur.execute(count_sql, params)
        total_products = cur.fetchone()['total']

        # Determine sorting
        if sort_by == 'price_asc':
            order_sql = "ORDER BY price ASC, product_id DESC"
        elif sort_by == 'price_desc':
            order_sql = "ORDER BY price DESC, product_id DESC"
        elif sort_by == 'rating':
            order_sql = "ORDER BY avg_rating DESC, review_count DESC, product_id DESC"
        else:
            order_sql = "ORDER BY product_id DESC"

        query_sql = f"""
            SELECT product_id, product_name, short_description, price, stock_quantity,
                   brand_name, category_name, category_slug, category_path,
                   primary_image, avg_rating, review_count, source_store
            FROM v_product_catalog
            WHERE {where_sql}
            {order_sql}
            LIMIT %s OFFSET %s
        """
        cur.execute(query_sql, params + [per_page, offset])
        products_list = cur.fetchall()

    total_pages = (total_products + per_page - 1) // per_page
    if total_pages == 0:
        total_pages = 1

    return render_template('category.html',
                           current_cat=current_cat,
                           parent_cat=parent_cat,
                           subcategories=subcategories,
                           sub_slug=sub_slug,
                           products=products_list,
                           available_brands=available_brands,
                           brand_filter=brand_filter,
                           min_price=min_price,
                           max_price=max_price,
                           sort_by=sort_by,
                           search_q=search_q,
                           page=page,
                           total_pages=total_pages,
                           total_products=total_products)


@app.route('/products')
def products():
    """Product listing with search, category filter, brand filter, gender, collection, family, and price sort."""
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
        sql = """
            SELECT product_id, product_name AS name, price, stock_quantity,
                   is_active, category_name, category_slug, brand_name,
                   primary_image, short_description, avg_rating, review_count,
                   gender, concentration, bottle_size, fragrance_family,
                   collection_name, is_featured, is_bestseller, is_new_arrival
            FROM v_perfume_catalog
            WHERE is_active = 1
        """
        params = []
        if q:
            sql += " AND (product_name LIKE %s OR description LIKE %s OR collection_name LIKE %s OR top_notes LIKE %s)"
            params.extend([f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'])
        else:
            # When browsing general perfume storefront catalog, display genuine perfume formulations (id >= 100)
            sql += " AND (product_id >= 100 OR collection_name IS NOT NULL)"
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
                           sort_by=sort_by)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Single perfume page with fragrance notes pyramid, collection specs, gallery, and reviews."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS supplier_name
            FROM v_perfume_catalog p
            JOIN products pr ON p.product_id = pr.product_id
            JOIN suppliers s ON pr.supplier_id = s.supplier_id
            WHERE p.product_id = %s
        """, (product_id,))
        product = cur.fetchone()

        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))

        # Get all images for this product (gallery)
        cur.execute("""
            SELECT image_id, image_path, is_primary, sort_order
            FROM product_images
            WHERE product_id = %s
            ORDER BY sort_order ASC, image_id ASC
        """, (product_id,))
        images = cur.fetchall()

        if not images:
            images = [{'image_id': 0, 'image_path': product['primary_image'], 'is_primary': 1, 'sort_order': 1}]

        # Related perfumes from same collection or category
        cur.execute("""
            SELECT product_id, product_name, price, primary_image, brand_name,
                   concentration, bottle_size, collection_name, avg_rating, review_count
            FROM v_perfume_catalog
            WHERE (collection_name = %s OR category_id = %s) AND product_id != %s AND is_active = 1
            ORDER BY RAND() LIMIT 4
        """, (product.get('collection_name'), product.get('category_id'), product_id))
        related_products = cur.fetchall()

        # Verified reviews
        cur.execute("""
            SELECT r.rating, r.comment, r.created_at, u.full_name AS customer_name, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        """, (product_id,))
        reviews = cur.fetchall()

    return render_template('product_detail.html',
                           product=product,
                           images=images,
                           reviews=reviews,
                           related_products=related_products)



def get_cart_id(conn, create_if_missing=False):
    """
    WHY: Discovers or creates active cart for authenticated customer or anonymous guest.
    Guest carts are tracked via cryptographically signed session['cart_token'] (FR-03, AC-08.1).
    """
    if 'user_id' in session:
        user_id = session['user_id']
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cart_id FROM carts WHERE user_id = %s AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1",
                (user_id,)
            )
            row = cur.fetchone()
            if row:
                return row['cart_id'], False
            if create_if_missing:
                cur.execute(
                    "INSERT INTO carts (user_id, status) VALUES (%s, 'active')",
                    (user_id,)
                )
                conn.commit()
                return cur.lastrowid, False
            return None, False
    else:
        token = session.get('cart_token')
        if not token:
            token = secrets.token_hex(24)
            session['cart_token'] = token

        with conn.cursor() as cur:
            cur.execute(
                "SELECT cart_id FROM carts WHERE session_token = %s AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1",
                (token,)
            )
            row = cur.fetchone()
            if row:
                return row['cart_id'], True
            if create_if_missing:
                cur.execute(
                    "INSERT INTO carts (user_id, session_token, status) VALUES (NULL, %s, 'active')",
                    (token,)
                )
                conn.commit()
                return cur.lastrowid, True
            return None, True


# ─── SHOPPING CART ────────────────────────────────────────────────────────────

@app.route('/cart')
def cart():
    """Display active cart with live pricing from sp_cart_summary (FR-01, FR-08, FR-09)."""
    conn = get_db()
    cart_id, is_guest = get_cart_id(conn, create_if_missing=False)

    selected_province = request.args.get('province', 'Sindh')
    selected_city = request.args.get('city', 'Karachi')

    items = []
    pricing = {
        'subtotal': Decimal('0.00'),
        'tax_amount': Decimal('0.00'),
        'delivery_fee': Decimal('0.00'),
        'total_amount': Decimal('0.00'),
        'min_days': 0,
        'max_days': 0
    }
    delivery_days_text = ""

    if cart_id:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ci.cart_id, ci.product_id, ci.quantity,
                       p.name AS product_name, p.price AS unit_price,
                       p.name, p.price, p.stock_quantity,
                       (ci.quantity * p.price) AS line_total
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
            """, (cart_id,))
            items = cur.fetchall()

            if items:
                cur.execute(
                    "CALL sp_cart_summary(%s, %s, %s, @p_subtotal, @p_tax, @p_fee, @p_total, @p_min, @p_max)",
                    (cart_id, selected_province, selected_city)
                )
                cur.execute("""
                    SELECT @p_subtotal AS subtotal, @p_tax AS tax_amount,
                           @p_fee AS delivery_fee, @p_total AS total_amount,
                           @p_min AS min_days, @p_max AS max_days
                """)
                summary = cur.fetchone()
                if summary and summary['subtotal'] is not None:
                    pricing = summary
                    min_d = int(pricing['min_days'])
                    max_d = int(pricing['max_days'])
                    delivery_days_text = f"{min_d} to {max_d} business days"

    cart_total = pricing['total_amount']
    return render_template(
        'cart.html',
        items=items,
        cart_items=items,
        cart_total=cart_total,
        pricing=pricing,
        selected_province=selected_province,
        selected_city=selected_city,
        delivery_days_text=delivery_days_text,
        is_guest=is_guest
    )


@app.route('/cart/add', methods=['POST'])
def cart_add():
    """Add an item to the shopping cart (supports guests & authenticated customers)."""
    product_id = int(request.form['product_id'])
    quantity = int(request.form.get('quantity', 1))

    conn = get_db()
    try:
        cart_id, is_guest = get_cart_id(conn, create_if_missing=True)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
                (cart_id, product_id)
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    "UPDATE cart_items SET quantity = quantity + %s "
                    "WHERE cart_id = %s AND product_id = %s",
                    (quantity, cart_id, product_id)
                )
            else:
                cur.execute(
                    "INSERT INTO cart_items (cart_id, product_id, quantity) "
                    "VALUES (%s, %s, %s)",
                    (cart_id, product_id, quantity)
                )
            cur.execute("UPDATE carts SET updated_at = NOW() WHERE cart_id = %s", (cart_id,))
        conn.commit()
        flash('Item added to cart.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Could not add to cart: {e}', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
def cart_update():
    """Update quantity of a cart item."""
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    cart_id = int(request.form['cart_id'])

    conn = get_db()
    try:
        with conn.cursor() as cur:
            if quantity <= 0:
                cur.execute(
                    "DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s",
                    (cart_id, product_id)
                )
            else:
                cur.execute(
                    "UPDATE cart_items SET quantity = %s "
                    "WHERE cart_id = %s AND product_id = %s",
                    (quantity, cart_id, product_id)
                )
            cur.execute("UPDATE carts SET updated_at = NOW() WHERE cart_id = %s", (cart_id,))
        conn.commit()
        flash('Cart updated.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    """Remove an item from the cart."""
    product_id = int(request.form['product_id'])
    cart_id = int(request.form['cart_id'])

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s",
                (cart_id, product_id)
            )
            cur.execute("UPDATE carts SET updated_at = NOW() WHERE cart_id = %s", (cart_id,))
        conn.commit()
        flash('Item removed from cart.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('cart'))


# ─── CHECKOUT ─────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """
    Checkout page: supports both authenticated customers and guest checkout (FR-02, AC-03.1).
    Enforces mandatory terms consent (FR-19, AC-06.3) and sp_cart_summary parity (NFR-06).
    """
    conn = get_db()
    cart_id, is_guest = get_cart_id(conn, create_if_missing=False)

    if not cart_id:
        flash('Your cart is empty. Add products before checking out.', 'warning')
        return redirect(url_for('products'))

    selected_province = request.args.get('province', 'Sindh')
    selected_city = request.args.get('city', 'Karachi')

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'cod')

        # Mandatory terms consent (FR-19, AC-06.3)
        if not request.form.get('consent_terms') and not request.form.get('address_id'):
            pass
        elif not request.form.get('consent_terms') and is_guest:
            flash('Please accept the Terms of Service and Privacy Policy to proceed.', 'danger')
            return redirect(url_for('checkout'))

        try:
            with conn.cursor() as cur:
                if 'user_id' in session:
                    # Authenticated checkout
                    address_id = int(request.form['address_id'])
                    cur.execute(
                        "CALL sp_place_order(%s, %s, %s, @p_order_id, @p_status_message)",
                        (session['user_id'], address_id, payment_method)
                    )
                else:
                    # Guest checkout (FR-02, AC-03.1)
                    token = session.get('cart_token', '')
                    g_name = request.form.get('guest_name', 'Guest Shopper').strip()
                    g_email = request.form.get('guest_email', 'guest@example.com').strip()
                    g_phone = request.form.get('guest_phone', '+92 300 0000000').strip()
                    g_address = request.form.get('guest_address', 'Main Road').strip()
                    g_city = request.form.get('guest_city', selected_city).strip()
                    g_prov = request.form.get('guest_province', selected_province).strip()

                    cur.execute(
                        "CALL sp_place_guest_order(%s, %s, %s, %s, %s, %s, %s, %s, @p_order_id, @p_status_message)",
                        (token, g_name, g_email, g_phone, g_address, g_city, g_prov, payment_method)
                    )

                cur.execute("SELECT @p_order_id AS order_id, @p_status_message AS msg")
                result = cur.fetchone()

            conn.commit()

            if result and result['order_id']:
                new_order_id = result['order_id']
                flash(result['msg'], 'success')

                # Route based on payment adapter
                if payment_method == 'simulated':
                    return redirect(url_for('payment_simulate', order_id=new_order_id))
                else:
                    return redirect(url_for('order_confirmation', order_id=new_order_id))
            else:
                flash(result['msg'] if result else 'Order placement aborted.', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Checkout failed: {e}', 'danger')

        return redirect(url_for('checkout'))

    # GET: Load items, calculate exact pricing via sp_cart_summary
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ci.product_id, ci.quantity,
                   p.name AS product_name, p.price AS unit_price,
                   p.name, p.price,
                   (ci.quantity * p.price) AS line_total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.product_id
            WHERE ci.cart_id = %s
        """, (cart_id,))
        items = cur.fetchall()

        if not items:
            flash('Your cart is empty. Add products before checking out.', 'warning')
            return redirect(url_for('products'))

        # Fetch pricing breakdown from sp_cart_summary
        cur.execute(
            "CALL sp_cart_summary(%s, %s, %s, @p_subtotal, @p_tax, @p_fee, @p_total, @p_min, @p_max)",
            (cart_id, selected_province, selected_city)
        )
        cur.execute("""
            SELECT @p_subtotal AS subtotal, @p_tax AS tax_amount,
                   @p_fee AS delivery_fee, @p_total AS total_amount,
                   @p_min AS min_days, @p_max AS max_days
        """)
        pricing = cur.fetchone()

        addresses = []
        if 'user_id' in session:
            cur.execute(
                "SELECT address_id, line1, line1 AS address_line1, city, province, postal_code, is_default "
                "FROM addresses WHERE user_id = %s ORDER BY is_default DESC",
                (session['user_id'],)
            )
            addresses = cur.fetchall()

    min_days = int(pricing['min_days']) if pricing else 2
    max_days = int(pricing['max_days']) if pricing else 5
    exp_date = (datetime.date.today() + datetime.timedelta(days=max_days)).strftime('%A, %d %B %Y')

    return render_template(
        'checkout.html',
        items=items,
        cart_items=items,
        cart_total=pricing['total_amount'] if pricing else 0.00,
        pricing=pricing,
        addresses=addresses,
        is_guest=is_guest,
        selected_province=selected_province,
        selected_city=selected_city,
        expected_delivery_date=exp_date
    )


# ─── PAYMENT ADAPTER & SIMULATION (FR-06, FR-10, FR-11, AC-02.x) ───────────────

@app.route('/payment/simulate/<int:order_id>')
def payment_simulate(order_id):
    """Simulated payment gateway sandbox with success, fail, and cancel testing controls."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.order_id, o.total_amount, o.status,
                   COALESCE(u.full_name, o.guest_name, 'Guest Customer') AS customer_name,
                   COALESCE(o.shipping_address_snapshot, o.guest_address_line1, 'Regional Address') AS shipping_destination
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()

    if not order:
        abort(404)

    return render_template('payment_simulate.html', order=order)


@app.route('/payment/process/<int:order_id>', methods=['POST'])
def payment_process(order_id):
    """Processes simulated gateway authorization outcomes (success, fail, cancel)."""
    action = request.form.get('action', 'success')
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("SELECT order_id, total_amount FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()

    if not order:
        abort(404)

    amount = order['total_amount']
    ts = int(time.time())

    try:
        with conn.cursor() as cur:
            if action == 'success':
                # Settle order and update payment status to completed
                cur.execute("UPDATE orders SET status = 'paid' WHERE order_id = %s", (order_id,))
                cur.execute(
                    "UPDATE payments SET status = 'completed', paid_at = NOW() WHERE order_id = %s",
                    (order_id,)
                )
                cur.execute("""
                    INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
                    VALUES (%s, 'simulated', %s, 'successful', %s, NULL)
                """, (order_id, amount, f'SIM-SUCCESS-{ts}-{order_id}'))
                conn.commit()
                flash('Payment authorized successfully. Your order is confirmed!', 'success')
                return redirect(url_for('order_confirmation', order_id=order_id))

            elif action == 'fail':
                # Log failed attempt without altering cart or cancelling order
                fail_reason = 'Card declined: Insufficient funds or invalid card details'
                cur.execute("""
                    INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
                    VALUES (%s, 'simulated', %s, 'failed', %s, %s)
                """, (order_id, amount, f'SIM-FAIL-{ts}-{order_id}', fail_reason))
                conn.commit()
                flash('Payment authorization failed: Card was declined.', 'danger')
                return redirect(url_for('payment_retry', order_id=order_id))

            else:  # cancel
                cancel_reason = 'Customer cancelled transaction at gateway'
                cur.execute("""
                    INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
                    VALUES (%s, 'simulated', %s, 'cancelled', %s, %s)
                """, (order_id, amount, f'SIM-CANCEL-{ts}-{order_id}', cancel_reason))
                conn.commit()
                flash('Payment transaction cancelled. You may retry or switch settlement method.', 'warning')
                return redirect(url_for('payment_retry', order_id=order_id))
    except Exception as e:
        conn.rollback()
        flash(f'Payment processing error: {e}', 'danger')
        return redirect(url_for('payment_simulate', order_id=order_id))


@app.route('/payment/retry/<int:order_id>')
def payment_retry(order_id):
    """Payment recovery page offering instant retry or COD fallback (FR-11, AC-02.2)."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.order_id, o.total_amount, o.status,
                   COALESCE(o.shipping_address_snapshot, o.guest_address_line1, 'Regional Address') AS shipping_destination
            FROM orders o WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()

        cur.execute("""
            SELECT failure_reason FROM payment_attempts 
            WHERE order_id = %s ORDER BY created_at DESC LIMIT 1
        """, (order_id,))
        last_attempt = cur.fetchone()

    if not order:
        abort(404)

    failure_reason = last_attempt['failure_reason'] if last_attempt else "Transaction unconfirmed."
    return render_template('payment_retry.html', order=order, failure_reason=failure_reason)


@app.route('/payment/switch-cod/<int:order_id>', methods=['POST'])
def payment_switch_cod(order_id):
    """Switch unpaid digital order to Cash on Delivery settlement (FR-11)."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE payments SET method = 'cod', status = 'pending', paid_at = NULL 
                WHERE order_id = %s
            """, (order_id,))
            cur.execute("""
                INSERT INTO payment_attempts (order_id, payment_method, amount, status, transaction_ref, failure_reason)
                SELECT order_id, 'cod', total_amount, 'pending', CONCAT('COD-SWITCH-', UNIX_TIMESTAMP(), '-', order_id), NULL
                FROM orders WHERE order_id = %s
            """, (order_id,))
        conn.commit()
        flash('Payment settlement switched to Cash on Delivery. Order confirmed!', 'success')
        return redirect(url_for('order_confirmation', order_id=order_id))
    except Exception as e:
        conn.rollback()
        flash(f'Could not switch payment method: {e}', 'danger')
        return redirect(url_for('payment_retry', order_id=order_id))


@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Final order confirmation and receipt (Step 4 of checkout breadcrumb)."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.order_id, o.order_date, o.subtotal, o.tax_amount, o.delivery_fee,
                   o.total_amount, o.status, o.expected_delivery_date,
                   o.shipping_address_snapshot, o.guest_name, o.guest_email, o.guest_phone,
                   o.guest_address_line1, o.guest_city, o.guest_province,
                   p.method AS payment_method, p.status AS payment_status
            FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            abort(404)

        cur.execute("""
            SELECT oi.product_id, oi.quantity, oi.unit_price,
                   (oi.quantity * oi.unit_price) AS line_total,
                   p.name AS product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()

    return render_template('order_confirmation.html', order=order, items=items)


# ─── ORDER TRACKING (FR-12, AC-04.3) ──────────────────────────────────────────

@app.route('/orders/<int:order_id>/track')
def order_track(order_id):
    """Customer self-service tracking page backed by order_status_history trigger audit."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.order_id, o.order_date, o.status, o.expected_delivery_date,
                   o.shipping_address_snapshot, o.total_amount, o.user_id, o.guest_email
            FROM orders o WHERE o.order_id = %s
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            flash(f'Order #{order_id} could not be located. Please verify your reference number.', 'warning')
            return redirect(url_for('track_order_lookup'))

        cur.execute("""
            SELECT courier, tracking_number, shipped_at, delivered_at
            FROM shipments WHERE order_id = %s
            ORDER BY shipment_id DESC LIMIT 1
        """, (order_id,))
        shipment = cur.fetchone() or {}

        cur.execute("""
            SELECT history_id, old_status, new_status, changed_by, notes, changed_at
            FROM order_status_history
            WHERE order_id = %s
            ORDER BY changed_at DESC, history_id DESC
        """, (order_id,))
        history = cur.fetchall()

    return render_template('order_track.html', order=order, shipment=shipment, history=history)


@app.route('/track-order', methods=['GET', 'POST'])
def track_order_lookup():
    """Allows guest and registered shoppers to look up order tracking securely."""
    if request.method == 'POST':
        order_id = request.form.get('order_id', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not order_id.isdigit():
            flash('Please enter a valid numeric Order ID.', 'warning')
            return render_template('order_track.html', order=None, history=[], shipment={})

        order_id_int = int(order_id)
        conn = get_db()
        with conn.cursor() as cur:
            if email:
                cur.execute("""
                    SELECT o.order_id
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.user_id
                    WHERE o.order_id = %s AND (LOWER(o.guest_email) = %s OR LOWER(u.email) = %s)
                """, (order_id_int, email, email))
            else:
                cur.execute("SELECT o.order_id FROM orders o WHERE o.order_id = %s", (order_id_int,))
            matched = cur.fetchone()

        if not matched:
            flash('No matching order was found for the details provided. Please check your confirmation email.', 'warning')
            return render_template('order_track.html', order=None, history=[], shipment={})

        return redirect(url_for('order_track', order_id=order_id_int))

    return render_template('order_track.html', order=None, history=[], shipment={})


# ─── ORDER HISTORY ────────────────────────────────────────────────────────────

@app.route('/my-orders')
@login_required
def my_orders():
    """Customer order history listing."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT order_id, order_date, status, total_amount
            FROM orders
            WHERE user_id = %s
            ORDER BY order_date DESC
        """, (session['user_id'],))
        orders = cur.fetchall()
    return render_template('my_orders.html', orders=orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """Single order detail page."""
    conn = get_db()
    with conn.cursor() as cur:
        # Only allow viewing own orders (unless admin/staff)
        if session.get('role') == 'customer':
            cur.execute(
                "SELECT * FROM orders WHERE order_id = %s AND user_id = %s",
                (order_id, session['user_id'])
            )
        else:
            cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()

        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('my_orders'))

        cur.execute("""
            SELECT oi.product_id, oi.quantity, oi.unit_price,
                   (oi.quantity * oi.unit_price) AS line_total,
                   p.name AS product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()

        cur.execute("SELECT * FROM payments WHERE order_id = %s", (order_id,))
        payment = cur.fetchone()

        cur.execute("SELECT * FROM shipments WHERE order_id = %s", (order_id,))
        shipment = cur.fetchone()

        cur.execute(
            "SELECT * FROM addresses WHERE address_id = %s",
            (order['address_id'],)
        )
        address = cur.fetchone()

        if address:
            order['address'] = f"{address['line1']}, {address['city']}, {address['province']} {address['postal_code']}"
        if payment:
            order['payment_method'] = payment['method']
            order['payment_status'] = payment['status']
            order['paid_at'] = payment['paid_at']
        if shipment:
            order['courier'] = shipment['courier']
            order['tracking_number'] = shipment['tracking_number']
            order['shipped_at'] = shipment['shipped_at']
            order['delivered_at'] = shipment['delivered_at']

    return render_template('order_detail.html',
                           order=order, items=items,
                           payment=payment, shipment=shipment,
                           address=address)


# ─── REVIEWS ──────────────────────────────────────────────────────────────────

@app.route('/review/add', methods=['POST'])
@login_required
def review_add():
    """Submit a product review (trigger enforces verified purchase)."""
    product_id = int(request.form['product_id'])
    rating = int(request.form['rating'])
    comment = request.form.get('comment', '').strip()

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reviews (user_id, product_id, rating, comment) "
                "VALUES (%s, %s, %s, %s)",
                (session['user_id'], product_id, rating, comment or None)
            )
        conn.commit()
        flash('Thank you for your review!', 'success')
    except Exception as e:
        conn.rollback()
        err = str(e)
        if 'Review Error' in err:
            flash('You can only review products you have purchased and received.', 'warning')
        elif 'Duplicate entry' in err:
            flash('You have already reviewed this product.', 'warning')
        else:
            flash(f'Could not submit review: {e}', 'danger')

    return redirect(url_for('product_detail', product_id=product_id))


# ─── ADMIN / STAFF ROUTES ────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with key metrics."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS total_sales
            FROM orders WHERE status IN ('paid', 'shipped', 'delivered')
        """)
        total_sales = cur.fetchone()['total_sales']

        cur.execute("SELECT COUNT(*) AS cnt FROM orders WHERE status = 'pending'")
        pending_orders = cur.fetchone()['cnt']

        cur.execute("SELECT COUNT(*) AS cnt FROM v_low_stock")
        low_stock = cur.fetchone()['cnt']

        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_customers = cur.fetchone()['cnt']

        # Query v_abandoned_carts for admin dashboard monitoring (SRS Topic Focus)
        cur.execute("""
            SELECT cart_id, customer_name, customer_email, customer_phone,
                   last_activity, days_idle, item_count, estimated_cart_value
            FROM v_abandoned_carts
            ORDER BY days_idle DESC
            LIMIT 10
        """)
        abandoned_carts = cur.fetchall()

    return render_template('admin/dashboard.html',
                           total_sales=total_sales,
                           pending_orders=pending_orders,
                           low_stock=low_stock,
                           total_customers=total_customers,
                           abandoned_carts=abandoned_carts)


@app.route('/admin/products')
@admin_required
def admin_products():
    """Product management listing."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.product_id, p.name, c.name AS category_name, b.name AS brand_name,
                   p.price, p.stock_quantity, p.is_active,
                   COALESCE(pi.image_path, 'static/images/placeholder.svg') AS primary_image,
                   ppd.concentration, ppd.bottle_size, ppd.gender, ppd.collection_name, ppd.fragrance_family
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
            LEFT JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
            ORDER BY p.product_id DESC
        """)
        products = cur.fetchall()
    return render_template('admin/products.html', products=products)


@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    """Add a new product with optional brand and image upload."""
    conn = get_db()
    if request.method == 'POST':
        try:
            brand_id = int(request.form['brand_id']) if request.form.get('brand_id') else None
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO products (category_id, brand_id, supplier_id, name, description, 
                                         price, stock_quantity, is_active) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        int(request.form['category_id']),
                        brand_id,
                        int(request.form['supplier_id']),
                        request.form['name'].strip(),
                        request.form.get('description', '').strip(),
                        float(request.form['price']),
                        int(request.form['stock_quantity']),
                        1 if request.form.get('is_active') else 0
                    )
                )
                product_id = cur.lastrowid

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
                    cur.execute("""
                        INSERT INTO product_perfume_details 
                        (product_id, gender, concentration, bottle_size, fragrance_family, 
                         top_notes, heart_notes, base_notes, collection_name, is_featured, is_bestseller, is_new_arrival)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        gender=VALUES(gender), concentration=VALUES(concentration), bottle_size=VALUES(bottle_size),
                        fragrance_family=VALUES(fragrance_family), top_notes=VALUES(top_notes), heart_notes=VALUES(heart_notes),
                        base_notes=VALUES(base_notes), collection_name=VALUES(collection_name),
                        is_featured=VALUES(is_featured), is_bestseller=VALUES(is_bestseller), is_new_arrival=VALUES(is_new_arrival)
                    """, (product_id, gender or 'Unisex', concentration or 'Eau de Parfum (EDP)', bottle_size or '100ml',
                          fragrance_family or 'Oriental', top_notes or '', heart_notes or '', base_notes or '',
                          collection_name or 'Mainline Classics', is_featured, is_bestseller, is_new_arrival))

                # Image upload handling
                file = request.files.get('image')
                if file and file.filename:
                    filename = secure_filename(file.filename).lower()
                    ext = os.path.splitext(filename)[1]
                    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
                        flash('Invalid image format. Allowed: JPG, PNG, WebP.', 'danger')
                        return redirect(request.url)

                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > 2 * 1024 * 1024:
                        flash('Image file exceeds maximum limit of 2 MB.', 'danger')
                        return redirect(request.url)

                    safe_name = f"admin-{product_id}-{int(time.time())}{ext}"
                    rel_path = f"static/images/products/uploads/{safe_name}"
                    root_dest = os.path.join(os.path.dirname(__file__), '..', rel_path)
                    app_dest = os.path.join(os.path.dirname(__file__), rel_path)
                    os.makedirs(os.path.dirname(root_dest), exist_ok=True)
                    os.makedirs(os.path.dirname(app_dest), exist_ok=True)
                    file.save(app_dest)
                    shutil.copyfile(app_dest, root_dest)

                    cur.execute(
                        "INSERT INTO product_images (product_id, image_path, is_primary, sort_order) VALUES (%s, %s, 1, 1)",
                        (product_id, rel_path)
                    )

            conn.commit()
            flash('Product added successfully.', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}', 'danger')

    with conn.cursor() as cur:
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        categories = cur.fetchall()
        cur.execute("SELECT supplier_id, name FROM suppliers ORDER BY name")
        suppliers = cur.fetchall()
        cur.execute("SELECT brand_id, name FROM brands ORDER BY name")
        brands = cur.fetchall()

    return render_template('admin/product_form.html',
                           product=None, categories=categories,
                           suppliers=suppliers, brands=brands,
                           form_action=url_for('admin_product_add'))


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    """Edit an existing product."""
    conn = get_db()
    if request.method == 'POST':
        try:
            brand_id = int(request.form['brand_id']) if request.form.get('brand_id') else None
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE products SET category_id=%s, brand_id=%s, supplier_id=%s, name=%s, 
                                        description=%s, price=%s, stock_quantity=%s, is_active=%s 
                    WHERE product_id=%s
                    """,
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
                    cur.execute("""
                        INSERT INTO product_perfume_details 
                        (product_id, gender, concentration, bottle_size, fragrance_family, 
                         top_notes, heart_notes, base_notes, collection_name, is_featured, is_bestseller, is_new_arrival)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        gender=VALUES(gender), concentration=VALUES(concentration), bottle_size=VALUES(bottle_size),
                        fragrance_family=VALUES(fragrance_family), top_notes=VALUES(top_notes), heart_notes=VALUES(heart_notes),
                        base_notes=VALUES(base_notes), collection_name=VALUES(collection_name),
                        is_featured=VALUES(is_featured), is_bestseller=VALUES(is_bestseller), is_new_arrival=VALUES(is_new_arrival)
                    """, (product_id, gender or 'Unisex', concentration or 'Eau de Parfum (EDP)', bottle_size or '100ml',
                          fragrance_family or 'Oriental', top_notes or '', heart_notes or '', base_notes or '',
                          collection_name or 'Mainline Classics', is_featured, is_bestseller, is_new_arrival))

                # Image upload handling
                file = request.files.get('image')
                if file and file.filename:
                    filename = secure_filename(file.filename).lower()
                    ext = os.path.splitext(filename)[1]
                    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
                        flash('Invalid image format. Allowed: JPG, PNG, WebP.', 'danger')
                        return redirect(request.url)

                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > 2 * 1024 * 1024:
                        flash('Image file exceeds maximum limit of 2 MB.', 'danger')
                        return redirect(request.url)

                    safe_name = f"admin-{product_id}-{int(time.time())}{ext}"
                    rel_path = f"static/images/products/uploads/{safe_name}"
                    root_dest = os.path.join(os.path.dirname(__file__), '..', rel_path)
                    app_dest = os.path.join(os.path.dirname(__file__), rel_path)
                    os.makedirs(os.path.dirname(root_dest), exist_ok=True)
                    os.makedirs(os.path.dirname(app_dest), exist_ok=True)
                    file.save(app_dest)
                    shutil.copyfile(app_dest, root_dest)

                    cur.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))
                    cur.execute(
                        "INSERT INTO product_images (product_id, image_path, is_primary, sort_order) VALUES (%s, %s, 1, 1)",
                        (product_id, rel_path)
                    )

            conn.commit()
            flash('Product updated successfully.', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}', 'danger')

    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, ppd.gender, ppd.concentration, ppd.bottle_size, ppd.fragrance_family,
                   ppd.top_notes, ppd.heart_notes, ppd.base_notes, ppd.collection_name,
                   ppd.is_featured, ppd.is_bestseller, ppd.is_new_arrival
            FROM products p
            LEFT JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
            WHERE p.product_id = %s
        """, (product_id,))
        product = cur.fetchone()
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        categories = cur.fetchall()
        cur.execute("SELECT supplier_id, name FROM suppliers ORDER BY name")
        suppliers = cur.fetchall()
        cur.execute("SELECT brand_id, name FROM brands ORDER BY name")
        brands = cur.fetchall()

    return render_template('admin/product_form.html',
                           product=product, categories=categories,
                           suppliers=suppliers, brands=brands,
                           form_action=url_for('admin_product_edit', product_id=product_id))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """All orders management listing."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.order_id, o.order_date, o.status, o.total_amount,
                   u.full_name AS customer_name
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.order_date DESC
        """)
        orders = cur.fetchall()
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/order/status', methods=['POST'])
@admin_required
def admin_order_status():
    """Update an order's status."""
    order_id = int(request.form['order_id'])
    new_status = request.form['new_status']

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET status = %s WHERE order_id = %s",
                (new_status, order_id)
            )
        conn.commit()
        flash(f'Order #{order_id} status updated to {new_status}.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('admin_orders'))


@app.route('/admin/order/cancel', methods=['POST'])
@admin_required
def admin_order_cancel():
    """Cancel an order using sp_cancel_order stored procedure."""
    order_id = int(request.form['order_id'])

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("CALL sp_cancel_order(%s, @msg)", (order_id,))
            cur.execute("SELECT @msg AS msg")
            result = cur.fetchone()
        conn.commit()

        if 'SUCCESS' in result['msg']:
            flash(result['msg'], 'success')
        else:
            flash(result['msg'], 'danger')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('admin_orders'))


@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Analytics reports using database views."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM v_sales_by_category")
        sales_by_category = cur.fetchall()

        cur.execute("SELECT * FROM v_low_stock")
        low_stock = cur.fetchall()

        cur.execute("SELECT * FROM v_best_sellers LIMIT 10")
        best_sellers = cur.fetchall()

        cur.execute("SELECT * FROM v_abandoned_carts")
        abandoned_carts = cur.fetchall()

    return render_template('admin/reports.html',
                           sales_by_category=sales_by_category,
                           low_stock=low_stock,
                           best_sellers=best_sellers,
                           abandoned_carts=abandoned_carts)


# ─── RUN ──────────────────────────────────────────────────────────────────────




# ─── CUSTOMER SUPPORT TICKETS (FR-14, AC-04.4, AC-04.5, UR-06) ────────────────

@app.route('/support', methods=['GET', 'POST'])
def support_page():
    """Customer support ticket filing form."""
    conn = get_db()
    if request.method == 'POST':
        c_name = request.form['contact_name'].strip()
        c_email = request.form['contact_email'].strip()
        c_phone = request.form.get('contact_phone', '').strip()
        order_id = request.form.get('order_id', '').strip()
        order_id = int(order_id) if order_id.isdigit() else None
        issue_type = request.form['issue_type']
        subject = request.form['subject'].strip()
        description = request.form['description'].strip()

        ticket_number = f"TCK-{int(time.time())}-{secrets.token_hex(2).upper()}"
        user_id = session.get('user_id')

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_tickets 
                    (ticket_number, order_id, user_id, contact_name, contact_email, contact_phone,
                     issue_type, subject, description, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'open')
                """, (ticket_number, order_id, user_id, c_name, c_email, c_phone, issue_type, subject, description))
                new_tck_id = cur.lastrowid
            conn.commit()
            flash(f'Support ticket {ticket_number} created successfully.', 'success')
            return redirect(url_for('ticket_detail', ticket_id=new_tck_id))
        except Exception as e:
            conn.rollback()
            flash(f'Error submitting ticket: {e}', 'danger')

    prefill_order_id = request.args.get('order_id', '')
    return render_template('support.html', prefill_order_id=prefill_order_id)


@app.route('/support/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    """View status and resolution notes of a customer support ticket."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM support_tickets WHERE ticket_id = %s", (ticket_id,))
        ticket = cur.fetchone()

    if not ticket:
        abort(404)

    return render_template('ticket_detail.html', ticket=ticket)


@app.route('/my-tickets')
@login_required
def my_tickets():
    """List support tickets submitted by current authenticated user."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ticket_id, ticket_number, order_id, issue_type, subject, status, created_at
            FROM support_tickets
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session['user_id'],))
        tickets = cur.fetchall()
    return render_template('staff/tickets.html', tickets=tickets)


@app.route('/staff/tickets')
@admin_required
def staff_tickets():
    """Staff triage queue for customer support tickets (AC-04.5)."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ticket_id, ticket_number, order_id, contact_name, contact_email,
                   issue_type, subject, description, status, staff_notes, created_at
            FROM support_tickets
            ORDER BY FIELD(status, 'open', 'in_progress', 'resolved', 'closed'), created_at DESC
        """)
        tickets = cur.fetchall()
    return render_template('staff/tickets.html', tickets=tickets)


@app.route('/staff/tickets/<int:ticket_id>/update', methods=['POST'])
@admin_required
def staff_ticket_update(ticket_id):
    """Staff updates ticket status and logs resolution notes."""
    new_status = request.form['status']
    notes = request.form.get('staff_notes', '').strip()

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE support_tickets 
                SET status = %s, staff_notes = %s, updated_at = NOW() 
                WHERE ticket_id = %s
            """, (new_status, notes, ticket_id))
        conn.commit()
        flash('Ticket updated successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to update ticket: {e}', 'danger')

    return redirect(url_for('staff_tickets'))


# ─── RETURN & REPLACEMENT CLAIMS (FR-20, FR-21, AC-08.4-6) ───────────────────

@app.route('/orders/<int:order_id>/return', methods=['GET', 'POST'])
def order_return_request(order_id):
    """Lodge a return or replacement request for an order item."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT order_id, status FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()

        if not order:
            abort(404)

        cur.execute("""
            SELECT oi.product_id, oi.quantity, oi.unit_price, p.name AS product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cur.fetchall()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        reason = request.form['reason']
        refund_method = request.form.get('refund_method', 'original_payment')
        description = request.form['description'].strip()

        proof_path = None
        if 'proof_image' in request.files:
            file = request.files['proof_image']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in ('jpg', 'jpeg', 'png', 'webp'):
                    sec_name = f"return_{order_id}_{int(time.time())}.{ext}"
                    root_save_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'returns')
                    app_save_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'returns')
                    os.makedirs(root_save_dir, exist_ok=True)
                    os.makedirs(app_save_dir, exist_ok=True)
                    full_save_app = os.path.join(app_save_dir, sec_name)
                    full_save_root = os.path.join(root_save_dir, sec_name)
                    file.save(full_save_app)
                    shutil.copyfile(full_save_app, full_save_root)
                    proof_path = f"static/images/returns/{sec_name}"

        return_number = f"RMA-{int(time.time())}-{secrets.token_hex(2).upper()}"
        user_id = session.get('user_id')

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO return_requests 
                    (return_number, order_id, product_id, user_id, reason, description, 
                     proof_image_path, status, refund_method)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'requested', %s)
                """, (return_number, order_id, product_id, user_id, reason, description, proof_path, refund_method))
                new_ret_id = cur.lastrowid
            conn.commit()
            flash(f'Return claim {return_number} submitted successfully.', 'success')
            return redirect(url_for('return_detail', return_id=new_ret_id))
        except Exception as e:
            conn.rollback()
            flash(f'Could not submit return claim: {e}', 'danger')

    return render_template('return_request.html', order=order, items=items)


@app.route('/returns/<int:return_id>')
def return_detail(return_id):
    """Customer view of a return claim and seller response."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.*, p.name AS product_name
            FROM return_requests r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.return_id = %s
        """, (return_id,))
        claim = cur.fetchone()

        if not claim:
            abort(404)

        cur.execute("""
            SELECT history_id, old_status, new_status, changed_by, notes, changed_at
            FROM return_status_history
            WHERE return_id = %s
            ORDER BY changed_at DESC
        """, (return_id,))
        history = cur.fetchall()

    return render_template('return_detail.html', claim=claim, history=history)


@app.route('/seller/returns')
@admin_required
def seller_returns():
    """Seller/Staff queue for reviewing return claims."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.return_id, r.return_number, r.order_id, r.product_id,
                   p.name AS product_name, r.reason, r.description,
                   r.proof_image_path, r.status, r.refund_method, r.seller_response, r.created_at
            FROM return_requests r
            JOIN products p ON r.product_id = p.product_id
            ORDER BY FIELD(r.status, 'requested', 'approved', 'item_returned', 'refunded', 'completed', 'rejected'), r.created_at DESC
        """)
        claims = cur.fetchall()
    return render_template('seller/returns.html', claims=claims)


@app.route('/seller/returns/<int:return_id>/update', methods=['POST'])
@admin_required
def seller_return_update(return_id):
    """Seller/Staff issues approval, rejection, or instructions on return claims."""
    new_status = request.form['status']
    response_note = request.form.get('seller_response', '').strip()

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE return_requests 
                SET status = %s, seller_response = %s, updated_at = NOW() 
                WHERE return_id = %s
            """, (new_status, response_note, return_id))
        conn.commit()
        flash('Return claim updated successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to update claim: {e}', 'danger')

    return redirect(url_for('seller_returns'))


@app.route('/admin/returns/overdue')
@admin_required
def admin_overdue_returns():
    """Displays return claims left unanswered past 3-day SLA via v_overdue_return_requests view (AC-08.6)."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM v_overdue_return_requests")
        overdue = cur.fetchall()
    return render_template('admin/overdue_returns.html', overdue=overdue)


# ─── SELLER VERIFICATION GOVERNANCE (FR-17, FR-18, AC-06.1-2) ──────────────────

@app.route('/admin/sellers')
@admin_required
def admin_sellers():
    """Admin dashboard listing all seller accounts and verification states."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM v_sellers ORDER BY seller_id")
        sellers = cur.fetchall()
    return render_template('admin/sellers.html', sellers=sellers)


@app.route('/admin/sellers/<int:seller_id>/verify', methods=['POST'])
@admin_required
def admin_seller_verify(seller_id):
    """Admin sets verification status to verified or rejected."""
    new_status = request.form['status']
    admin_name = session.get('user', 'admin')

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE suppliers 
                SET verification_status = %s, verified_at = NOW(), verified_by = %s 
                WHERE supplier_id = %s
            """, (new_status, admin_name, seller_id))
        conn.commit()
        flash(f'Seller #{seller_id} verification status changed to {new_status}.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Could not update seller verification: {e}', 'danger')

    return redirect(url_for('admin_sellers'))


# ─── LEGAL & POLICY PAGES (FR-19, AC-06.3) ───────────────────────────────────

@app.route('/privacy')
def privacy_policy():
    """Privacy policy page detailing academic data scope and non-storage of card data."""
    return render_template('privacy.html')


@app.route('/terms')
def terms_of_service():
    """Terms of service and acceptable academic use policy."""
    return render_template('terms.html')


@app.route('/returns-policy')
def returns_policy():
    """7-day buyer returns and replacement warranty policy."""
    return render_template('returns_policy.html')


# ─── OBSERVABILITY & HEALTH PROBE (NFR-08, AC-07.5) ───────────────────────────

@app.route('/health')
def health_check():
    """Health probe endpoint returning HTTP 200 JSON with database status (NFR-08, AC-07.5)."""
    conn = get_db()
    db_status = "connected"
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            cur.fetchone()
    except Exception as e:
        db_status = f"unhealthy: {e}"
        return jsonify({"status": "error", "database": db_status}), 500

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "service": "MUET Online Shopping System",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200


# ─── CUSTOM ERROR HANDLERS (FR-04, NFR-04, AC-07.4) ───────────────────────────

@app.errorhandler(400)
def bad_request_error(e):
    """Custom accessible 400 Bad Request error page."""
    return render_template('errors/400.html', error_message=str(e)), 400


@app.errorhandler(404)
def not_found_error(e):
    """Custom accessible 404 Not Found error page."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom accessible 500 Database / Internal Server Error page."""
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
