-- Read-only profiling template. Replace the table/column names for your schema.
-- Run against the isolated test fork. EXPLAIN ANALYZE executes the SELECT.

SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'sensor_data'
ORDER BY ordinal_position;

SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'sensor_data'
ORDER BY indexname;

EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT avg(value)
FROM public.sensor_data
WHERE time > now() - interval '1 day';
