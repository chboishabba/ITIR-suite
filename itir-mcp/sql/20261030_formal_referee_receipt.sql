-- PostgreSQL is the only runtime authority for independent formal referee receipts.
-- Apply using the privileged migration role, not the application runtime role.
CREATE SCHEMA IF NOT EXISTS formal;
CREATE TABLE IF NOT EXISTS formal.referee_receipt (
  repo text NOT NULL,
  sha text NOT NULL CHECK (sha ~ '^[0-9a-f]{40}$'),
  path text NOT NULL,
  canonical_thread_id text NOT NULL,
  receipt_json jsonb NOT NULL,
  PRIMARY KEY (repo, sha, path, canonical_thread_id)
);
-- Role grants should be managed by deployment: referee INSERT/SELECT,
-- consumers SELECT only. No UPDATE or DELETE for runtime identities.
