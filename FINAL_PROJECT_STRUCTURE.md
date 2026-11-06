# FINAL PROJECT STRUCTURE

**Project:** Online Shopping Database Management System (DBMS CEP)  
**Institution:** Mehran University of Engineering and Technology, Jamshoro  
**Phase:** Phase 4 — Perfume E-Commerce Domain Transformation (Haute Arabian Perfumery)  
**Status:** Completed & Verified (56/56 Tests Passed, 100% Pass Rate)  
**Architecture:** Python 3.11 + Flask 3 + MySQL 8 + PyMySQL + Jinja2 + Bootstrap 5 + Gunicorn + Docker  

---

```text
.
├── .env.example                                  # Canonical environment template (DB, Secret Key, SSL)
├── .gitignore                                    # Version control exclusion rules
├── Dockerfile                                    # Debian Python 3.11-slim production container image
├── docker-compose.yml                            # Stack orchestration (MySQL 8 + Flask web)
├── gunicorn_config.py                            # Production WSGI server settings (workers, timeout, bind)
├── requirements.txt                              # Pinned Python dependencies
│
├── README.md                                     # Project overview, examiner setup & quickstart guide
├── PROGRESS.md                                   # Master project checklist (Phases 0–12, Stages 1–3, Phase 4)
├── TASKS.md                                      # Task tracking board & execution milestone records
├── DECISIONS.md                                  # Architecture Decision Records (ADRs)
├── KNOWN_ISSUES.md                               # Platform constraints & retail notes
│
├── AUDIT_REPORT.md                               # Initial comprehensive independent project audit
├── AUDIT_REVIEW.md                               # Independent challenge & verification of audit report
├── STAGE_1_REPORT.md                             # Stage 1 Critical Remediation implementation report
├── STAGE_1_TEST_RESULTS.md                       # Stage 1 test logs & evidence
├── STAGE_1_CHANGELOG.md                          # Stage 1 itemized file modifications
├── STAGE_1_5_REPORT.md                           # Stage 1.5 Object reconciliation & secret hardening
├── STAGE_1_5_TEST_RESULTS.md                     # Stage 1.5 verification outputs
├── STAGE_1_5_CHANGELOG.md                        # Stage 1.5 itemized file modifications
├── STAGE_2_FILE_INVENTORY.md                     # Complete file inventory & classification
├── STAGE_2_CLEANUP_REPORT.md                     # Stage 2 cleanup actions & asset serving analysis
├── STAGE_2_CHANGELOG.md                          # Stage 2 itemized file modifications
├── STAGE_3_TEST_RESULTS.md                       # Stage 3 regression execution evidence (all suites)
├── STAGE_3_VERIFICATION_REPORT.md                 # Stage 3 verification & deployment readiness report
├── FINAL_DEPLOYMENT_READINESS.md                 # Final independent GO/NO-GO deployment verdict
├── FINAL_PROJECT_STRUCTURE.md                    # Final verified repository directory tree
│
├── PERFUME_TRANSFORMATION_PLAN.md                # Phase 4: Initial architecture & execution roadmap
├── PERFUME_DATABASE_DESIGN.md                    # Phase 4: Schema extension, 1:1 table & views
├── PERFUME_CATALOG.md                            # Phase 4: 100-perfume catalog documentation
├── PERFUME_CATALOG_DATA.csv                      # Phase 4: Raw researched dataset of all 100 perfumes
├── PERFUME_TRANSFORMATION_CHANGELOG.md           # Phase 4: Itemized code and schema changes
├── PERFUME_TRANSFORMATION_TEST_RESULTS.md        # Phase 4: Complete test matrix & Playwright logs
├── PERFUME_TRANSFORMATION_FINAL_REPORT.md        # Phase 4: Final executive & quantitative sign-off
│
├── run_test_suite.py                             # Test runner for 49-test unified regression suite
├── test_app.py                                   # 49-test unified Flask E2E integration test suite
├── test_perfume_suite.py                         # 7-test perfume domain transformation suite
├── test_secret_key.py                            # 7-test automated unit suite for Flask secret key
├── test_ssl_db.py                                # 6-test automated unit suite for database TLS/SSL
│
├── sql/                                          # Database DDL, Migrations & Test Assertions
│   ├── 01_schema.sql                             # Base relational schema (13 core tables)
│   ├── 02_sample_data.sql                        # Base sample data
│   ├── 03_views_indexes.sql                      # Base views & performance indexes
│   ├── 04_procedures_triggers.sql                # Stored procedures & stock/audit triggers
│   ├── 05_roles.sql                              # MySQL RBAC user roles & privilege grants
│   ├── 06_demo_queries.sql                       # Complex analytical queries
│   ├── 07_tests.sql                              # 25-assertion SQL verification suite
│   ├── 08_catalog_expansion.sql                  # Multi-image & brand schema expansion
│   ├── 09_srs_alignment.sql                      # Multi-vendor, SLA returns & guest carts
│   ├── 10_srs_alignment_fixes.sql                # Payment enum alignments
│   ├── 11_srs_final_alignment.sql                # Final procedures & view alignments
│   └── 12_perfume_transformation.sql             # Phase 4 schema extension & 100 perfume seeds
│
├── backups/                                      # Safe Recovery Snapshots
│   ├── pre_phase4_perfume_transformation_recovery.sql # 416KB MySQL 8.0 baseline dump
│   ├── pre_phase4_templates_backup/              # Preserved pre-transformation Jinja2 templates
│   └── pre_phase4_static_backup/                 # Preserved pre-transformation static assets
│
├── audits/                                       # Audit Evidence & Test Artifacts
│   └── evidence/
│       └── phase4/                               # 11 Playwright multi-viewport UI screenshots
│           ├── homepage_desktop_1280.png         # Desktop homepage layout
│           ├── catalog_desktop_1280.png          # Desktop fragrance catalog & filters
│           ├── collections_desktop_1280.png      # Desktop collections directory
│           ├── collection_khamrah_desktop_1280.png # Desktop Khamrah collection showcase
│           ├── product_detail_khamrah_desktop_1280.png # Desktop product flacon showcase
│           ├── olfactory_pyramid_desktop_1280.png # Desktop Top/Heart/Base notes accord card
│           ├── homepage_tablet_768.png           # Tablet homepage responsive layout
│           ├── product_detail_tablet_768.png     # Tablet product detail responsive layout
│           ├── homepage_mobile_390.png           # Mobile homepage responsive layout
│           ├── catalog_mobile_390.png            # Mobile catalog responsive layout
│           └── product_detail_mobile_390.png     # Mobile product detail responsive layout
│
├── app/                                          # Core Flask Application Package
│   ├── __init__.py                               # Package marker enabling root WSGI resolution
│   ├── app.py                                    # Main Flask routes, auth, session, cart, checkout, admin
│   ├── db.py                                     # Database connection helper with TLS/SSL & test routing
│   │
│   ├── scripts/                                  # Operational & Data Pipeline Scripts
│   │   ├── generate_perfume_catalog.py           # Catalog compiler for 100 genuine perfumes
│   │   ├── generate_perfume_assets.py            # SVG flacon vector illustration generator
│   │   └── check_endpoints.py                    # Template url_for validator
│   │
│   ├── templates/                                # 36 Accessible Jinja2 HTML Templates
│   │   ├── base.html                             # Master layout: Arabian luxury, Cinzel fonts, nav, footer
│   │   ├── index.html                            # 11-section luxury perfume storefront homepage
│   │   ├── products.html                         # Faceted catalog listing (gender, family, collection, sort)
│   │   ├── product_detail.html                   # Perfume showcase with Olfactory Pyramid accord card
│   │   ├── collections.html                      # Fragrance houses directory
│   │   ├── collection_detail.html                # Dedicated collection landing pages
│   │   ├── category.html                         # Filterable category browsing
│   │   ├── cart.html                             # Customer cart with sp_cart_summary single-source pricing
│   │   ├── checkout.html                         # 4-step atomic order checkout (guest & authenticated)
│   │   ├── payment_simulate.html                 # Payment gateway sandbox simulation
│   │   ├── payment_retry.html                    # Payment failure recovery & switch-to-COD interface
│   │   ├── order_confirmation.html               # Post-order confirmation with invoice breakdown
│   │   ├── my_orders.html                        # Customer order history listing
│   │   ├── order_detail.html                     # Itemized order invoice & status breakdown
│   │   ├── order_track.html                      # Live order status timeline from trigger history
│   │   ├── support.html                          # Customer support ticket lodging
│   │   ├── ticket_detail.html                    # Support ticket details and updates
│   │   ├── return_request.html                   # Return claim submission with photo upload
│   │   ├── return_detail.html                    # Return claim status & review
│   │   ├── returns_policy.html                   # Legal return and replacement policy
│   │   ├── privacy.html                          # Privacy policy with explicit consent
│   │   ├── terms.html                            # Terms of service
│   │   ├── login.html                            # Customer and administrative authentication form
│   │   ├── register.html                         # Customer account creation form
│   │   │
│   │   ├── admin/                                # Administrative Operations Views
│   │   │   ├── dashboard.html                    # Summary metrics & abandoned carts table
│   │   │   ├── orders.html                       # Order management & status transitions
│   │   │   ├── products.html                     # Fragrance catalog administration table
│   │   │   ├── product_form.html                 # Fragrance editor with olfactory note inputs
│   │   │   ├── reports.html                      # Analytical view aggregations
│   │   │   ├── sellers.html                      # Seller verification governance dashboard
│   │   │   └── overdue_returns.html              # SLA escalation queue for return claims
│   │   │
│   │   ├── seller/                               # Seller Multi-Vendor Views
│   │   │   └── returns.html                      # Vendor return claims queue & dispute interface
│   │   │
│   │   ├── staff/                                # Customer Support Staff Views
│   │   │   └── tickets.html                      # Support ticket triage queue
│   │   │
│   │   └── errors/                               # Branded HTTP Error Pages (No Stack Leaks)
│   │       ├── 400.html                          # Bad Request / CSRF error page
│   │       ├── 404.html                          # Not Found error page
│   │       └── 500.html                          # Internal Server Error page
│   │
│   └── static/                                   # Static Assets
│       └── images/
│           ├── branding/                         # Brandmark and logo SVGs
│           ├── hero/                             # Perfume hero banner SVG
│           ├── collections/                      # 7 collection banners
│           ├── categories/                       # 8 category cards
│           └── products/                         # 100 custom perfume flacon vector SVGs (perfume_101.svg .. perfume_200.svg)
```
