# KNOWN_ISSUES.md - Phase 11 Operational Issues

| Issue ID | Sub-Phase | Description | Impact | Mitigation / Status |
| :--- | :--- | :--- | :--- | :--- |
| **ISSUE-11C-01** | 11C | Pakistani retail domains (Khaadi, Dawlance, Bonanza Satrangi, Alkaram, Westpoint) returned HTTP 403 Forbidden or Cloudflare challenge during automated image retrieval. Per Option B safety rules, requests were halted after two 403s. | 49 product images could not be fetched directly from external CDN endpoints. | Resolved by generating local specimen fallback assets in `static/images/products/<category-slug>/` and fallback to `placeholder.svg`. Zero HTTP 404 broken images exist in the storefront. Full audit list exported to `data/images_report.json` for optional manual replacement. |
