import os
import sqlite3
import mysql.connector
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "farm2home_secret_key_2026_secure"

# MySQL Connection Configuration (User can edit host, user, password)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'farm2home_db',
}

def get_db():
    """
    Database Connection helper:
    Tries MySQL first. If MySQL is configured and credentials match, connects to MySQL.
    Otherwise, gracefully falls back to local SQLite database (farm2home.db) for instant zero-config testing.
    """
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn, True
    except Exception as e:
        # Fallback to SQLite
        sqlite_db_path = os.path.join(app.root_path, 'farm2home.db')
        conn = sqlite3.connect(sqlite_db_path)
        conn.row_factory = sqlite3.Row
        init_sqlite_db(conn)
        return conn, False

def init_sqlite_db(conn):
    """
    Initialize SQLite Database schema and seed initial demo data if tables don't exist.
    """
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        unit TEXT NOT NULL DEFAULT 'kg',
        stock INTEGER NOT NULL DEFAULT 0,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        shipping_address TEXT NOT NULL,
        payment_method TEXT DEFAULT 'Cash on Delivery',
        order_status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'Pending'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        subject TEXT,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()

    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        default_pwd = generate_password_hash("admin123")
        farmer_pwd = generate_password_hash("farmer123")
        buyer_pwd = generate_password_hash("user123")

        cursor.executemany("""
        INSERT INTO users (id, full_name, email, password_hash, phone, address, role, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 'System Admin', 'admin@farm2home.com', default_pwd, '1234567890', 'Farm2Home HQ, Green City', 'admin', 'active'),
            (2, 'Ramesh Farmer', 'farmer@farm2home.com', farmer_pwd, '9876543210', 'Green Valley Farms, Sector 4', 'farmer', 'active'),
            (3, 'John Buyer', 'user@farm2home.com', buyer_pwd, '9123456780', 'Flat 402, Sunshine Apartments', 'user', 'active')
        ])

        cursor.executemany("""
        INSERT INTO categories (id, name, description, image_url) VALUES (?, ?, ?, ?)
        """, [
            (1, 'Fresh Vegetables', 'Organic and farm-fresh vegetables harvested daily.', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop'),
            (2, 'Fresh Fruits', 'Naturally ripened seasonal fruits rich in nutrition.', 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=600&auto=format&fit=crop'),
            (3, 'Dairy & Eggs', 'Pure farm milk, butter, cheese, and free-range eggs.', 'https://images.unsplash.com/photo-1528750997573-59b89d66f4f7?w=600&auto=format&fit=crop'),
            (4, 'Grains & Pulses', 'Unpolished natural grains, wheat, rice, and pulses.', 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop'),
            (5, 'Spices & Herbs', 'Aromatic handpicked spices and fresh garden herbs.', 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&auto=format&fit=crop')
        ])

        cursor.executemany("""
        INSERT INTO products (id, farmer_id, category_id, title, description, price, unit, stock, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 2, 1, 'Organic Tomatoes', 'Farm fresh vine-ripened red tomatoes without chemical pesticides.', 40.00, 'kg', 150, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop'),
            (2, 2, 1, 'Fresh Spinach (Palak)', 'Nutritious green spinach leaves freshly cut from the soil.', 25.00, 'bunch', 80, 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&auto=format&fit=crop'),
            (3, 2, 2, 'Farm Crisp Apples', 'Sweet and juicy apples direct from Himalayan orchards.', 120.00, 'kg', 100, 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop'),
            (4, 2, 3, 'Pure Cow Milk', 'Fresh unpasteurized whole cow milk delivered within hours of milking.', 60.00, 'liter', 50, 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&auto=format&fit=crop'),
            (5, 2, 4, 'Organic Brown Rice', 'High fiber unpolished traditional brown rice.', 90.00, 'kg', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop')
        ])

        cursor.execute("""
        INSERT INTO orders (id, user_id, total_amount, shipping_address, payment_method, order_status) VALUES (?, ?, ?, ?, ?, ?)
        """, (1, 3, 140.00, 'Flat 402, Sunshine Apartments, Green City', 'Cash on Delivery', 'Shipped'))

        cursor.executemany("""
        INSERT INTO order_items (id, order_id, product_id, farmer_id, quantity, price, status) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, 1, 1, 2, 2, 40.00, 'Shipped'),
            (2, 1, 4, 2, 1, 60.00, 'Shipped')
        ])

        conn.commit()

def query_db(query, args=(), one=False, commit=False):
    """Utility to execute SQL queries on MySQL or SQLite seamlessly."""
    conn, is_mysql = get_db()
    try:
        if is_mysql:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, args)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return last_id
            rv = cursor.fetchall()
            cursor.close()
            conn.close()
            return (rv[0] if rv else None) if one else rv
        else:
            # Replace MySQL placeholders `%s` with SQLite `?`
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                conn.close()
                return last_id
            rv = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return (rv[0] if rv else None) if one else rv
    except Exception as e:
        print(f"Database Query Error: {e}")
        if conn:
            conn.close()
        raise e

# Role Access Decorator
def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('login'))
            if session.get('user_role') != role_name:
                flash(f"Unauthorized access. Requires {role_name.capitalize()} privileges.", "danger")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Cart Utility Helper
def update_cart_count():
    cart = session.get('cart', {})
    session['cart_count'] = sum(cart.values())

# -----------------------------------------------------
# PUBLIC STOREFRONT ROUTES
# -----------------------------------------------------

@app.route("/")
def home():
    categories = query_db("SELECT * FROM categories ORDER BY id ASC LIMIT 6")
    featured_products = query_db("""
        SELECT p.*, c.name as category_name, u.full_name as farmer_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.farmer_id = u.id
        ORDER BY p.id DESC LIMIT 8
    """)
    update_cart_count()
    return render_template("index.html", categories=categories, products=featured_products)

@app.route("/products")
def products():
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('q', '').strip()

    sql = """
        SELECT p.*, c.name as category_name, u.full_name as farmer_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.farmer_id = u.id
        WHERE 1=1
    """
    params = []

    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)
    if search_query:
        sql += " AND (p.title LIKE %s OR p.description LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    sql += " ORDER BY p.id DESC"

    all_products = query_db(sql, params)
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")
    selected_cat = query_db("SELECT * FROM categories WHERE id = %s", [category_id], one=True) if category_id else None

    return render_template("products.html", products=all_products, categories=categories, selected_category=selected_cat, search_query=search_query)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = query_db("""
        SELECT p.*, c.name as category_name, u.full_name as farmer_name, u.address as farmer_address, u.phone as farmer_phone
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.farmer_id = u.id
        WHERE p.id = %s
    """, [product_id], one=True)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('products'))

    related_products = query_db("""
        SELECT p.*, c.name as category_name, u.full_name as farmer_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.farmer_id = u.id
        WHERE p.category_id = %s AND p.id != %s LIMIT 4
    """, [product['category_id'], product_id])

    return render_template("product_detail.html", product=product, related_products=related_products)

# -----------------------------------------------------
# CART & CHECKOUT ROUTES
# -----------------------------------------------------

@app.route("/cart")
def cart():
    cart_dict = session.get('cart', {})
    cart_items = []
    grand_total = 0.0

    if cart_dict:
        product_ids = list(cart_dict.keys())
        # Safe string building for IN clause
        placeholders = ','.join(['%s'] * len(product_ids))
        products = query_db(f"""
            SELECT p.*, c.name as category_name, u.full_name as farmer_name 
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN users u ON p.farmer_id = u.id
            WHERE p.id IN ({placeholders})
        """, product_ids)

        for p in products:
            qty = cart_dict.get(str(p['id']), cart_dict.get(p['id'], 0))
            subtotal = float(p['price']) * qty
            grand_total += subtotal
            cart_items.append({
                'product': p,
                'quantity': qty,
                'subtotal': subtotal
            })

    user_info = None
    if session.get('user_id'):
        user_info = query_db("SELECT * FROM users WHERE id = %s", [session['user_id']], one=True)

    return render_template("cart.html", cart_items=cart_items, grand_total=grand_total, user_info=user_info)

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    str_pid = str(product_id)

    cart[str_pid] = cart.get(str_pid, 0) + quantity
    session['cart'] = cart
    update_cart_count()
    flash("Item successfully added to your cart!", "success")
    return redirect(request.referrer or url_for('products'))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    cart = {}
    for key, value in request.form.items():
        if key.startswith('qty_'):
            pid = key.replace('qty_', '')
            qty = int(value)
            if qty > 0:
                cart[pid] = qty
    session['cart'] = cart
    update_cart_count()
    flash("Cart updated.", "info")
    return redirect(url_for('cart'))

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    str_pid = str(product_id)
    if str_pid in cart:
        del cart[str_pid]
        session['cart'] = cart
        update_cart_count()
        flash("Item removed from cart.", "info")
    return redirect(url_for('cart'))

@app.route("/checkout", methods=["POST"])
def checkout():
    if not session.get('user_id'):
        flash("Please log in or register to complete your order.", "warning")
        return redirect(url_for('login'))

    cart_dict = session.get('cart', {})
    if not cart_dict:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('products'))

    shipping_address = request.form.get('shipping_address', '').strip()
    payment_method = request.form.get('payment_method', 'Cash on Delivery')

    if not shipping_address:
        flash("Please enter a valid shipping address.", "danger")
        return redirect(url_for('cart'))

    # Calculate Total & Collect Items
    product_ids = list(cart_dict.keys())
    placeholders = ','.join(['%s'] * len(product_ids))
    db_products = query_db(f"SELECT * FROM products WHERE id IN ({placeholders})", product_ids)
    
    prod_map = {str(p['id']): p for p in db_products}
    grand_total = 0.0
    items_to_insert = []

    for pid_str, qty in cart_dict.items():
        if pid_str in prod_map:
            p = prod_map[pid_str]
            price = float(p['price'])
            grand_total += price * qty
            items_to_insert.append({
                'product_id': p['id'],
                'farmer_id': p['farmer_id'],
                'quantity': qty,
                'price': price
            })

    # Create Order
    order_id = query_db("""
        INSERT INTO orders (user_id, total_amount, shipping_address, payment_method, order_status)
        VALUES (%s, %s, %s, %s, 'Pending')
    """, [session['user_id'], grand_total, shipping_address, payment_method], commit=True)

    # Insert Order Items
    for item in items_to_insert:
        query_db("""
            INSERT INTO order_items (order_id, product_id, farmer_id, quantity, price, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        """, [order_id, item['product_id'], item['farmer_id'], item['quantity'], item['price']], commit=True)

    # Clear Cart
    session['cart'] = {}
    update_cart_count()
    flash(f"Order #{order_id} placed successfully! Thank you for supporting local farmers.", "success")
    return redirect(url_for('user_dashboard'))

# -----------------------------------------------------
# AUTHENTICATION ROUTES
# -----------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db("SELECT * FROM users WHERE email = %s", [email], one=True)

        if user and check_password_hash(user['password_hash'], password):
            if user['status'] != 'active':
                flash("Your account status is currently pending approval or suspended.", "danger")
                return redirect(url_for('login'))

            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash(f"Welcome back, {user['full_name']}!", "success")
            if user['role'] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))

        flash("Invalid email address or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        role = request.form.get('role', 'user')

        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('register'))

        existing_user = query_db("SELECT id FROM users WHERE email = %s", [email], one=True)
        if existing_user:
            flash("Email address is already registered. Please login.", "warning")
            return redirect(url_for('login'))

        pwd_hash = generate_password_hash(password)
        status = 'active' # Auto-activate for testing

        user_id = query_db("""
            INSERT INTO users (full_name, email, password_hash, phone, address, role, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [full_name, email, pwd_hash, phone, address, role, status], commit=True)

        # Auto Login
        session['user_id'] = user_id
        session['user_name'] = full_name
        session['user_email'] = email
        session['user_role'] = role

        flash("Registration successful! Welcome to Farm2Home.", "success")
        if role == 'farmer':
            return redirect(url_for('farmer_dashboard'))
        return redirect(url_for('user_dashboard'))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# -----------------------------------------------------
# FARMER DASHBOARD & ACTIONS
# -----------------------------------------------------

@app.route("/farmer/dashboard")
@role_required('farmer')
def farmer_dashboard():
    farmer_id = session['user_id']
    products = query_db("""
        SELECT p.*, c.name as category_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.farmer_id = %s ORDER BY p.id DESC
    """, [farmer_id])

    categories = query_db("SELECT * FROM categories ORDER BY name ASC")

    received_items = query_db("""
        SELECT oi.*, p.title as product_title, o.shipping_address, o.payment_method, o.created_at as order_date, u.full_name as buyer_name, u.phone as buyer_phone
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        JOIN users u ON o.user_id = u.id
        WHERE oi.farmer_id = %s ORDER BY oi.id DESC
    """, [farmer_id])

    total_sales = sum(float(item['price']) * item['quantity'] for item in received_items if item['status'] != 'Cancelled')
    pending_orders_count = sum(1 for item in received_items if item['status'] == 'Pending')

    return render_template("farmer_dashboard.html", 
                           products=products, 
                           categories=categories, 
                           received_items=received_items,
                           total_sales=total_sales,
                           pending_orders_count=pending_orders_count)

@app.route("/farmer/add_product", methods=["POST"])
@role_required('farmer')
def farmer_add_product():
    title = request.form.get('title', '').strip()
    category_id = request.form.get('category_id', type=int)
    price = request.form.get('price', type=float)
    unit = request.form.get('unit', 'kg').strip()
    stock = request.form.get('stock', type=int, default=0)
    description = request.form.get('description', '').strip()
    image_url = request.form.get('image_url', '').strip()

    if not image_url:
        image_url = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop'

    query_db("""
        INSERT INTO products (farmer_id, category_id, title, description, price, unit, stock, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, [session['user_id'], category_id, title, description, price, unit, stock, image_url], commit=True)

    flash(f"Product '{title}' added successfully!", "success")
    return redirect(url_for('farmer_dashboard'))

@app.route("/farmer/edit_product/<int:product_id>", methods=["POST"])
@role_required('farmer')
def farmer_edit_product(product_id):
    title = request.form.get('title', '').strip()
    category_id = request.form.get('category_id', type=int)
    price = request.form.get('price', type=float)
    unit = request.form.get('unit', 'kg').strip()
    stock = request.form.get('stock', type=int)
    description = request.form.get('description', '').strip()
    image_url = request.form.get('image_url', '').strip()

    query_db("""
        UPDATE products 
        SET title = %s, category_id = %s, price = %s, unit = %s, stock = %s, description = %s, image_url = %s
        WHERE id = %s AND farmer_id = %s
    """, [title, category_id, price, unit, stock, description, image_url, product_id, session['user_id']], commit=True)

    flash("Product updated successfully.", "success")
    return redirect(url_for('farmer_dashboard'))

@app.route("/farmer/delete_product/<int:product_id>", methods=["POST"])
@role_required('farmer')
def farmer_delete_product(product_id):
    query_db("DELETE FROM products WHERE id = %s AND farmer_id = %s", [product_id, session['user_id']], commit=True)
    flash("Product deleted.", "info")
    return redirect(url_for('farmer_dashboard'))

@app.route("/farmer/update_item_status/<int:item_id>", methods=["POST"])
@role_required('farmer')
def farmer_update_item_status(item_id):
    new_status = request.form.get('status')
    query_db("UPDATE order_items SET status = %s WHERE id = %s AND farmer_id = %s", [new_status, item_id, session['user_id']], commit=True)
    flash("Order item status updated.", "success")
    return redirect(url_for('farmer_dashboard'))

# -----------------------------------------------------
# USER / BUYER DASHBOARD
# -----------------------------------------------------

@app.route("/user/dashboard")
@role_required('user')
def user_dashboard():
    user_id = session['user_id']
    user_info = query_db("SELECT * FROM users WHERE id = %s", [user_id], one=True)

    user_orders = query_db("""
        SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC
    """, [user_id])

    # Fetch order items breakdown for user
    orders_data = []
    for o in user_orders:
        items = query_db("""
            SELECT oi.*, p.title as product_title, p.image_url, u.full_name as farmer_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN users u ON oi.farmer_id = u.id
            WHERE oi.order_id = %s
        """, [o['id']])
        orders_data.append({
            'order': o,
            'items': items
        })

    return render_template("user_dashboard.html", user_info=user_info, orders_data=orders_data)

# -----------------------------------------------------
# ADMIN DASHBOARD & MANAGEMENT
# -----------------------------------------------------

@app.route("/admin/dashboard")
@role_required('admin')
def admin_dashboard():
    total_users = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'user'", one=True)['count']
    total_farmers = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'farmer'", one=True)['count']
    total_products = query_db("SELECT COUNT(*) as count FROM products", one=True)['count']
    total_orders = query_db("SELECT COUNT(*) as count FROM orders", one=True)['count']
    total_revenue = query_db("SELECT SUM(total_amount) as rev FROM orders WHERE order_status != 'Cancelled'", one=True)['rev'] or 0.0

    all_users = query_db("SELECT * FROM users ORDER BY id DESC")
    all_categories = query_db("SELECT c.*, COUNT(p.id) as product_count FROM categories c LEFT JOIN products p ON c.id = p.category_id GROUP BY c.id ORDER BY c.id ASC")
    all_products = query_db("""
        SELECT p.*, c.name as category_name, u.full_name as farmer_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN users u ON p.farmer_id = u.id
        ORDER BY p.id DESC
    """)
    all_orders = query_db("""
        SELECT o.*, u.full_name as buyer_name 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
    """)
    contact_msgs = query_db("SELECT * FROM contact_messages ORDER BY id DESC")

    return render_template("admin_dashboard.html",
                           total_users=total_users,
                           total_farmers=total_farmers,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           users=all_users,
                           categories=all_categories,
                           products=all_products,
                           orders=all_orders,
                           contact_msgs=contact_msgs)

@app.route("/admin/toggle_user_status/<int:user_id>", methods=["POST"])
@role_required('admin')
def admin_toggle_user_status(user_id):
    current_user = query_db("SELECT status FROM users WHERE id = %s", [user_id], one=True)
    if current_user:
        new_status = 'suspended' if current_user['status'] == 'active' else 'active'
        query_db("UPDATE users SET status = %s WHERE id = %s", [new_status, user_id], commit=True)
        flash(f"User status changed to {new_status}.", "info")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/add_category", methods=["POST"])
@role_required('admin')
def admin_add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    image_url = request.form.get('image_url', '').strip()

    if not image_url:
        image_url = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600&auto=format&fit=crop'

    query_db("INSERT INTO categories (name, description, image_url) VALUES (%s, %s, %s)", [name, description, image_url], commit=True)
    flash(f"Category '{name}' created.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete_category/<int:cat_id>", methods=["POST"])
@role_required('admin')
def admin_delete_category(cat_id):
    query_db("DELETE FROM categories WHERE id = %s", [cat_id], commit=True)
    flash("Category removed.", "info")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/update_order_status/<int:order_id>", methods=["POST"])
@role_required('admin')
def admin_update_order_status(order_id):
    new_status = request.form.get('status')
    query_db("UPDATE orders SET order_status = %s WHERE id = %s", [new_status, order_id], commit=True)
    query_db("UPDATE order_items SET status = %s WHERE order_id = %s", [new_status, order_id], commit=True)
    flash(f"Order #{order_id} status updated to {new_status}.", "success")
    return redirect(url_for('admin_dashboard'))

# -----------------------------------------------------
# STATIC INFORMATIONAL PAGES
# -----------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        query_db("""
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, [name, email, subject, message], commit=True)

        flash("Thank you for reaching out! Our team will contact you shortly.", "success")
        return redirect(url_for('contact'))
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)