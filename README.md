# LATTAFA — Haute Arabian Perfumery E-Commerce Platform
**Department of Software Engineering, Mehran University of Engineering and Technology (MUET)**  
**Course:** Database Management Systems (DBMS) — Complex Engineering Problem (CEP)  
**Semester:** Fall 2024 / Semester 3 | **Instructor:** Engr. Aisha Ashfaque  
**Domain Transformation:** Phase 4 — Arabian Perfume E-Commerce Experience  

[![MySQL 8.0](https://img.shields.io/badge/Database-MySQL%208.0%20InnoDB-00758F?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Python 3.11](https://img.shields.io/badge/Backend-Python%203.11%20%7C%20Flask-3776AB?logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap%205%20%2B%20Custom%20CSS-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Verification-56%2F56%20PASSED-success)](#automated-testing--verification)

---

## 1. Project Overview

This project implements a full-featured, relational e-commerce application transformed into a high-end Arabian perfume store demonstration inspired by the official **LATTAFA** shopping experience. 

Originally developed as a generic multi-vendor shop, the system underwent a comprehensive **Domain Transformation (Phase 4)** to showcase advanced database concepts, including:
- **Relational Integrity & 1:1 Extensions**: Normalized extension pattern (`product_perfume_details`) capturing olfactory pyramids, concentrations, and bottle volumes without altering baseline tables.
- **ACID Transaction Management**: Multi-table atomic checkout procedures (`sp_place_order` and `sp_place_guest_order`) enforcing stock deduction and financial settlement isolation.
- **Automated Triggers**: Inventory stock adjustments on order placement/cancellation and immutable audit logging on order state transitions.
- **Multi-Role Access Control (RBAC)**: Role separation between unregistered guests, authenticated shoppers, sellers, and system administrators.
- **Curated Fragrance Catalog**: 100 verified perfume products across major houses (*Khamrah*, *Asad*, *Yara*, *Badee Al Oud*, *Lattafa Pride*, *Maison Alhambra*) including all 17 mandatory academic specimens with authentic olfactory notes (Top, Heart, Base).

---

## 2. Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Language** | Python 3.11 | Application logic and transaction orchestration |
| **Backend Framework** | Flask 3.0.3 | Lightweight WSGI web framework |
| **Database Engine** | MySQL 8.0 (InnoDB) | ACID transactions, foreign keys, stored procedures, triggers |
| **Database Driver** | PyMySQL 1.1.1 | Python native DB-API connector |
| **Template Engine** | Jinja2 | Dynamic HTML rendering with custom filters |
| **Frontend Styling** | Bootstrap 5.3 + Custom CSS | Arabian luxury theme (Cinzel serif typography, gold accents, deep noir) |
| **Security** | Flask-WTF / CSRFProtect | Per-session CSRF protection and Werkzeug PBKDF2 password hashing |

---

## 3. Database Architecture & Design

### 3.1 Schema Summary
- **19 Total Tables**: `users`, `categories`, `brands`, `products`, `product_perfume_details`, `product_images`, `orders`, `order_items`, `payments`, `payment_attempts`, `order_status_history`, `reviews`, `addresses`, `cart_items`, `guest_carts`, `sellers`, `support_tickets`, `ticket_replies`, `order_returns`.
- **Primary Views**:
  - `v_perfume_catalog`: Consolidated catalog projection combining core product specs, brand provenance, flacon images, ratings, and olfactory attributes.
  - `v_perfume_collections`: Aggregations of volume, pricing range, and product counts per fragrance house.
  - `v_order_summary`: Detailed customer order metrics.
  - `v_abandoned_carts`: SLA monitoring for checkout recovery.
  - `v_overdue_return_requests`: Operational dispute resolution queue.
- **Stored Procedures**:
  - `sp_place_order`: Atomic customer checkout with inventory verification.
  - `sp_place_guest_order`: Frictionless guest checkout without account registration.
  - `sp_update_order_status`: Controlled state transition management with audit tracking.
  - `sp_cart_summary`: Real-time calculation of subtotal, sales tax, shipping fees, and item counts.
- **Triggers**:
  - `trg_orders_status_audit`: Automatically inserts an audit record whenever an order's status changes.
  - `trg_after_order_item_insert_stock`: Decrements warehouse inventory upon order confirmation.
  - `trg_restore_stock_on_cancel`: Restores reserved stock when an order is cancelled.

---

## 4. Quick Start & Local Demonstration

### Prerequisites
- Python 3.11+
- MySQL 8.0 Server running on `localhost:3306`

### 1. Environment Setup
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
The project defaults to the transformed development database `online_shop_perfume_dev`:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=online_shop_perfume_dev

FLASK_SECRET_KEY=muet-dbms-cep-2024-secret
FLASK_DEBUG=1
```

### 3. Database Initialization (If Not Already Imported)
```powershell
# The Docker Compose stack uses the perfume-specific bootstrap in sql/init_perfume/
docker compose up --build

# For an existing local MySQL instance, restore the dedicated perfume snapshot
# or run the files in sql/init_perfume/ in filename order.
# The final migration is sql/init_perfume/09_perfume_transformation.sql.
```

### 4. Run Automated Test Suites
```powershell
# Run the 49-test core regression suite
.\venv\Scripts\python.exe run_test_suite.py

# Run the 7-test perfume domain verification suite
.\venv\Scripts\python.exe test_perfume_suite.py
```

### 5. Launch Local Web Application
```powershell
.\venv\Scripts\python.exe app\app.py
```
Open your browser and navigate to:  
`http://127.0.0.1:5000`

---

## 5. Demonstration Accounts

| Role | Email Address | Password | Permissions |
|---|---|---|---|
| **System Administrator** | `admin@muetshop.pk` | `password123` | Full catalog, orders, and seller administration |
| **Registered Customer** | `zeeshan@gmail.com` | `password123` | Cart, checkout, order history, review submission |
| **Guest Shopper** | *(None required)* | *(None)* | Instant cookie cart, guest checkout, order tracking |

---

## 6. Project Documentation Index

| Document | Description |
|---|---|
| [`PERFUME_TRANSFORMATION_PLAN.md`](PERFUME_TRANSFORMATION_PLAN.md) | Initial architecture and execution roadmap for Phase 4 |
| [`PERFUME_DATABASE_DESIGN.md`](PERFUME_DATABASE_DESIGN.md) | Relational database schema extension, views, and data dictionaries |
| [`PERFUME_CATALOG.md`](PERFUME_CATALOG.md) | Full 100-perfume catalog documentation with notes and pricing |
| [`PERFUME_CATALOG_DATA.csv`](PERFUME_CATALOG_DATA.csv) | Machine-readable dataset of all 100 fragrance specimens |
| [`PERFUME_TRANSFORMATION_CHANGELOG.md`](PERFUME_TRANSFORMATION_CHANGELOG.md) | Step-by-step delta of schema, route, and template changes |
| [`PERFUME_TRANSFORMATION_TEST_RESULTS.md`](PERFUME_TRANSFORMATION_TEST_RESULTS.md) | Comprehensive 56-test execution matrix and Playwright evidence |
| [`PERFUME_TRANSFORMATION_FINAL_REPORT.md`](PERFUME_TRANSFORMATION_FINAL_REPORT.md) | Complete executive and technical transformation sign-off report |
| [`PROGRESS.md`](PROGRESS.md) | Historical task progress and milestone tracking |
| [`FINAL_PROJECT_STRUCTURE.md`](FINAL_PROJECT_STRUCTURE.md) | Full repository directory tree and asset index |

---

## 7. Academic Integrity & Non-Commercial Notice

This project was developed strictly for academic demonstration purposes as part of the Database Management Systems (DBMS) coursework at the Department of Software Engineering, Mehran University of Engineering and Technology (MUET), Jamshoro, Pakistan.

All brand names, product references, and trademarks (including *Lattafa*, *Yara*, *Asad*, *Khamrah*, *Badee Al Oud*, *Maison Alhambra*) remain the exclusive property of **Lattafa Perfumes Industries L.L.C.** No commercial affiliation, endorsement, or cloud deployment is claimed or authorized.
