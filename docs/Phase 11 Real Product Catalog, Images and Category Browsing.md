# Phase 11: Real Product Catalog, Images and Category Browsing

Addendum to the Online Shopping Database roadmap (DBMS CEP, MUET). Put this file in the DOC folder next to the assignment and the main roadmap, then give Antigravity the starter prompt.

## 1. Goal

Replace the placeholder sample products with a realistic catalog of about 80 products across 5 main categories, each with real product pictures, and make the web app feel like a real store where the customer picks a category and sees picture-based product cards.

**Done means:**

- At least 50 new products, each with a name, brand, category, approximate price in PKR, stock, short description and at least one image.
- Home page shows category cards with images; category pages show sub-category chips, filters and sorting.
- Product page shows an image gallery, brand, price, stock status and reviews.
- Existing orders, users and carts keep working (nothing destroyed).
- ER diagram, viva notes, demo queries and tests are updated for the new tables.

## 2. Rules for images and data (read this first)

- Product pictures and descriptions belong to the stores. This project is an educational demo, not a real shop. Do not publish the site publicly or sell anything.
- Store a `source_store` and `source_url` for every product and image so the origin is always traceable.
- Add a footer note in the app: "Product images and names belong to their respective stores and are used for educational demonstration only."
- Download images into the project (static/images/products/...). Do not hotlink to the store’s servers.
- Prices are approximate sample values. Write them in the manifest as the price seen on the day of copying, and say so in the report. Do not claim they are live prices.
- Do not bypass logins, bot protection, captchas or rate limits. If a site blocks an automated download, skip it and report it so the picture can be saved by hand.

## 3. Starter instructions for Antigravity

Copy this block as the master prompt for the phase.

```
You are continuing a finished university DBMS project (Online Shopping System, MySQL 8 + Flask). Read DOC/ (assignment, main roadmap, and this Phase 11 file) completely before doing anything.

Rules (same as before, plus):
1. Work in sub-phases 11A to 11G in order. Finish and verify one, update PROGRESS.md, then wait for my "go".
2. Back up the database first (mysqldump to backups/). All database changes go in a new re-runnable script sql/08_catalog_expansion.sql using ALTER TABLE and INSERT ... ON DUPLICATE KEY UPDATE. Never DROP existing tables or delete existing orders, users or carts.
3. Comment every new SQL object with WHY it exists. Add viva notes to docs/viva_notes.md for each sub-phase.
4. Use parameterized queries, keep credentials in .env, and keep the code simple and readable.
5. Follow the image and data rules in section 2 of the Phase 11 file exactly.
6. Never claim something works unless you ran it and showed me the output. If a download or a script fails, say so.
7. Do not add features outside this phase. Ask me if anything is unclear.

First response: confirm you read the files, summarize 11A to 11G in 7 lines, list anything you need from me, and wait.
```

## 4. Database changes (sub-phase 11A)

Keep the design in Third Normal Form and explain every change in the viva notes.

| Change | Details |
| --- | --- |
| New table brands | brand\_id PK, name UNIQUE, country (nullable) |
| products | add brand\_id FK to brands, source\_store, source\_url, short\_description; keep existing columns |
| New table product\_images | image\_id PK, product\_id FK (ON DELETE CASCADE), image\_path, is\_primary, sort\_order, source\_url; UNIQUE (product\_id, sort\_order) |
| categories | use the existing parent\_category\_id to build the tree below; add slug (UNIQUE) and image\_path for the category card |
| Index | products(brand\_id), products(category\_id, price), categories(slug) |
| View v\_product\_catalog | product, brand, category path, primary image, price, stock, average rating |
| View v\_category\_counts | category, number of active products |
| Constraint | exactly one primary image per product (enforce with a trigger or a procedure and explain which) |

**Category tree**

- Laptops and Computers: Laptops, Computers (desktops and monitors)
- Accessories and Gadgets: Accessories, Tablets and Gadgets
- Women’s Clothing: Unstitched, Ready to Wear
- Men’s and Kids’ Clothing: Men, Kids
- Kitchen Appliances

The 5 top-level categories drive the home page cards. Sub-categories drive the chips on each category page. Slugs used for image folders are listed in section 8.

## 5. Catalog data pipeline (sub-phase 11B)

1. Create `data/products_manifest.csv` with these columns: product\_name, brand, category\_slug, description, price\_pkr, stock\_quantity, supplier\_name, source\_store, source\_url, image\_files, primary\_image.
2. Fill it from the checklist in section 8 (one row per product). Use the real product name shown on the store page. Descriptions must be short (1 to 2 sentences) and written in our own words, not copied.
3. Write `app/scripts/import_catalog.py`: reads the CSV, validates it, inserts or updates brands, suppliers, categories, products and product\_images, and prints a report of rows imported, rows skipped and products with a missing image file.
4. Image path convention: `static/images/products/<category-slug>/<product-slug>-1.jpg` (extra pictures as -2, -3). Convert or resize large images to at most 1000 px wide, JPEG or WebP, under 300 KB each.
5. Add a placeholder image (static/images/placeholder.svg) used whenever a file is missing.
6. Keep a few of the original sample products only if they still fit the new categories; otherwise mark them is\_active = 0 instead of deleting them, so old orders keep their references.

**Done when:** the import runs twice with no duplicate rows and the report shows 0 products without images.

## 6. Getting the pictures (sub-phase 11C)

**Option A (recommended): save them by hand.** Use the checklist in section 8. Open the store, search the item, open one product page, and save the main image (right-click, Save image as) into the right folder with the file name shown. Optionally save 1 or 2 extra angles as -2 and -3. Split the list between the 3 group members. Fill source\_url in the manifest with the product page link.

**Option B (optional, only if the store allows it): a small polite script.** Antigravity may write `app/scripts/fetch_images.py` that visits only the product page URLs already listed in the manifest, checks robots.txt first, waits at least 3 seconds between requests, stops after the manifest’s last row, and saves the page’s main product images locally. It must not log in, use proxies, or work around any blocking. Any page it cannot fetch is listed in a report and done by hand under Option A.

Ask the group which option to use before writing any download code.

**Done when:** every manifest row has its primary image file on disk and the file opens correctly.

## 7. UI changes (sub-phases 11D to 11F)

**11D: Home page and category browsing**

- Hero strip, then 5 category cards (image, name, product count).
- Category page: breadcrumb, sub-category chips, product grid, sort (price low to high, high to low, newest, top rated), filter by brand and price range, search box, pagination (12 per page).
- Empty state message when a filter returns nothing.

**11E: Product cards and detail page**

- Card: image (lazy loaded, consistent aspect ratio), name, brand, price in PKR, stock badge (In stock, Low stock, Out of stock), Add to cart button.
- Detail page: large image with thumbnail gallery, brand, category breadcrumb, price, description, stock status, reviews, Add to cart.

**11F: Admin product management**

- Admin and staff product form with brand and category dropdowns and image upload (JPEG, PNG, WebP only; maximum 2 MB; rename the file safely).
- Admin page listing products with no image or low stock using the new views.

**Design guidance:** one consistent colour palette, readable typography, mobile-friendly layout (Bootstrap grid), generous spacing, and no layout shift while images load. Test at phone width and desktop width.

**Done when:** a customer can go Home, then a category, then filter and sort, then open a product, then add to cart and complete checkout with the new products.

## 8. Picture checklist (about 50 items)

All files go under `static/images/products/`. The folder is shown in each heading. Brand names are examples of what is sold in Pakistan. The exact model is whatever the store shows, so pick any item that is in stock.

Note: I confirmed that Paklap sells laptops (Dell, HP, Lenovo, Acer, Asus), desktops, tablets, cameras and accessories. For the clothing brands and kitchen brands the list is from general knowledge, so check each item exists on the site and use the closest equivalent if it does not.

### Paklap (paklap.pk): laptops/

| # | Find this | Save as |
| --- | --- | --- |
| 1 | Dell laptop, Core i5 (Latitude or Inspiron) | dell-i5-1.jpg |
| 2 | HP laptop, Core i5 (Pavilion, ProBook or 15s) | hp-i5-1.jpg |
| 3 | Lenovo laptop (IdeaPad or ThinkPad) | lenovo-ideapad-1.jpg |
| 4 | Asus Vivobook | asus-vivobook-1.jpg |
| 5 | Acer Aspire | acer-aspire-1.jpg |
| 6 | Gaming laptop A (Asus TUF, HP Victus, Acer Nitro or Lenovo LOQ) | gaming-a-1.jpg |
| 7 | Gaming laptop B (different brand from 6) | gaming-b-1.jpg |
| 8 | Apple MacBook Air | macbook-air-1.jpg |

### Paklap: computers/

| # | Find this | Save as |
| --- | --- | --- |
| 9 | Branded desktop PC (Dell OptiPlex or HP) | desktop-pc-1.jpg |
| 10 | 24-inch monitor | monitor-24-1.jpg |

### Paklap: accessories/

| # | Find this | Save as |
| --- | --- | --- |
| 11 | Wireless mouse | wireless-mouse-1.jpg |
| 12 | Keyboard (mechanical or wireless) | keyboard-1.jpg |
| 13 | Headphones or gaming headset | headset-1.jpg |
| 14 | Portable SSD or external hard drive | external-ssd-1.jpg |
| 15 | USB flash drive | usb-drive-1.jpg |
| 16 | Laptop backpack or sleeve | laptop-bag-1.jpg |
| 17 | Webcam | webcam-1.jpg |
| 18 | Wi-Fi router | router-1.jpg |

### Paklap: tablets-gadgets/

| # | Find this | Save as |
| --- | --- | --- |
| 19 | Tablet (Samsung Galaxy Tab or iPad) | tablet-1.jpg |
| 20 | Smartwatch | smartwatch-1.jpg |
| 21 | Power bank | power-bank-1.jpg |
| 22 | Bluetooth speaker | bt-speaker-1.jpg |

### Khaadi, Alkaram Studio, Bonanza Satrangi: women-unstitched/

| # | Find this | Save as |
| --- | --- | --- |
| 23 | Khaadi lawn unstitched suit, design A | khaadi-lawn-a-1.jpg |
| 24 | Khaadi unstitched suit, design B (different colour) | khaadi-lawn-b-1.jpg |
| 25 | Alkaram Studio lawn unstitched suit, design A | alkaram-lawn-a-1.jpg |
| 26 | Alkaram Studio unstitched suit, design B | alkaram-lawn-b-1.jpg |
| 27 | Bonanza Satrangi unstitched suit, design A | bonanza-unstitched-a-1.jpg |
| 28 | Bonanza Satrangi unstitched suit, design B | bonanza-unstitched-b-1.jpg |

### Same stores: women-ready-to-wear/

| # | Find this | Save as |
| --- | --- | --- |
| 29 | Khaadi stitched kurta | khaadi-kurta-1.jpg |
| 30 | Alkaram Studio stitched 2-piece or 3-piece suit | alkaram-stitched-1.jpg |
| 31 | Bonanza Satrangi ready-to-wear kurta | bonanza-kurta-1.jpg |
| 32 | Bonanza Satrangi stitched 3-piece suit | bonanza-stitched-1.jpg |
| 33 | Alkaram Studio kurti | alkaram-kurti-1.jpg |

### Khaadi and Bonanza Satrangi (use another store if one does not stock it): men-wear/

| # | Find this | Save as |
| --- | --- | --- |
| 34 | Men’s kurta | men-kurta-1.jpg |
| 35 | Men’s shalwar kameez | men-shalwar-kameez-1.jpg |
| 36 | Men’s waistcoat | men-waistcoat-1.jpg |
| 37 | Men’s polo shirt | men-polo-1.jpg |
| 38 | Men’s casual shirt | men-casual-shirt-1.jpg |

### Same stores: kids-wear/

| # | Find this | Save as |
| --- | --- | --- |
| 39 | Girls’ frock | girls-frock-1.jpg |
| 40 | Boys’ kurta | boys-kurta-1.jpg |
| 41 | Kids’ shalwar kameez | kids-shalwar-kameez-1.jpg |

### Kitchen appliances (brand official sites such as Dawlance, Haier, Orient, Westpoint, Anex, or a general Pakistani marketplace): kitchen-appliances/

| # | Find this | Save as |
| --- | --- | --- |
| 42 | Dawlance refrigerator | refrigerator-1.jpg |
| 43 | Haier microwave oven | microwave-1.jpg |
| 44 | Electric kettle (Westpoint or Anex) | kettle-1.jpg |
| 45 | Blender or juicer (Anex or Westpoint) | blender-1.jpg |
| 46 | Air fryer (any brand sold in Pakistan) | air-fryer-1.jpg |
| 47 | Rice cooker (Anex or Panasonic) | rice-cooker-1.jpg |
| 48 | Hand mixer or food chopper (Westpoint) | hand-mixer-1.jpg |
| 49 | Sandwich maker or toaster (Anex) | sandwich-maker-1.jpg |
| 50 | Built-in gas hob or cooking range (Dawlance or Nasgas) | gas-hob-1.jpg |
| 51 | Water dispenser (Dawlance or Orient) | water-dispenser-1.jpg |

For each item also note in the manifest: the exact product name, the brand, the approximate price in PKR and the product page link.

## 9. Testing, report and viva updates (sub-phase 11G)

- **Tests (add to sql/07\_tests.sql and the web app):** import is repeatable with no duplicates; a product cannot have two primary images; deleting a product removes its image rows but never an order item (orders keep their history); category counts match; filter and sort return the expected rows; missing image falls back to the placeholder; upload rejects a wrong file type and an oversized file.
- **Demo queries:** products per brand, category tree with product counts, top rated products per category, products with no images, average price per category.
- **Documents:** update the ER diagram (brands, product\_images, category changes), the table list in the report (questions 3, 4 and 5), the challenges section (image handling, prices, migrations without losing data) and the future improvements.
- **Viva notes:** each member explains the part they own. Suggested ownership: Member B owns brands, products, product\_images and the catalog views; Member A owns the admin upload form and access rules; Member C owns the cart and checkout tests with the new products. Everyone can explain the import pipeline.

## 10. Tools to install before starting (Antigravity)

Optional but useful. Install before running the starter prompt, then restart Antigravity.

**MCP servers.** In Antigravity open the agent panel menu, then Manage MCP Servers, then View raw config, and merge this into `mcpServers`:

```
{
  "mcpServers": {
    "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] },
    "context7": { "command": "npx", "args": ["-y", "@upstash/context7-mcp"] }
  }
}
```

- **Playwright MCP:** lets the agent open your running Flask app in a browser, click through categories and checkout, and take screenshots to check the UI.
- **Context7:** gives the agent current documentation for Flask, Jinja, Bootstrap and MySQL so it writes fewer outdated snippets.

A MySQL MCP is not needed, since the agent can run the mysql command line directly.

**Skills (UI quality).**

```
npx skills add https://github.com/anthropics/skills -y -g --skill frontend-design
npx skills add https://github.com/vercel-labs/agent-skills -y -g --skill web-design-guidelines
```

frontend-design pushes the agent toward distinctive, intentional layouts instead of generic templates. web-design-guidelines reviews the UI against accessibility and design best practices. If a skill name is not found, run the command without --skill and pick from the list it shows. Check that MCP servers and skills load by asking the agent: "List your MCP servers and skills."

Only install tools from sources you recognise, and read what a skill does before enabling it.
