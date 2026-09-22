# Graph Report - hfg-login-service  (2026-09-22)

## Corpus Check
- 28 files · ~4,768 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 104 nodes · 178 edges · 16 communities (12 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e468c93d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jwt_helper.py
- auth_routes.py
- vendor.py
- auth_services.py
- _EmailText
- extension.py
- AGENTS.md
- password_manager
- LoginTests
- console.py

## God Nodes (most connected - your core abstractions)
1. `create_jwt_token()` - 9 edges
2. `_EmailText` - 8 edges
3. `create_app()` - 6 edges
4. `forgot_password()` - 6 edges
5. `LoginTests` - 6 edges
6. `refresh_token()` - 6 edges
7. `configure_redis()` - 5 edges
8. `PasswordManager` - 5 edges
9. `PasswordResetCode` - 5 edges
10. `Vendor` - 5 edges

## Surprising Connections (you probably didn't know these)
- `_build_hfg_email_template()` --calls--> `build_hfg_email_html()`  [EXTRACTED]
  routes/auth_routes.py → services/email_template.py
- `validate_pin()` --calls--> `create_jwt_token()`  [EXTRACTED]
  routes/auth_routes.py → utils/jwt_helper.py
- `refresh_token_route()` --calls--> `refresh_token()`  [EXTRACTED]
  routes/auth_routes.py → utils/jwt_helper.py
- `forgot_password()` --calls--> `email_text()`  [EXTRACTED]
  routes/auth_routes.py → services/email_template.py
- `forgot_password()` --calls--> `PasswordResetCode`  [EXTRACTED]
  routes/auth_routes.py → models/passwordResetCode.py

## Import Cycles
- None detected.

## Communities (16 total, 4 thin omitted)

### Community 0 - "jwt_helper.py"
Cohesion: 0.19
Nodes (12): decode_token(), extract_token_from_header(), is_token_blacklisted(), Refresh a JWT token by generating a new token with the same payload. :param…, Decode a JWT token. :param token: Encoded JWT token as a string. :return:…, Validate the given token by decoding it and checking if it's blacklisted.…, Check if the token is blacklisted. :param token: JWT token as a string.…, Revoke a token by adding it to a blacklist. :param token: JWT token as a string. (+4 more)

### Community 1 - "auth_routes.py"
Cohesion: 0.22
Nodes (15): PasswordResetCode, route, auth_health(), _build_hfg_email_template(), change_password(), _ensure_password_force_change_column(), forgot_password(), login_route() (+7 more)

### Community 2 - "vendor.py"
Cohesion: 0.48
Nodes (3): Vendor, VendorAccount, VendorPin

### Community 3 - "auth_services.py"
Cohesion: 0.16
Nodes (14): ContactInfo, PasswordManager, User, logout_route(), generate_token_for_vendor(), invalidate_token(), login(), Generate JWT token directly from vendor_id and parent_type. (+6 more)

### Community 4 - "_EmailText"
Cohesion: 0.24
Nodes (6): HTMLParser, build_hfg_email_html(), email_text(), _EmailText, _extract_body(), Generate a useful plain-text alternative, retaining links and table values.

### Community 5 - "extension.py"
Cohesion: 0.22
Nodes (9): Config, configure_redis(), Flask, Configures the Redis client with the app configuration., create_app(), _is_insecure_secret(), Flask, _validate_production_config() (+1 more)

## Knowledge Gaps
- **2 isolated node(s):** `VendorStatus`, `graphify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `email_text()` connect `_EmailText` to `auth_routes.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `create_jwt_token()` connect `auth_services.py` to `jwt_helper.py`, `auth_routes.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **What connects `VendorStatus`, `graphify` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._