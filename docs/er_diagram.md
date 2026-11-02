# ER Diagram – Online Shopping System (Expanded Phase 11)
**MUET DBMS CEP | Department of Software Engineering**

All 15 tables and their relationships are shown below (including Phase 11 Brand Management and Multi-Image Catalog Gallery entities).
To export as PNG: open this file in VS Code with the Mermaid Preview extension,
or paste the diagram block into https://mermaid.live and download.

```mermaid
erDiagram

    %% ── MEMBER A: Users and Access ──────────────────────────────────────
    users {
        int         user_id         PK
        varchar     full_name
        varchar     email           UK
        varchar     password_hash
        varchar     phone
        enum        role
        datetime    created_at
    }

    addresses {
        int         address_id      PK
        int         user_id         FK
        varchar     line1
        varchar     city
        varchar     province
        varchar     postal_code
        tinyint     is_default
    }

    audit_log {
        int         log_id          PK
        varchar     table_name
        varchar     action
        int         record_id
        text        details
        datetime    changed_at
    }

    %% ── MEMBER B: Catalog, Brands & Multi-Image Gallery ──────────────────
    brands {
        int         brand_id        PK
        varchar     name            UK
        varchar     country
        datetime    created_at
    }

    categories {
        int         category_id     PK
        varchar     name            UK
        varchar     slug            UK
        int         parent_category_id FK
        varchar     image_path
    }

    suppliers {
        int         supplier_id     PK
        varchar     name
        varchar     email
        varchar     phone
    }

    products {
        int         product_id      PK
        int         category_id     FK
        int         brand_id        FK
        int         supplier_id     FK
        varchar     name
        varchar     short_description
        text        description
        decimal     price
        int         stock_quantity
        varchar     source_store
        varchar     source_url
        tinyint     is_active
        datetime    created_at
    }

    product_images {
        int         image_id        PK
        int         product_id      FK
        varchar     image_path
        tinyint     is_primary
        int         sort_order
        varchar     source_url
        datetime    created_at
    }

    reviews {
        int         review_id       PK
        int         user_id         FK
        int         product_id      FK
        int         rating
        text        comment
        datetime    created_at
    }

    %% ── MEMBER C: Orders and Payments ───────────────────────────────────
    carts {
        int         cart_id         PK
        int         user_id         FK
        enum        status
        datetime    created_at
        datetime    updated_at
    }

    cart_items {
        int         cart_id         FK
        int         product_id      FK
        int         quantity
    }

    orders {
        int         order_id        PK
        int         user_id         FK
        int         address_id      FK
        datetime    order_date
        enum        status
        decimal     total_amount
    }

    order_items {
        int         order_id        FK
        int         product_id      FK
        int         quantity
        decimal     unit_price
    }

    payments {
        int         payment_id      PK
        int         order_id        FK
        enum        method
        decimal     amount
        enum        status
        datetime    paid_at
    }

    shipments {
        int         shipment_id     PK
        int         order_id        FK
        varchar     courier
        varchar     tracking_number
        datetime    shipped_at
        datetime    delivered_at
    }

    %% ── Relationships ────────────────────────────────────────────────────

    %% Member A relationships
    users          ||--o{  addresses       : "has many"
    users          ||--o{  carts           : "has many"
    users          ||--o{  orders          : "places many"
    users          ||--o{  reviews         : "writes many"

    %% Member B relationships
    brands         ||--o{  products        : "manufactures many"
    categories     ||--o{  products        : "contains many"
    categories     ||--o|  categories      : "parent of (self-ref)"
    suppliers      ||--o{  products        : "supplies many"
    products       ||--o{  product_images  : "showcased by many (ON DELETE CASCADE)"
    products       ||--o{  reviews         : "receives many"

    %% Member C relationships
    carts          ||--o{  cart_items      : "holds many"
    products       ||--o{  cart_items      : "added to many"
    orders         ||--o{  order_items     : "contains many"
    products       ||--o{  order_items     : "ordered in many"
    addresses      ||--o{  orders          : "ships to many"
    orders         ||--||  payments        : "paid by exactly one"
    orders         ||--o|  shipments       : "shipped via one"
```

## Relationship summary (15 Entities in 3NF)

| Relationship | Type | Why |
|---|---|---|
| brands → products | 1 to many | A brand produces multiple catalog items; product retains brand_id FK |
| products → product_images | 1 to many | A product has multiple gallery pictures (ON DELETE CASCADE) |
| users → addresses | 1 to many | A customer can have multiple delivery addresses |
| users → carts | 1 to many | Each shopping session creates a new cart |
| users → orders | 1 to many | A customer places many orders over time |
| users → reviews | 1 to many | A customer can review many products |
| categories → categories | self-reference | Allows multi-level departmental hierarchy (Laptops & Computers → Laptops) |
| categories → products | 1 to many | Each product belongs to one specific category |
| suppliers → products | 1 to many | One supplier provides many products |
| products → reviews | 1 to many | A product receives many customer reviews |
| carts ↔ products | many to many | Resolved by cart_items junction table |
| orders ↔ products | many to many | Resolved by order_items junction table |
| orders → payments | 1 to 1 | Every order has exactly one payment record |
| orders → shipments | 1 to 0-or-1 | Shipment is created only after payment settlement |
| addresses → orders | 1 to many | An address can be used for multiple orders |

## Key design notes
1. `order_items` stores `unit_price` (copied from the product at checkout time). This deliberate denormalization preserves accounting audit records against future catalog price updates.
2. `product_images` isolates media storage from core product rows into an atomic 1-to-N relation, preventing 1NF violations and eliminating string-splitting queries.
