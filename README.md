# Farm2Home 🌾🏡

**Farm2Home** is a direct-from-farm marketplace web application that connects local farmers directly with consumers. By cutting out middle channels, Farm2Home ensures fresh organic produce for consumers and better profit margins for farmers.

---

## 🌟 Features

### 🛒 Customer / Public Storefront
- **Dynamic Catalog**: Browse fresh produce categorized by Vegetables, Fruits, Dairy, Grains, and Spices.
- **Search & Filter**: Filter products by category or keyword search.
- **Interactive Shopping Cart**: Add items, update quantities dynamically, and view subtotal calculations.
- **Order Checkout**: Seamless checkout experience with custom delivery address specification.
- **Customer Dashboard**: Track active and historic orders along with item fulfillment statuses.

### 🧑‍🌾 Farmer Panel
- **Product Management**: Add, update, or delete products, prices, stock quantities, and product images.
- **Fulfillment Tracker**: View customer orders containing their farm products and update fulfillment status (`Pending`, `Processing`, `Shipped`, `Delivered`, `Cancelled`).
- **Sales Analytics**: Real-time summary of total earnings and pending order counts.

### 🛡️ Admin Dashboard
- **System Overview**: Monitor total registered buyers, farmers, listed products, total orders, and gross revenue.
- **Category Control**: Create, update, or remove product categories.
- **User Management**: Activate or suspend user accounts (buyers and farmers).
- **Order Oversight**: Global order status management and contact message inbox.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- **Backend**: Python (Flask framework)
- **WSGI / Production Server**: Gunicorn
- **Database**: MySQL (Primary) with SQLite fallback (`farm2home.db`) for instant zero-config testing
- **Authentication & Security**: Flask Sessions, Werkzeug password hashing (`scrypt`/`pbkdf2`), Environment-controlled secrets

---

## 📁 Project Structure

```text
Farm2Home/
├── app.py                  # Main Flask application logic & routing
├── database.sql            # MySQL schema definition and seed data
├── farm2home.db            # SQLite zero-config local development database fallback
├── Procfile                # Production process starter for cloud hosting (Render/Heroku)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules for security
├── static/                 # Static assets and upload directories
│   └── imges/
└── templates/              # Jinja2 HTML templates
    ├── base.html
    ├── index.html
    ├── products.html
    ├── product_detail.html
    ├── cart.html
    ├── login.html
    ├── register.html
    ├── user_dashboard.html
    ├── farmer_dashboard.html
    ├── admin_dashboard.html
    ├── about.html
    └── contact.html
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/Farm2Home.git
cd Farm2Home
```

### 2. Create and Activate Virtual Environment
**Windows (PowerShell/CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables Setup

Create a `.env` file in the root directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to configure your environment:

```env
SECRET_KEY=your-custom-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=farm2home_db
DB_PORT=3306
FLASK_DEBUG=True
PORT=5000
```

---

## 🗄️ Database Setup (MySQL)

1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or MySQL CLI):
   ```bash
   mysql -u root -p
   ```

2. Execute the schema script:
   ```sql
   SOURCE database.sql;
   ```
   *Note: `database.sql` creates the database `farm2home_db`, sets up all tables with primary/foreign keys, and seeds demo data.*

3. *(Optional)* **Zero-Config Fallback**: If MySQL is not running or credentials are not provided, Farm2Home automatically falls back to `farm2home.db` (SQLite) so you can run and test the application instantly out of the box.

---

## 🚀 Running Locally

Start the development server:

```bash
python app.py
```

Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🔑 Demo & Recruiter Access Credentials

| Role | Email | Password |
|---|---|---|
| **System Admin** | `admin@farm2home.com` | `admin123` |
| **Farmer** | `farmer@farm2home.com` | `farmer123` |
| **Customer** | `user@farm2home.com` | `user123` |

---

## ☁️ Production Cloud Deployment (Render / Heroku)

### Deployment Configuration
1. **WSGI Server**: The repository includes `gunicorn` in `requirements.txt`.
2. **Start Command**: Set the startup command to:
   ```bash
   gunicorn app:app
   ```
   *(Or rely on the included `Procfile`)*.

3. **Cloud Environment Variables**: Set the following environment variables in your cloud hosting dashboard (e.g. Render Dashboard):
   - `SECRET_KEY`: A long, secure random string.
   - `DB_HOST`: Hostname of your Cloud MySQL database (e.g. Aiven, PlanetScale, AWS RDS).
   - `DB_USER`: Database username.
   - `DB_PASSWORD`: Database password.
   - `DB_NAME`: Database name (`farm2home_db`).
   - `DB_PORT`: Database port (usually `3306`).
   - `FLASK_DEBUG`: `False`

---

## 📸 Screenshots

*(Add project screenshots here)*

| Storefront | Farmer Dashboard | Admin Dashboard |
|---|---|---|
| ![Storefront](https://placehold.co/600x400?text=Farm2Home+Storefront) | ![Farmer Dashboard](https://placehold.co/600x400?text=Farmer+Dashboard) | ![Admin Dashboard](https://placehold.co/600x400?text=Admin+Dashboard) |

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
