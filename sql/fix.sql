-- FORK ONLY. Review and adapt to the actual schema before running.
-- This example assumes public.sensor_data.time is already TIMESTAMPTZ NOT NULL.
-- Do not use it to guess a timezone for a timestamp-without-time-zone column.

-- Inspect existing indexes first (see 01_profile.sql). This conversion can
-- take time and may lock a populated table. Foreign keys require extra care.
SELECT create_hypertable(
    'public.sensor_data',
    by_range('time'),
    migrate_data => true,
    if_not_exists => true
);

-- Tiger/Timescale may create the partition-column index automatically.
-- Add another index only if inspection shows it is absent and the measured
-- query workload benefits from it. For example, for per-device lookups:
-- CREATE INDEX sensor_data_device_time_idx
--     ON public.sensor_data (device_id, time DESC) INCLUDE (value);

-- Compare this plan with the saved baseline from 01_profile.sql.
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT avg(value)
FROM public.sensor_data
WHERE time > now() - interval '1 day';
