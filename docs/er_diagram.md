# ER Diagram – Online Shopping System
**MUET DBMS CEP | Department of Software Engineering**

All 13 tables and their relationships are shown below.
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

    %% ── MEMBER B: Catalog and Inventory ─────────────────────────────────
    categories {
        int         category_id     PK
        varchar     name            UK
        int         parent_category_id FK
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
        int         supplier_id     FK
        varchar     name
        text        description
        decimal     price
        int         stock_quantity
        tinyint     is_active
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
    users       ||--o{  addresses   : "has many"
    users       ||--o{  carts       : "has many"
    users       ||--o{  orders      : "places many"
    users       ||--o{  reviews     : "writes many"

    %% Member B relationships
    categories  ||--o{  products    : "contains many"
    categories  ||--o|  categories  : "parent of (self-ref)"
    suppliers   ||--o{  products    : "supplies many"
    products    ||--o{  reviews     : "receives many"

    %% Member C relationships
    carts       ||--o{  cart_items  : "holds many"
    products    ||--o{  cart_items  : "added to many"
    orders      ||--o{  order_items : "contains many"
    products    ||--o{  order_items : "ordered in many"
    addresses   ||--o{  orders      : "ships to many"
    orders      ||--||  payments    : "paid by exactly one"
    orders      ||--o|  shipments   : "shipped via one"
```

## Relationship summary (for the report)

| Relationship | Type | Why |
|---|---|---|
| users → addresses | 1 to many | A customer can have multiple delivery addresses |
| users → carts | 1 to many | Each shopping session creates a new cart |
| users → orders | 1 to many | A customer places many orders over time |
| users → reviews | 1 to many | A customer can review many products |
| categories → categories | self-reference | Allows sub-categories (e.g. Electronics → Mobiles) |
| categories → products | 1 to many | Each product belongs to one category |
| suppliers → products | 1 to many | One supplier provides many products |
| products → reviews | 1 to many | A product receives many customer reviews |
| carts ↔ products | many to many | Resolved by cart_items junction table |
| orders ↔ products | many to many | Resolved by order_items junction table |
| orders → payments | 1 to 1 | Every order has exactly one payment record |
| orders → shipments | 1 to 0-or-1 | Shipment is created only after payment |
| addresses → orders | 1 to many | An address can be used for multiple orders |

## Key design note
`order_items` stores `unit_price` (copied from the product at checkout time).
This is intentional: if the product price changes later, old order totals must
remain correct. This is a classic example of denormalization done on purpose.
