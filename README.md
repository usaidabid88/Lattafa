# LUXE FRAGRANCE — Haute Arabian Perfumery E-Commerce Platform
**Department of Software Engineering, Mehran University of Engineering and Technology (MUET)**  
**Course:** Database Management Systems (DBMS) — Complex Engineering Problem (CEP)  
**Curriculum Scope:** Fall 2024 / Semester 3 | **Instructor:** Engr. Aisha Ashfaque  
**Domain:** Luxury Arabian Fragrance Storefront & ACID Relational DBMS  

[![MySQL 8.0](https://img.shields.io/badge/Database-MySQL%208.0%20InnoDB-00758F?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Python 3.11](https://img.shields.io/badge/Backend-Python%203.11%20%7C%20Flask-3776AB?logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap%205%20%2B%20Custom%20CSS-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Tests Passed](https://img.shields.io/badge/Verification-69%2F69%20PASSED%20(100%25)-success)](#11-running-automated-tests)
[![Security Audited](https://img.shields.io/badge/Security-CSRF%20%7C%20RBAC%20%7C%20TLS-blue)](#4-security--architecture)

---

## 1. Project Introduction

**LUXE FRAGRANCE** is an enterprise-grade, relational e-commerce application transformed into a high-end Arabian perfume store demonstration inspired by the official **LATTAFA** brand experience. Originally developed as a multi-vendor marketplace, the system underwent a comprehensive architectural transformation to demonstrate advanced relational database engineering, ACID transaction isolation, and secure web application development.

The system manages a complete luxury fragrance catalog of **100 verified commercial products** across world-renowned Arabian perfume houses (*Lattafa Perfumes*, *Lattafa Pride*, and *Maison Alhambra*), featuring genuine olfactory pyramids (Top, Heart, and Base notes), custom-engineered procedural 1200×1500 product imagery, and comprehensive order lifecycle management.

---

## 2. Key Features

- **Normalized Fragrance Catalog (100 Fragrances)**:
  - 1:1 extension pattern (`product_perfume_details`) capturing fragrance families, concentrations (EDP, Extrait), volumes (100ml), longevity, and olfactory notes without altering baseline e-commerce tables.
  - Dedicated brand hubs for *Khamrah*, *Asad*, *Yara*, *Badee Al Oud*, and *Lattafa Pride*.
  - Strict inclusion and verification of all 17 mandatory academic specimen fragrances.
- **ACID Transactional Stored Procedures**:
  - `sp_place_order`: Multi-table atomic customer checkout enforcing stock deduction, order line items, and financial records within a single transaction boundary.
  - `sp_place_guest_order`: Anonymous checkout workflow supporting guest sessions.
  - `sp_cart_summary`: Real-time pricing calculations (subtotals, tax rates, shipping, net totals).
- **Automated Database Triggers & Audit Trail**:
  - `trg_orders_status_audit`: Immutable audit log recording all order status transitions with timestamps and actors.
  - `trg_after_order_item_insert_stock`: Atomic stock decrement upon purchase.
  - `trg_restore_stock_on_cancel`: Automatic inventory restoration upon order cancellation.
- **Role-Based Access Control (RBAC)**:
  - Strict role isolation separating Customers, Guests, Sellers, and Administrators.
  - Granular administrative dashboards for inventory control, seller approvals, and order tracking.
- **Procedural & Photorealistic Visual Pipeline**:
  - Dual asset generation pipeline producing high-resolution (1200×1500) WebP and JPEG flacon visuals with 12 archetypal bottle silhouettes, optical glass gradients, and authentic color palettes.
- **Enterprise Security**:
  - Flask-WTF CSRF protection across all forms and AJAX mutations.
  - Mandatory high-entropy secret key validation in production.
  - Remote database TLS/SSL enforcement for managed cloud databases.

---

## 3. Technology Stack

| Layer | Component | Specification |
|---|---|---|
| **Runtime** | Python | 3.11+ |
| **Framework** | Flask | 3.0.3 (WSGI Web Framework) |
| **Database** | MySQL Server | 8.0+ (InnoDB Engine, UTF8MB4) |
| **Database Driver** | PyMySQL | 1.1.1 (Pure-Python DB-API Client) |
| **Templates** | Jinja2 | Dynamic HTML templating with custom currency and text filters |
| **Styling** | Bootstrap 5.3 + Custom CSS | Luxury noir aesthetic: gold accents (`#D4AF37`), dark slate, Cinzel typography |
| **Security** | Flask-WTF / Werkzeug | CSRF token validation, PBKDF2:SHA256 password hashing |
| **Image Processing** | Pillow & resvg-py | 1200×1500 vector rendering and multi-format WebP/JPEG conversion |
| **Production WSGI** | Gunicorn | Multi-worker, threaded WSGI HTTP server |
| **Containerization** | Docker & Docker Compose | Multi-container microservices architecture (App + MySQL 8) |

---

## 4. Repository Directory Structure

```text
.
├── app/                        # Application package
│   ├── app.py                  # Core Flask application, route handlers, view functions
│   ├── db.py                   # Centralized PyMySQL connection & SSL/TLS helper
│   ├── __init__.py             # App package marker exporting Flask instance
│   ├── data/                   # Runtime data (manifests, cache)
│   ├── scripts/                # Backward-compatibility execution forwarders
│   ├── static/                 # Application static assets (CSS, JS, images)
│   └── templates/              # Jinja2 HTML templates organized by domain
│
├── database/                   # Structured MySQL 8 relational artifacts
│   ├── schema/                 # DDL: Tables, views, procedures, triggers, roles
│   ├── seeds/                  # Baseline seed datasets and 100-perfume catalog
│   ├── migrations/             # Incremental schema evolution and SRS alignment
│   ├── queries/                # Analytical KPI queries and SQL test scripts
│   ├── init_perfume/           # Sequential automated container bootstrap (01 to 09)
│   └── README.md               # Detailed database documentation and restore guides
│
├── tests/                      # Automated test harness (69 Tests)
│   ├── unit/                   # Unit test suites (Secret key security, SSL/TLS DB)
│   ├── integration/            # E2E regression suite & perfume domain test suite
│   ├── conftest.py             # Pytest fixtures and environment configuration
│   ├── run_test_suite.py       # Test harness executor
│   └── __init__.py
│
├── docs/                       # Comprehensive project documentation
│   ├── architecture/           # Architecture design records and decisions
│   ├── database/               # Database ER diagrams and schema specifications
│   ├── development/            # Developer setup guides and demonstration walkthroughs
│   ├── deployment/             # Cloud deployment readiness and production audits
│   ├── audits/                 # Comprehensive QA, code quality, and security audits
│   ├── reports/                # Academic reports, SRS test sheets, and milestones
│   └── project/                # Catalog specifications, task logs, and roadmap
│
├── scripts/                    # Standalone utility and automation scripts
│   ├── database/               # SQL migration generators and catalog importers
│   ├── development/            # Endpoint checkers and developer tooling
│   └── maintenance/            # Perfume asset and flacon rendering engines
│
├── data/                       # Active dataset files and manifests
│   ├── PERFUME_CATALOG_DATA.csv# 100 curated authentic perfumes with notes
│   ├── PERFUME_IMAGE_MANIFEST.json # Image metadata and silhouette mappings
│   └── products_manifest.csv   # Legacy baseline catalog manifest
│
├── static/                     # Primary static assets (mirrored with app/static)
│   ├── css/                    # Custom stylesheets and Bootstrap theme overrides
│   ├── js/                     # Client-side scripts (cart mutations, search)
│   └── images/                 # Product photography, SVGs, and category hero banners
│
├── archive/                    # Preserved historical assets and reports
├── backups/                    # Stage backups and database SQL dumps
├── .env.example                # Sanitized environment configuration template
├── .gitignore                  # Git tracking rules
├── docker-compose.yml          # Multi-container service definition
├── Dockerfile                  # Production Debian-slim container image definition
├── gunicorn_config.py          # Production WSGI process configuration
├── requirements.txt            # Locked Python package dependencies
├── run.py                      # Primary application local development entrypoint
├── run_test_suite.py           # Master automated test harness entrypoint
└── README.md                   # Authoritative repository documentation
```

---

## 5. Installation & Prerequisites

### Prerequisites
- **Python 3.11+** installed on host machine.
- **MySQL Server 8.0+** running locally (or Docker installed for containerized deployment).
- **Git** for version control.

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone <repository_url>
cd "DBS project"

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
source venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Environment Configuration

Copy `.env.example` to create your local `.env` configuration:

```bash
cp .env.example .env
```

Edit `.env` to supply your local MySQL database credentials:

```ini
# Database Connection Settings
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=online_shop_perfume_dev
TEST_DB_NAME=online_shop_perfume_test

# Application Environment (development, testing, or production)
APP_ENV=development
FLASK_DEBUG=1

# Secret Key (Auto-generated ephemeral key used in dev if left blank)
# In production, this MUST be a 64-character random hex string:
FLASK_SECRET_KEY=dev-secret-key-change-in-production

# Optional SSL CA certificate for cloud databases (e.g. AWS RDS, Aiven)
# DB_SSL_CA=/path/to/ca.pem
```

---

## 7. Database Initialization

The system requires two databases:
1. `online_shop_perfume_dev`: Active database for browsing, shopping, and administrative management.
2. `online_shop_perfume_test`: Isolated database used exclusively by the automated test harness.

### Automated Container Initialization (Docker)
Docker Compose will automatically execute all scripts in `database/init_perfume/` in sequential order:
```bash
docker compose up db -d
```

### Manual Local MySQL Initialization
Run the sequential initialization scripts against your local MySQL server:

```powershell
# 1. Create databases
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS online_shop_perfume_dev;"
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS online_shop_perfume_test;"

# 2. Populate development database
Get-ChildItem -Path "database/init_perfume/*.sql" | ForEach-Object {
    Write-Host "Executing $_.Name on dev..."
    Get-Content $_.FullName | mysql -u root -p online_shop_perfume_dev
}

# 3. Populate test database
Get-ChildItem -Path "database/init_perfume/*.sql" | ForEach-Object {
    Write-Host "Executing $_.Name on test..."
    Get-Content $_.FullName | mysql -u root -p online_shop_perfume_test
}
```

---

## 8. Running the Application

### Local Development Server
Execute the application entry point:

```bash
python run.py
```

The application will bind to `http://127.0.0.1:5000/`.

### Verified Navigation Routes
- **Storefront & Catalog**:
  - Homepage: `http://127.0.0.1:5000/`
  - All Perfumes: `http://127.0.0.1:5000/products`
  - Collections Hub: `http://127.0.0.1:5000/collections`
  - Specific Collection: `http://127.0.0.1:5000/collection/khamrah-collection`
  - Gender Landing Pages: `/men`, `/women`, `/unisex`
  - Discovery Hubs: `/bestsellers`, `/new-arrivals`
  - Product Detail: `http://127.0.0.1:5000/product/101`
- **Customer Shopping Flow**:
  - Shopping Cart: `http://127.0.0.1:5000/cart`
  - Checkout (Guest / User): `http://127.0.0.1:5000/checkout`
  - Live Order Tracking: `http://127.0.0.1:5000/orders/<order_id>/track`
- **Administrative Portals**:
  - Admin Dashboard: `http://127.0.0.1:5000/admin`
  - Product Catalog Management: `http://127.0.0.1:5000/admin/products`
  - Order Processing: `http://127.0.0.1:5000/admin/orders`
  - Analytical Reporting Views: `http://127.0.0.1:5000/admin/reports`
- **System Monitoring**:
  - Health Probe: `http://127.0.0.1:5000/health` (Returns JSON status: 200 OK)

---

## 9. Running Automated Tests

The test harness enforces 100% database isolation, executing strictly against `online_shop_perfume_test` and aborting immediately if pointed at development or production.

Execute the unified test suite:

```bash
python run_test_suite.py
```
*(Alternatively, execute directly from the test package: `python tests/run_test_suite.py`)*

### Test Suite Structure (69 Total Tests)

| Suite | Module Location | Tests | Focus Area |
|---|---|---|---|
| **Suite 1: E2E Regression** | `tests/integration/test_app.py` | 49 | CSRF protection, auth, cart merge, atomic checkout, RBAC, returns, order tracking, error handling |
| **Suite 2: Perfume Domain** | `tests/integration/test_perfume_suite.py` | 7 | 100 verified perfumes, 17 mandatory specimens, olfactory pyramids, faceted filtering |
| **Suite 3: Secret Key Security** | `tests/unit/test_secret_key.py` | 7 | Ephemeral dev keys, strict production entropy enforcement, invalid key rejection |
| **Suite 4: Database TLS/SSL** | `tests/unit/test_ssl_db.py` | 6 | Localhost unencrypted allowance, remote cloud TLS enforcement, certificate validation |
| **Total** | | **69** | **100% Passed (0 Failures, 0 Errors)** |

---

## 10. Docker Deployment

The application includes a production-ready, multi-container Docker configuration with healthchecks, non-root user execution, and persistent data volumes.

### Build and Start Stack
```bash
docker compose up --build -d
```

### Inspect Container Health
```bash
docker compose ps
```

### Stream Application Logs
```bash
docker compose logs -f web
```

### Stop Containers
```bash
docker compose down
```

---

## 11. Production Deployment & Security Notes

1. **WSGI Process Management**:
   In production environments (e.g. Render, Railway, AWS ECS, DigitalOcean), run the application via Gunicorn using the verified configuration:
   ```bash
   gunicorn --config gunicorn_config.py app.app:app
   ```
2. **Strict Production Environment Variables**:
   - `APP_ENV=production`
   - `FLASK_SECRET_KEY`: Set to a cryptographically strong 64-character hex string generated via:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
3. **Database TLS/SSL Configuration**:
   When connecting to remote managed MySQL instances (AWS RDS, Aiven, GCP Cloud SQL), set `DB_SSL_CA=/path/to/ca.pem` to ensure all transit traffic is encrypted. The application automatically enforces SSL connections in production mode when connecting to non-local hosts.

---

## 12. Authors & Acknowledgments

- **Department of Software Engineering**, Mehran University of Engineering and Technology (MUET), Jamshoro.
- **Complex Engineering Problem (CEP)** for Database Management Systems (DBMS).
- Academic Guidance: **Engr. Aisha Ashfaque**.
