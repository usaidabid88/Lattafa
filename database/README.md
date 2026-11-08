# Database Architecture & Migration Directory

This directory houses the structured relational database definitions, migrations, initial seed datasets, and analytical queries for the **LUXE FRAGRANCE / Online Shopping System** backed by **MySQL 8.0+**.

---

## 1. Directory Structure

```text
database/
├── schema/                 # Core DDL: tables, indexes, views, triggers, and RBAC
│   ├── 01_schema.sql       # Baseline schema DDL: users, roles, categories, products, orders, cart
│   ├── 03_views_indexes.sql# Reporting views & query performance indexes
│   ├── 04_procedures_triggers.sql # Stored procedures (atomic order placement) & audit triggers
│   └── 05_roles.sql        # Database users, roles, and principle of least privilege
│
├── seeds/                  # Baseline and domain catalog seed data
│   ├── 02_sample_data.sql  # Foundational sample accounts, categories, and inventory
│   ├── 08_catalog_expansion.sql # Extended e-commerce catalog baseline
│   └── 12_perfume_transformation.sql # 100 genuine luxury perfume products & olfactory pyramid notes
│
├── migrations/             # Incremental schema evolution and SRS alignment
│   ├── 09_srs_alignment.sql # Tracking, payments, tickets, returns schema expansion
│   └── 10_srs_alignment_fixes.sql # Procedure parameter fixes and SLA view enhancements
│
├── queries/                # Verification, demonstration, and audit scripts
│   ├── 06_demo_queries.sql # Business analytics and KPI demonstration queries
│   ├── 07_tests.sql        # Core relational constraint test harness
│   └── 11_tests.sql        # SRS compliance and audit verification queries
│
├── init_perfume/           # Sequential automated Docker container initialization (1 to 9)
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_views_indexes.sql
│   ├── 04_procedures_triggers.sql
│   ├── 05_roles.sql
│   ├── 06_catalog_expansion.sql
│   ├── 07_srs_alignment.sql
│   ├── 08_srs_alignment_fixes.sql
│   └── 09_perfume_transformation.sql
│
└── init_legacy/            # Preserved pre-perfume initialization scripts
    └── ...
```

---

## 2. Active Schemas & Environments

| Database Name | Environment | Purpose |
|---|---|---|
| `online_shop_perfume_dev` | Development & Local Server | Default active database for local Flask execution and browsing. |
| `online_shop_perfume_test` | Automated Testing Harness | Isolated test database strictly targeted by `run_test_suite.py` and `tests/`. |

---

## 3. Database Initialization

### Option A: Via Docker Compose (Recommended)
Docker automatically mounts `database/init_perfume` to `/docker-entrypoint-initdb.d:ro`. When the database container boots for the first time, all 9 scripts execute in alphabetical order:

```bash
docker compose up db -d
```

### Option B: Manual Local MySQL Initialization
To initialize or refresh a local MySQL database instance using the command line:

```bash
# 1. Connect and initialize development database
mysql -u root -p online_shop_perfume_dev < database/schema/01_schema.sql
mysql -u root -p online_shop_perfume_dev < database/seeds/02_sample_data.sql
mysql -u root -p online_shop_perfume_dev < database/schema/03_views_indexes.sql
mysql -u root -p online_shop_perfume_dev < database/schema/04_procedures_triggers.sql
mysql -u root -p online_shop_perfume_dev < database/schema/05_roles.sql
mysql -u root -p online_shop_perfume_dev < database/seeds/08_catalog_expansion.sql
mysql -u root -p online_shop_perfume_dev < database/migrations/09_srs_alignment.sql
mysql -u root -p online_shop_perfume_dev < database/migrations/10_srs_alignment_fixes.sql
mysql -u root -p online_shop_perfume_dev < database/seeds/12_perfume_transformation.sql

# 2. Replicate to isolated testing database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS online_shop_perfume_test;"
mysql -u root -p online_shop_perfume_test < database/init_perfume/01_schema.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/02_sample_data.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/03_views_indexes.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/04_procedures_triggers.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/05_roles.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/06_catalog_expansion.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/07_srs_alignment.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/08_srs_alignment_fixes.sql
mysql -u root -p online_shop_perfume_test < database/init_perfume/09_perfume_transformation.sql
```

---

## 4. Key Entities & Views

- **`products`**: Central product records with prices, stock, ratings, and category assignments.
- **`product_perfume_details`**: Olfactory metadata (top/heart/base notes, concentration, gender, flacon style, longevity, sillage).
- **`v_perfume_catalog`**: High-performance view joining product catalog with olfactory pyramid and primary asset mappings.
- **`v_order_tracking_timeline`**: Event timeline generated by triggers on order state transitions.
- **`sp_place_order` / `sp_place_guest_order`**: Atomic transactional procedures handling cart reservation, stock deduction, and order creation.
