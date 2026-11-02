# DECISIONS.md - Autonomous Operational Log

This document records architectural, data, and design decisions made during the autonomous Phase 11 overnight run.

| Date / Time | Sub-Phase | Decision | Rationale |
| :--- | :--- | :--- | :--- |
| 2026-11-03 01:40 | 11A | Enforce single primary image via dual mechanism: Trigger (`SIGNAL 45000`) + Stored Procedure (`sp_set_product_primary_image`). | MySQL triggers throw Error 1442 if they mutate the same table invoked by the outer statement. Trigger guarantees constraint integrity; procedure performs safe transactional switching. |
| 2026-11-03 01:42 | 11A | Mapped existing 30 products into the new category hierarchy without deleting or moving existing foreign keys. | Guarantees 100% backward compatibility with existing orders, order items, and historic test assertions. |
| 2026-11-03 01:47 | 11B | Use Option B for image collection with automated polite fallback to styled SVG placeholder whenever a store rate-limits or protects endpoints. | Strict compliance with Phase 11 safety rules: never bypass captchas or bot protection; keep the application functional at all times. |
| 2026-11-03 01:52 | 11B | Upsert catalog items by product `name` rather than assuming fixed autoincrement `product_id`. | Preserves existing database rows, avoids ID collisions, and allows safe re-running of `import_catalog.py` without duplicate insertion. |
| 2026-11-03 01:56 | 11C | Generated local specimen fallback JPEG images alongside SVG placeholder when Pakistani store endpoints returned 403 or blocked bot headers. | Ensures all 51 manifest products have dedicated assets on disk in `static/images/products/<category-slug>/` so zero 404 image errors occur on detail and listing views. |
| 2026-11-03 02:00 | 11D | Roll up department product counts in `v_category_counts` using correlated subqueries for child categories. | Top-level department headers (`parent_category_id IS NULL`) accurately aggregate active product counts from all child subcategories rather than displaying 0. |
| 2026-11-03 02:04 | 11F | Validate image uploads in Flask via strict extension, MIME type, and max 2 MB file size checks, saving under sanitized timestamps in `static/images/uploads/`. | Mitigates arbitrary file upload and path traversal risks; updates both `products.image_url` and `product_images` atomically. |
| 2026-11-03 02:07 | 11G | Expanded `sql/07_tests.sql` with tests T11 through T15 and expanded `test_app.py` from 18 to 25 automated assertions. | Validates brand uniqueness, slug uniqueness, primary image trigger, primary image procedure, and cascade deletion at both database engine and web routing levels. |
