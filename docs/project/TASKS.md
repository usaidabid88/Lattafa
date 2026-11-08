# TASKS.md - Phase 12 & 13 Task Board

| Task ID | Description | Owner | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-12AB-VERIFY** | Verify 12A traceability matrix and 12B schema migration objects | AUDITOR | None | DONE (PASS) |
| **TASK-12C-GUEST-CART** | Guest session cookie token & atomic cart merge on login (`sp_merge_carts`) | CHECKOUT | TASK-12AB-VERIFY | DONE (PASS) |
| **TASK-12C-PRICING** | Single source pricing with `sp_cart_summary` (subtotal, tax, fee, delivery dates) | CHECKOUT | TASK-12C-GUEST-CART | DONE (PASS) |
| **TASK-12C-CHECKOUT-FLOW**| 4-step progress UI, guest & auth checkout, address snapshot, order confirmation | CHECKOUT | TASK-12C-PRICING | DONE (PASS) |
| **TASK-12C-PAYMENTS** | Payment adapter (COD & Simulated Gateway: success, fail, cancel, retry/change) | CHECKOUT | TASK-12C-CHECKOUT-FLOW | DONE (PASS) |
| **TASK-12C-ERRORS** | Friendly error mapping & custom error templates (400, 404, 500) | CHECKOUT | TASK-12C-PAYMENTS | DONE (PASS) |
| **TASK-12C-AUDIT** | Audit 12C checkout & pricing implementation | AUDITOR | TASK-12C-ERRORS | DONE (PASS) |
| **TASK-12D-TRACKING** | Customer order status tracking page with timeline from `order_status_history` | TRUST | TASK-12AB-VERIFY | DONE (PASS) |
| **TASK-12D-TICKETS** | Support tickets customer submission form & staff triage queue | TRUST | TASK-12D-TRACKING | DONE (PASS) |
| **TASK-12D-RETURNS** | Return & replacement claims, photo proof upload, seller queue & overdue SLA view | TRUST | TASK-12D-TICKETS | DONE (PASS) |
| **TASK-12D-SELLERS** | Seller verification dashboard (`/admin/sellers`) & catalog filter enforcement | TRUST | TASK-12D-RETURNS | DONE (PASS) |
| **TASK-12D-POLICIES** | Privacy, terms & returns pages, mandatory consent checkboxes & header/footer link | TRUST | TASK-12D-SELLERS | DONE (PASS) |
| **TASK-12D-ABANDONED** | Admin dashboard abandoned carts view integration (`v_abandoned_carts`) | TRUST | TASK-12D-POLICIES | DONE (PASS) |
| **TASK-12D-AUDIT** | Audit 12D trust, support & seller implementation | AUDITOR | TASK-12D-ABANDONED | DONE (PASS) |
| **TASK-12E-A11Y-MOBILE**| Accessibility audit (labels, contrast, touch targets, alt) & 390px/1280px screenshots | QUALITY | TASK-12C-AUDIT, TASK-12D-AUDIT | DONE (PASS) |
| **TASK-12F-TEST-SHEET** | Complete SRS acceptance criteria test sheet (`docs/srs_test_sheet.md`) | AUDITOR | TASK-12E-A11Y-MOBILE | DONE (PASS) |
| **TASK-12F-EXPAND-TESTS**| Comprehensive automated test additions in `sql/07_tests.sql` & `test_app.py` | AUDITOR | TASK-12F-TEST-SHEET | DONE (PASS) |
| **TASK-12F-DOCS** | Update ER diagram, FINAL_REPORT.md, and viva_notes.md | DOCS | TASK-12F-EXPAND-TESTS | DONE (PASS) |
| **TASK-13A-PROD** | Production readiness: Dockerfile, compose, /health, security headers, Gunicorn | LEAD | TASK-12F-DOCS | DONE (PASS) |
| **TASK-FINAL-REPORT** | Final comprehensive overnight `MORNING_REPORT.md` compilation | LEAD | ALL | DONE (PASS) |
| **TASK-STAGE1-PREFLIGHT** | Pre-flight dump recovery point & git inspection | LEAD | TASK-FINAL-REPORT | DONE (PASS) |
| **TASK-STAGE1-WPA-CSRF** | CSRF protection across 21 POST forms via Flask-WTF | SECURITY | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPB-TLS** | PyMySQL TLS/SSL support via DB_SSL_CA | DB_ENGINE | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPC-ISOLATION** | Test database isolation (`online_shop_test`) with safety guards | QA | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPD-WSGI** | Gunicorn root import path resolution (`app.app:app` & `app/__init__.py`) | DEVOPS | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPE-DOCKER-INIT** | Docker database init ordering (`sql/init/` 01-08 sequential) | DEVOPS | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPF-ROLES** | MySQL privilege compatibility (remove FLUSH PRIVILEGES;) | DB_ENGINE | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-WPG-RUNTIME** | Python runtime consistency (Dockerfile & requirements pinning) | DEVOPS | TASK-STAGE1-PREFLIGHT | DONE (PASS) |
| **TASK-STAGE1-VERIFY** | End-to-end test suite execution & Stage 1 reporting | LEAD | ALL_STAGE1 | DONE (PASS) |
| **TASK-STAGE1.5-WPA** | Database Object Count Reconciliation (49 vs 51 objects explained) | AUDITOR | TASK-STAGE1-VERIFY | DONE (PASS) |
| **TASK-STAGE1.5-WPB** | Production Secret Key Hardening & Verification (`test_secret_key.py`) | SECURITY | TASK-STAGE1-VERIFY | DONE (PASS) |
| **TASK-STAGE1.5-WPC** | Eradicate Hardcoded Credentials from Scripts & Docs | SECURITY | TASK-STAGE1-VERIFY | DONE (PASS) |
| **TASK-STAGE2-INVENTORY** | Complete 529-file repository audit & categorization (`STAGE_2_FILE_INVENTORY.md`) | AUDITOR | ALL_STAGE1.5 | DONE (PASS) |
| **TASK-STAGE2-CLEANUP** | Code quality polish, import cleanup, static parity & return upload path fix | LEAD | TASK-STAGE2-INVENTORY | DONE (PASS) |
| **TASK-STAGE2-IMAGE-PIPELINE** | Recover Option B `fetch_images.py` from `agent/image` branch | DEV | TASK-STAGE2-CLEANUP | DONE (PASS) |
| **TASK-STAGE2-STRUCTURE** | Purge 0-byte corrupt backup & freeze `FINAL_PROJECT_STRUCTURE.md` | DEVOPS | TASK-STAGE2-IMAGE-PIPELINE | DONE (PASS) |
| **TASK-STAGE2-REPORTS** | Author `STAGE_2_CLEANUP_REPORT.md` and `STAGE_2_CHANGELOG.md` | LEAD | TASK-STAGE2-STRUCTURE | DONE (PASS) |
| **TASK-STAGE3-REGRESSION** | Complete regression test run (49 app, 25 SQL, 7 key, 6 SSL = 87 tests) | QA | ALL_STAGE2 | DONE (PASS) |
| **TASK-STAGE3-CLEAN-INIT** | Pristine database initialization on disposable DB (`online_shop_stage3_verify`) | DB_ENGINE | TASK-STAGE3-REGRESSION | DONE (PASS) |
| **TASK-STAGE3-DEV-PRESERVE** | Verify zero modification or data drift on development DB (`online_shop`) | AUDITOR | TASK-STAGE3-CLEAN-INIT | DONE (PASS) |
| **TASK-STAGE3-DOCKER-VERIFY** | Docker daemon status verification & static container configuration check | DEVOPS | TASK-STAGE3-DEV-PRESERVE | DONE (BLOCKED/PASS) |
| **TASK-STAGE3-REPORTS** | Author `STAGE_3_TEST_RESULTS.md`, `STAGE_3_VERIFICATION_REPORT.md`, `FINAL_DEPLOYMENT_READINESS.md` | LEAD | ALL_STAGE3 | DONE (PASS) |
