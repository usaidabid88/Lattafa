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
from decimal import Decimal
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, abort, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from db import get_connection

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-dev-secret-key')


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_db():
    """Return a per-request DB connection stored on Flask g."""
    if 'db' not in g:
        g.db = get_connection()
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
    """Homepage with 5 department cards, featured specimen, and live stats."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
        total_products = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM orders")
        total_orders = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_users = cur.fetchone()['cnt']

        # 5 Department Cards from v_category_counts
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
                           departments=departments)


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
    """Product listing with search, category filter, brand filter, and price sort."""
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
        sql = """
            SELECT product_id, product_name AS name, price, stock_quantity,
                   is_active, category_name, category_slug, brand_name,
                   primary_image, short_description, avg_rating, review_count
            FROM v_product_catalog
            WHERE is_active = 1
        """
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
                           sort_by=sort_by)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Single product page with multi-image gallery, brand specs, and reviews."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, s.name AS supplier_name
            FROM v_product_catalog p
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
                           reviews=reviews)


# ─── SHOPPING CART ────────────────────────────────────────────────────────────

@app.route('/cart')
@login_required
def cart():
    """Display current user's active cart."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT cart_id FROM carts WHERE user_id = %s AND status = 'active' "
            "ORDER BY updated_at DESC LIMIT 1",
            (session['user_id'],)
        )
        cart_row = cur.fetchone()

        items = []
        cart_total = 0
        if cart_row:
            cur.execute("""
                SELECT ci.cart_id, ci.product_id, ci.quantity,
                       p.name AS product_name, p.price AS unit_price,
                       p.name, p.price, p.stock_quantity,
                       (ci.quantity * p.price) AS line_total
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
            """, (cart_row['cart_id'],))
            items = cur.fetchall()
            cart_total = sum(item['line_total'] for item in items)

    return render_template('cart.html', items=items, cart_items=items, cart_total=cart_total)


@app.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    """Add an item to the shopping cart."""
    product_id = int(request.form['product_id'])
    quantity = int(request.form.get('quantity', 1))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Find or create active cart
            cur.execute(
                "SELECT cart_id FROM carts WHERE user_id = %s AND status = 'active' "
                "ORDER BY updated_at DESC LIMIT 1",
                (session['user_id'],)
            )
            cart_row = cur.fetchone()
            if cart_row:
                cart_id = cart_row['cart_id']
            else:
                cur.execute(
                    "INSERT INTO carts (user_id, status) VALUES (%s, 'active')",
                    (session['user_id'],)
                )
                cart_id = cur.lastrowid

            # Check if item already in cart
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
        conn.commit()
        flash('Item added to cart.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Could not add to cart: {e}', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
@login_required
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
        conn.commit()
        flash('Cart updated.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('cart'))


@app.route('/cart/remove', methods=['POST'])
@login_required
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
        conn.commit()
        flash('Item removed from cart.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('cart'))


# ─── CHECKOUT ─────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page: calls sp_place_order stored procedure."""
    conn = get_db()

    if request.method == 'POST':
        address_id = int(request.form['address_id'])
        payment_method = request.form['payment_method']

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL sp_place_order(%s, %s, %s, @p_order_id, @p_status_message)",
                    (session['user_id'], address_id, payment_method)
                )
                cur.execute("SELECT @p_order_id AS order_id, @p_status_message AS msg")
                result = cur.fetchone()
            conn.commit()

            if result['order_id']:
                flash(result['msg'], 'success')
                return redirect(url_for('order_detail', order_id=result['order_id']))
            else:
                flash(result['msg'], 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Checkout failed: {e}', 'danger')

        return redirect(url_for('checkout'))

    # GET: load cart items and addresses for the form
    with conn.cursor() as cur:
        cur.execute(
            "SELECT cart_id FROM carts WHERE user_id = %s AND status = 'active' "
            "ORDER BY updated_at DESC LIMIT 1",
            (session['user_id'],)
        )
        cart_row = cur.fetchone()

        items = []
        cart_total = 0
        if cart_row:
            cur.execute("""
                SELECT ci.product_id, ci.quantity,
                       p.name AS product_name, p.price AS unit_price,
                       p.name, p.price,
                       (ci.quantity * p.price) AS line_total
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = %s
            """, (cart_row['cart_id'],))
            items = cur.fetchall()
            cart_total = sum(i['line_total'] for i in items)

        cur.execute(
            "SELECT address_id, line1, city, province, postal_code, is_default "
            "FROM addresses WHERE user_id = %s ORDER BY is_default DESC",
            (session['user_id'],)
        )
        addresses = cur.fetchall()

    if not items:
        flash('Your cart is empty. Add products before checking out.', 'warning')
        return redirect(url_for('products'))

    if not addresses:
        flash('Please add a delivery address before checking out.', 'warning')
        return redirect(url_for('checkout'))

    return render_template('checkout.html',
                           items=items, cart_items=items, cart_total=cart_total,
                           addresses=addresses)


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

    return render_template('admin/dashboard.html',
                           total_sales=total_sales,
                           pending_orders=pending_orders,
                           low_stock=low_stock,
                           total_customers=total_customers)


@app.route('/admin/products')
@admin_required
def admin_products():
    """Product management listing."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.product_id, p.name, c.name AS category_name, b.name AS brand_name,
                   p.price, p.stock_quantity, p.is_active,
                   COALESCE(pi.image_path, 'static/images/placeholder.svg') AS primary_image
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            LEFT JOIN product_images pi ON p.product_id = pi.product_id AND pi.is_primary = 1
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
        cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
