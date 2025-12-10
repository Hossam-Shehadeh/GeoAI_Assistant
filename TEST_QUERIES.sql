-- ============================================
-- Test Queries for Example 11 Tables
-- ============================================
-- Use these queries to test your imported tables
-- ============================================

-- ============================================
-- 1. CHECK IF TABLES EXIST
-- ============================================
-- Verify all tables were imported successfully
SELECT 
    table_name,
    (SELECT COUNT(*) 
     FROM information_schema.columns 
     WHERE table_name = t.table_name 
     AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_name IN ('buildings', 'roads', 'landuse', 'sewage', 'cistern')
ORDER BY table_name;

-- ============================================
-- 2. COUNT ROWS IN EACH TABLE
-- ============================================
-- Check how many features are in each table
SELECT 'buildings' as table_name, COUNT(*) as row_count FROM buildings
UNION ALL
SELECT 'roads', COUNT(*) FROM roads
UNION ALL
SELECT 'landuse', COUNT(*) FROM landuse
UNION ALL
SELECT 'sewage', COUNT(*) FROM sewage
UNION ALL
SELECT 'cistern', COUNT(*) FROM cistern
ORDER BY table_name;

-- ============================================
-- 3. CHECK GEOMETRY COLUMNS
-- ============================================
-- Verify geometry columns exist and are correct
SELECT 
    f_table_name as table_name,
    f_geometry_column as geometry_column,
    type as geometry_type,
    coord_dimension,
    srid
FROM geometry_columns
WHERE f_table_schema = 'public'
    AND f_table_name IN ('buildings', 'roads', 'landuse', 'sewage', 'cistern')
ORDER BY f_table_name;

-- ============================================
-- 4. SAMPLE DATA FROM BUILDINGS
-- ============================================
-- Get first 5 buildings
SELECT 
    id,
    geom,
    ST_AsText(geom) as geometry_text
FROM buildings
LIMIT 5;

-- ============================================
-- 5. BUILDINGS WITH AREA (if area column exists)
-- ============================================
-- Get buildings with area information
SELECT 
    id,
    "AREA" as area,
    "OWNER" as owner,
    "TYPE" as type,
    ST_Area(geom) as calculated_area
FROM buildings
WHERE "AREA" IS NOT NULL
ORDER BY "AREA" DESC
LIMIT 10;

-- ============================================
-- 6. COUNT BY TYPE (if TYPE column exists)
-- ============================================
-- Count buildings by type
SELECT 
    "TYPE" as building_type,
    COUNT(*) as count
FROM buildings
WHERE "TYPE" IS NOT NULL
GROUP BY "TYPE"
ORDER BY count DESC;

-- ============================================
-- 7. ROADS LENGTH
-- ============================================
-- Calculate total length of roads
SELECT 
    COUNT(*) as road_count,
    SUM(ST_Length(geom)) as total_length_meters,
    SUM(ST_Length(geom::geography)) as total_length_meters_geography
FROM roads;

-- ============================================
-- 8. LANDUSE AREA
-- ============================================
-- Calculate total area of landuse
SELECT 
    COUNT(*) as landuse_count,
    SUM(ST_Area(geom)) as total_area,
    AVG(ST_Area(geom)) as avg_area
FROM landuse;

-- ============================================
-- 9. SPATIAL QUERY - BUILDINGS NEAR ROADS
-- ============================================
-- Find buildings within 100 meters of roads
SELECT 
    b.id as building_id,
    r.id as road_id,
    ST_Distance(b.geom::geography, r.geom::geography) as distance_meters
FROM buildings b
CROSS JOIN roads r
WHERE ST_DWithin(b.geom::geography, r.geom::geography, 100)
LIMIT 10;

-- ============================================
-- 10. SIMPLE SELECT - ALL TABLES
-- ============================================
-- Quick test: Select from each table

-- Buildings
SELECT COUNT(*) as buildings_count FROM buildings;

-- Roads
SELECT COUNT(*) as roads_count FROM roads;

-- Landuse
SELECT COUNT(*) as landuse_count FROM landuse;

-- Sewage
SELECT COUNT(*) as sewage_count FROM sewage;

-- Cistern
SELECT COUNT(*) as cistern_count FROM cistern;

-- ============================================
-- 11. CHECK TABLE STRUCTURE
-- ============================================
-- See columns in buildings table
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'buildings'
ORDER BY ordinal_position;

-- ============================================
-- 12. SPATIAL EXTENT
-- ============================================
-- Get bounding box of all features
SELECT 
    'buildings' as layer,
    ST_AsText(ST_Extent(geom)) as bounding_box
FROM buildings
UNION ALL
SELECT 
    'roads',
    ST_AsText(ST_Extent(geom))
FROM roads
UNION ALL
SELECT 
    'landuse',
    ST_AsText(ST_Extent(geom))
FROM landuse;

-- ============================================
-- QUICK TEST QUERIES
-- ============================================
-- Run these to quickly verify everything works:

-- Test 1: Do tables exist?
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('buildings', 'roads', 'landuse', 'sewage', 'cistern');

-- Test 2: Do they have data?
SELECT 'buildings' as table_name, COUNT(*) as rows FROM buildings
UNION ALL SELECT 'roads', COUNT(*) FROM roads
UNION ALL SELECT 'landuse', COUNT(*) FROM landuse
UNION ALL SELECT 'sewage', COUNT(*) FROM sewage
UNION ALL SELECT 'cistern', COUNT(*) FROM cistern;

-- Test 3: Do they have geometry?
SELECT f_table_name, f_geometry_column, type 
FROM geometry_columns 
WHERE f_table_schema = 'public';

-- ============================================
