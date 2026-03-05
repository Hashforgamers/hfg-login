BEGIN;

-- Speed up case-insensitive email lookup in /api/login.
CREATE INDEX IF NOT EXISTS ix_vendor_accounts_email_lower
    ON vendor_accounts (LOWER(email));

-- Speed up PasswordManager lookup by polymorphic owner.
CREATE INDEX IF NOT EXISTS ix_password_manager_parent_type_parent_id
    ON password_manager (parent_type, parent_id);

-- Speed up vendor->pc count aggregation during login response shaping.
CREATE INDEX IF NOT EXISTS ix_consoles_vendor_lower_type
    ON consoles (vendor_id, LOWER(console_type));

-- Speed up validatePin vendor+pin lookup path.
CREATE INDEX IF NOT EXISTS ix_vendor_pins_vendor_id_pin_code
    ON vendor_pins (vendor_id, pin_code);

COMMIT;
