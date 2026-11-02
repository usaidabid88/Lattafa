# KNOWN_ISSUES.md - Phase 11 Operational Issues

| Issue ID | Sub-Phase | Description | Impact | Mitigation / Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-11C-01** | 11C | Pakistani retail domains (Khaadi, Dawlance, Bonanza Satrangi, Alkaram, Westpoint) returned HTTP 403 Forbidden or Cloudflare challenge during automated image retrieval. Per Option B safety rules, requests were halted after two 403s. | 49 product images could not be fetched directly from external CDN endpoints. | Resolved by generating local specimen fallback assets in `static/images/products/<category-slug>/` and fallback to `placeholder.svg`. Zero HTTP 404 broken images exist in the storefront. Full audit list exported to `data/images_report.json` for optional manual replacement. |
| **ISSUE-12C-01** | 12C | Simulated payment gateway runs in test sandbox mode only; no real merchant banking accounts or cards are processed. | Live banking transactions cannot be executed. | Intended behavior per safety rules; test cards and simulated success/fail/cancel buttons allow 100% test coverage without security or financial exposure. |
