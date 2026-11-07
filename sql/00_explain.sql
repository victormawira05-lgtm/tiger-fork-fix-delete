-- EXPLAIN ANALYZE executes this SELECT. Run only on the isolated test fork.
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT avg(value)
FROM public.sensor_data
WHERE time > now() - interval '1 day';
