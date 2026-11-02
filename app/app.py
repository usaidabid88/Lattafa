"""
app.py – Main Flask Application for Online Shopping System
WHY: Provides the web interface (routes, session management, form handling) on
     top of the MySQL 8 database. All SQL uses parameterized queries (%s).
     Credentials loaded from .env via db.py. Passwords hashed with Werkzeug.
"""

import os
import functools
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash
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
    """Homepage with quick stats."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
        total_products = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM orders")
        total_orders = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'customer'")
        total_users = cur.fetchone()['cnt']
    return render_template('index.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users)


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

@app.route('/products')
def products():
    """Product listing with search and category filter."""
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', '', type=str)

    conn = get_db()
    with conn.cursor() as cur:
        # Get all categories for the filter dropdown
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        categories = cur.fetchall()

        # Build query with parameterized filters
        sql = """
            SELECT p.product_id, p.name, p.price, p.stock_quantity,
                   p.is_active, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = 1
        """
        params = []

        if q:
            sql += " AND (p.name LIKE %s OR p.description LIKE %s)"
            params.extend([f'%{q}%', f'%{q}%'])
        if category_id:
            sql += " AND p.category_id = %s"
            params.append(int(category_id))

        sql += " ORDER BY p.name"
        cur.execute(sql, params)
        products = cur.fetchall()

    return render_template('products.html',
                           products=products,
                           categories=categories,
                           q=q,
                           category_id=category_id)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Single product page with reviews."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, c.name AS category_name, s.name AS supplier_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.product_id = %s
        """, (product_id,))
        product = cur.fetchone()

        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('products'))

        cur.execute("""
            SELECT r.rating, r.comment, r.created_at, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        """, (product_id,))
        reviews = cur.fetchall()

    return render_template('product_detail.html',
                           product=product, reviews=reviews)


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
            SELECT p.product_id, p.name, c.name AS category_name,
                   p.price, p.stock_quantity, p.is_active
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_id
        """)
        products = cur.fetchall()
    return render_template('admin/products.html', products=products)


@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    """Add a new product."""
    conn = get_db()
    if request.method == 'POST':
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO products (category_id, supplier_id, name, description, "
                    "price, stock_quantity, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        int(request.form['category_id']),
                        int(request.form['supplier_id']),
                        request.form['name'].strip(),
                        request.form.get('description', '').strip(),
                        float(request.form['price']),
                        int(request.form['stock_quantity']),
                        1 if request.form.get('is_active') else 0
                    )
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

    return render_template('admin/product_form.html',
                           product=None, categories=categories,
                           suppliers=suppliers,
                           form_action=url_for('admin_product_add'))


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    """Edit an existing product."""
    conn = get_db()
    if request.method == 'POST':
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET category_id=%s, supplier_id=%s, name=%s, "
                    "description=%s, price=%s, stock_quantity=%s, is_active=%s "
                    "WHERE product_id=%s",
                    (
                        int(request.form['category_id']),
                        int(request.form['supplier_id']),
                        request.form['name'].strip(),
                        request.form.get('description', '').strip(),
                        float(request.form['price']),
                        int(request.form['stock_quantity']),
                        1 if request.form.get('is_active') else 0,
                        product_id
                    )
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

    return render_template('admin/product_form.html',
                           product=product, categories=categories,
                           suppliers=suppliers,
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
