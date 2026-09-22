# Graph Report - hfg-login-service  (2026-09-18)

## Corpus Check
- 27 files · ~4,580 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 96 nodes · 168 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fc8a3e31`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- jwt_helper.py
- auth_routes.py
- extension.py
- auth_services.py
- _EmailText
- app/__init__.py
- AGENTS.md
- password_manager

## God Nodes (most connected - your core abstractions)
1. `create_jwt_token()` - 9 edges
2. `_EmailText` - 8 edges
3. `create_app()` - 6 edges
4. `forgot_password()` - 6 edges
5. `refresh_token()` - 6 edges
6. `configure_redis()` - 5 edges
7. `PasswordManager` - 5 edges
8. `PasswordResetCode` - 5 edges
9. `Vendor` - 5 edges
10. `VendorPin` - 5 edges

## Surprising Connections (you probably didn't know these)
- `_build_hfg_email_template()` --calls--> `build_hfg_email_html()`  [EXTRACTED]
  routes/auth_routes.py → services/email_template.py
- `validate_pin()` --calls--> `create_jwt_token()`  [EXTRACTED]
  routes/auth_routes.py → utils/jwt_helper.py
- `forgot_password()` --calls--> `email_text()`  [EXTRACTED]
  routes/auth_routes.py → services/email_template.py
- `login()` --calls--> `create_jwt_token()`  [EXTRACTED]
  services/auth_services.py → utils/jwt_helper.py
- `forgot_password()` --calls--> `PasswordResetCode`  [EXTRACTED]
  routes/auth_routes.py → models/passwordResetCode.py

## Import Cycles
- None detected.

## Communities (14 total, 2 thin omitted)

### Community 0 - "jwt_helper.py"
Cohesion: 0.13
Nodes (18): refresh_token_route(), generate_token_for_vendor(), Generate JWT token directly from vendor_id and parent_type., create_jwt_token(), decode_token(), extract_token_from_header(), is_token_blacklisted(), Refresh a JWT token by generating a new token with the same payload. :param… (+10 more)

### Community 1 - "auth_routes.py"
Cohesion: 0.24
Nodes (13): PasswordResetCode, route, auth_health(), _build_hfg_email_template(), change_password(), _ensure_password_force_change_column(), forgot_password(), login_route() (+5 more)

### Community 2 - "extension.py"
Cohesion: 0.18
Nodes (8): configure_redis(), Flask, Configures the Redis client with the app configuration., Console, Vendor, VendorAccount, VendorPin, VendorStatus

### Community 3 - "auth_services.py"
Cohesion: 0.21
Nodes (10): ContactInfo, PasswordManager, User, logout_route(), invalidate_token(), login(), Authenticate a user or vendor and return a JWT token., Invalidate a JWT token by adding it to the blacklist. :param token: The JWT… (+2 more)

### Community 4 - "_EmailText"
Cohesion: 0.24
Nodes (6): HTMLParser, build_hfg_email_html(), email_text(), _EmailText, _extract_body(), Generate a useful plain-text alternative, retaining links and table values.

### Community 5 - "app/__init__.py"
Cohesion: 0.39
Nodes (5): Config, create_app(), _is_insecure_secret(), Flask, _validate_production_config()

## Knowledge Gaps
- **2 isolated node(s):** `VendorStatus`, `graphify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `email_text()` connect `_EmailText` to `auth_routes.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `create_jwt_token()` connect `jwt_helper.py` to `auth_routes.py`, `auth_services.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `VendorStatus`, `graphify` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `jwt_helper.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13450292397660818 - nodes in this community are weakly interconnected._