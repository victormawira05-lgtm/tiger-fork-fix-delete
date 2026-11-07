-- TEMPLATE ONLY. Do not run until you establish what timezone the old values
-- represent. `timestamp without time zone` has no timezone information.
-- Replace the example with the confirmed source timezone (UTC shown here).
-- Apply on the disposable fork and review the lock/rewrite implications first.

-- ALTER TABLE public.sensor_data
--   ALTER COLUMN time TYPE timestamptz
--   USING time AT TIME ZONE 'UTC';

-- Verify type, nullability, row counts, min/max timestamps, and representative
-- values before any hypertable conversion. See 01_profile.sql for inspection.
