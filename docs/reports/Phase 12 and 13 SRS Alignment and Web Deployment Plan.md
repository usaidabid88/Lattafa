# Phase 12 and 13: SRS Alignment and Web Deployment Plan

Addendum to the Online Shopping Database roadmap (DBMS CEP, MUET). Put this file in the DOC folder next to the SRS and the earlier roadmap files. Phase 12 makes the project meet the SRS; Phase 13 puts it on the web.

## 1. Recommendation at a glance

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | Flask with Jinja templates, Bootstrap 5, small vanilla JavaScript, a PWA manifest | Already built in earlier phases; responsive; no rewrite needed |
| Backend | Flask 3 served by Gunicorn | Same code, production-grade server |
| Database | MySQL 8 (keep) | Views, triggers, stored procedures, transactions and roles are the core of the DBMS project and of the viva |
| Authentication | Flask-Login sessions, hashed passwords, CSRF protection, roles (customer, seller, staff, admin), plus a signed guest token | Meets guest checkout, saved carts and access control in the SRS |
| Payments | Payment adapter: cash on delivery and a simulated card/wallet gateway now; Safepay sandbox optional | Covers FR-06, FR-10, FR-11 without needing a real merchant account |
| Hosting for the demo | Render free web service plus Aiven free MySQL | Free, public HTTPS link, works with real MySQL |
| Fallback hosting | Small VPS running Docker Compose | No sleeping, full MySQL privileges, persistent disk |
| Domain, TLS, CDN | Cloudflare in front, managed TLS from the host | HTTPS everywhere and faster image delivery |
| Monitoring | Health endpoint, an uptime monitor, Sentry error tracking | Meets NFR-08 |
| CI/CD | GitHub repository, automatic deploy on push, tests in GitHub Actions | Repeatable releases and a safe rollback |

Free tiers change. Check each provider’s current pricing and limits page before relying on it.

## 2. Why keep Flask and MySQL

- The project’s marks and viva depend on the SQL objects you designed. Moving to another database or framework would throw that work away.
- Render’s managed databases are PostgreSQL and key-value only, so the MySQL database goes to a MySQL provider. MySQL-compatible services such as PlanetScale or TiDB limit or omit triggers and stored procedures, so avoid them unless you test your scripts first.
- Aiven runs genuine MySQL, which is why it is the first choice for the free database.

## 3. Architecture

```
Phone or desktop browser  (HTTPS link, QR code, installable PWA, shared links)
            |
   Cloudflare  (DNS, CDN, TLS)                      optional but recommended
            |
   Web service: Gunicorn + Flask
      pages for shoppers, sellers, staff, admin
      /health endpoint, read-only /api/v1 JSON
        |                |                    |
   MySQL 8          Image files          Payment adapter
   tables, views,   catalog images       cash on delivery
   triggers,        in the repo;         simulated gateway
   procedures,      uploads in           Safepay sandbox (optional)
   roles            object storage
```

## 4. Hosting options

| Option | What it is | Verified facts | Trade-offs |
| --- | --- | --- | --- |
| A. Free demo stack (start here) | Render free web service for the app; Aiven free MySQL for the database | Render free web services spin down after 15 minutes without traffic and take about a minute to wake; their local files are lost on restart or redeploy; they support custom domains and managed TLS; 750 free instance hours a month. Aiven’s free MySQL needs no credit card, has 1 GB RAM and 1 GB disk, runs indefinitely, keeps automated backups, may be shut down if unused, and is not aimed at production | Cost is zero. Wake-up delay on first visit; admin-uploaded images vanish unless stored outside the service; free terms can change |
| B. Small VPS with Docker Compose | One server running Caddy (automatic HTTPS), the Flask app and MySQL 8 with a persistent volume and nightly dumps | Typical small servers cost a few dollars a month (check current prices) | No sleeping, full MySQL privileges, images persist. Needs an international payment method and basic server administration |
| C. Managed database, paid | Same app host as A or B, with a paid managed MySQL | Aiven lists a Developer MySQL plan at 5 dollars a month on its pricing page | Fewer surprises than the free tier; small monthly cost |

**Plan:** start with A to get a public link quickly. The Dockerfile built in Phase 13A lets you move to B in about an hour if cold starts or database privileges cause trouble. Phase 13B tests this early.

Before the viva, open the site two minutes early so the free service is awake.

## 5. Stack details by layer

| Area | Details |
| --- | --- |
| Web framework | Flask 3; Blueprints per module (users, catalog, orders, support) so each member owns a clear part |
| Server | Gunicorn with 2 workers; app listens on the port the host provides; no debug mode in production |
| Database access | PyMySQL or mysql-connector with parameterized queries only; one least-privilege application user, never root or the admin account |
| Sessions and auth | Server-side sessions with secure, HttpOnly, SameSite cookies; passwords hashed with a modern algorithm (argon2 or scrypt); CSRF tokens on every form; login rate limiting |
| Guest token | Signed cookie that identifies a guest cart and guest order; merged into the account on login |
| Email | Any SMTP provider for order confirmation and password reset |
| Forms and validation | Server-side validation with clear, accessible error messages |
| Images | Catalog images committed in the repository; admin uploads sent to S3-compatible object storage (for example Cloudflare R2) or disabled on the free tier |
| Caching and speed | Far-future cache headers for static files, resized WebP or JPEG images, pagination, indexes already built in earlier phases |
| Monitoring | /health endpoint, uptime monitor on it, Sentry for exceptions, structured logs without personal data |
| Backups | Provider backups plus a scheduled mysqldump saved off-server; restore tested once |
| CI/CD | Repository on GitHub; tests run in GitHub Actions; the host deploys from the main branch |

## 6. Ways people can reach the site

1. A public HTTPS link that works in any phone or desktop browser.
2. A custom domain (optional) and a QR code for the report and slides.
3. An installable web app: a PWA manifest and service worker so shoppers can add it to the phone home screen, with an offline fallback page.
4. A read-only JSON API (/api/v1/products and /api/v1/categories) for future apps and for demos with Postman.
5. Open Graph tags so product links look good when shared in WhatsApp and social apps.
6. A local copy started with docker compose up as a backup if the internet fails during the viva.

## 7. Security checklist (supports NFR-01, NFR-02, AC-06.4, AC-06.5)

- HTTPS only, with HSTS and security headers (CSP, X-Content-Type-Options, frame protection).
- Secure cookie flags; CSRF protection; login rate limiting.
- Parameterized SQL everywhere; upload validation (type, size, renamed files).
- Passwords hashed; secrets only in environment variables; .env never committed.
- No card numbers stored. Use the simulated gateway or a hosted checkout from a real provider.
- App database user limited to what the app needs; MySQL roles from the earlier phases kept.
- Collect only needed fields (name, phone, address, city, email); privacy policy page; consent shown at registration and checkout.
- Demo data uses fake customers only. Do not put real personal data on the free-tier demo.

## 8. SRS gap analysis (what Phase 12 adds)

The SRS is the source of truth. Each row names what the project has after Phase 11 and what Phase 12 adds. Requirement IDs are from the SRS.

| SRS requirement | In the project now | Phase 12 adds |
| --- | --- | --- |
| FR-01, FR-08, FR-09, NFR-06, AC-01.x | Orders store only a total | Tables delivery\_rates (city or province, fee, min and max days) and tax\_rates; order columns subtotal, tax\_amount, delivery\_fee, total\_amount, expected\_delivery\_date; one procedure sp\_cart\_summary used both by the cart page and by sp\_place\_order so the shown total always equals the charged total |
| FR-02, AC-03.1 | Orders require a registered user | orders.user\_id nullable plus guest name, email and phone; carts.session\_token; checkout route that works without login; address copied into the order so later edits do not change history |
| FR-03, AC-08.1 to AC-08.3 | Cart tied to a user | Signed cart cookie for guests; sp\_merge\_carts on login; carts keep updated\_at for the abandoned-cart view |
| FR-04, NFR-04, AC-07.4 | Basic errors | Custom 400, 404 and 500 pages; friendly messages mapped from procedure error codes; the cart is marked converted only after the order commits, so a failure never loses it |
| FR-05, AC-04.1 | None | Expected delivery date shown at cart and order review, from delivery\_rates |
| FR-06, FR-10, FR-11, AC-02.x | payments table with a method | payment\_methods (enabled flag) and payment\_attempts (status, reference, failure reason); adapter with cash on delivery and a simulated gateway that can succeed, fail or cancel for demos; retry or change method |
| FR-07, UR-05 | None | Four-step progress indicator: cart, delivery, payment, review, then confirmation |
| FR-12, AC-04.3 | orders.status and shipments | order\_status\_history filled by a trigger, plus a customer tracking page |
| FR-13, AC-04.2 | addresses and shipments | Address snapshot on the order; courier and tracking number on the shipment |
| FR-14, AC-04.4, AC-04.5 | None | support\_tickets (type: delayed, damaged, wrong item, other; status; order; description) with a customer form and a staff queue |
| FR-15, AR-06 | Catalog and images (Phase 11) | alt\_text column on product\_images shown on every image |
| FR-16 | Registration exists | Keep to essential fields only |
| FR-17, FR-18, AC-06.1, AC-06.2 | suppliers table | Extend into sellers: business name, contact, address, store location, verification\_status (pending, verified, rejected), verified\_at, verified\_by; role seller and a MySQL role for it; admin verification page; only verified sellers’ products are listed |
| FR-19, AC-06.3 | None | Privacy, terms and returns pages; consent box with a stored timestamp |
| FR-20, FR-21, AC-08.4 to AC-08.6 | None | return\_requests (order item, reason, proof image, status, seller response, dates, refund method); status history trigger; customer status page; seller queue; view of requests left unanswered past a configurable number of days |
| NFR-03, AC-07.1 | Indexes and pagination | Image sizes and caching headers; Lighthouse and response-time checks against the target in SRS OI-07 |
| NFR-05, AC-05.x | Responsive Bootstrap | Playwright checks at phone and desktop widths across the browser list |
| NFR-08, AC-07.5 | None | Health endpoint, uptime monitor, Sentry |
| AR-01 to AR-05 | Partial | Labels on all inputs, keyboard focus order, contrast checks, error text announced to screen readers, text that scales; check with Lighthouse and axe |
| UR-06, UR-07 | None | Support link visible on every page; no pop-ups or ads in checkout |

The project already has an abandoned-carts view. Show it on the admin dashboard, since cart abandonment is the topic of the SRS.

## 9. Phase 12 roadmap: SRS alignment

Work in order. Update PROGRESS.md after each step and write viva notes for each member’s module.

- **12A Traceability.** Create docs/traceability.csv listing every SRS requirement and acceptance criterion with the table, page or test that will satisfy it. Done when no requirement is missing a target.
- **12B Database.** Back up first. Write sql/09\_srs\_alignment.sql (non-destructive, re-runnable) for the new tables, columns, procedures, triggers, views and roles from section 8. Done when it runs twice with no error and the existing flows still work.
- **12C Checkout.** Guest checkout, cart cookie and merge, cart summary with taxes, delivery fee and date, progress indicator, payment adapter, confirmation and error handling. Done when a guest and a registered customer can each complete an order, and a failed payment can be retried.
- **12D Support and trust.** Order tracking, delivery issue tickets, return and replacement requests, seller verification, policy pages, support link. Done when each has a working page and a database record.
- **12E Quality pass.** Accessibility, mobile and performance checks with screenshots saved to audits/screenshots/. Done when Lighthouse accessibility is at least 90 and no step breaks at 390 px width.
- **12F Verification.** A test sheet maps every AC-xx.y to a test, the result and the date. Update the ER diagram, report and viva notes. Done when every Must have acceptance criterion passes.

## 10. Phase 13 roadmap: deployment

- **13A Production-ready app.** Configuration from environment variables, debug off, strong secret key, pinned requirements.txt, Gunicorn start command, Dockerfile and docker-compose.yml, /health, logging, cookie flags, security headers, rate limits. Done when docker compose up runs the whole site locally.
- **13B Cloud database.** Create the Aiven MySQL service, create a least-privilege app user, run sql/01 to sql/09 in order, import the data from a dump, connect over TLS. Test that triggers, procedures, views and roles all work. If a privilege blocks any of them, switch to Option B. Done when the checkout, trigger and rollback tests pass against the cloud database.
- **13C Deploy the app.** Put the code in a private GitHub repository, create the Render web service from it, set environment variables, and deploy. Done when the public link loads and an order can be placed.
- **13D Images.** Catalog images ship in the repository; uploads go to object storage or are switched off. Done when product pages show images after a redeploy.
- **13E Domain and access.** Custom domain if wanted, Cloudflare DNS and TLS, www redirect, PWA manifest and service worker, Open Graph tags, QR code, read-only API. Done when the site installs on a phone and a shared link shows a preview.
- **13F Monitoring and backups.** Uptime monitor on /health, Sentry, scheduled backup, one restore test. Done when a deliberate error appears in Sentry and a restored copy opens.
- **13G Smoke test and demo.** Run the full test list on a phone and a desktop: guest checkout, registered checkout, payment failure and retry, tracking, ticket, return request, seller verification, admin dashboard. Write the demo script and a rollback plan (previous deploy and database restore). Done when the checklist is clean twice in a row.

## 11. Risks and caveats

- Free services sleep, change terms or shut down unused databases. Keep the Docker setup ready as a fallback.
- Real payment gateways need business onboarding. Use cash on delivery and the simulated gateway for the course; treat any sandbox as optional. No real money moves.
- Do not put real customer data on the demo. Use fake data and say so on the privacy page.
- Check that triggers, procedures and roles work on the cloud database early, not at the end.
- Product images belong to their stores; keep the educational-use note from Phase 11.

## 12. Starter prompt for Antigravity (Phase 12)

```
This is an existing DBMS project (Online Shopping, MySQL 8 + Flask), finished through Phase 11. Read everything in DOC/ first: the assignment, the earlier roadmaps, the SRS, and this Phase 12 and 13 file. The SRS is the source of truth.

Do Phase 12 only (12A to 12F), in order. After each step: update PROGRESS.md, add viva notes, show me how to verify, and wait for my go.

Rules: back up the database with mysqldump first; make all database changes in a new re-runnable script sql/09_srs_alignment.sql and never drop existing tables or delete orders, users or carts; parameterized SQL only; WHY comment on every new SQL object; keep credentials in .env; no invented facts; never say something works unless you ran it and showed the output; do not add features outside the SRS. First reply: confirm what you read, summarize 12A to 12F in 6 lines, list what you need from me, then wait.
```

After Phase 12 is verified, ask for the Phase 13 prompt.
