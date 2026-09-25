-- Initialize PostGIS extensions for SIH 2026 Disaster Management
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'PostGIS and UUID extensions installed successfully for SIH 2026 Database';
END $$;
