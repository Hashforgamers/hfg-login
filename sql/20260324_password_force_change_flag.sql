-- Force-password-change support for temporary password flows
ALTER TABLE password_manager
ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE;
