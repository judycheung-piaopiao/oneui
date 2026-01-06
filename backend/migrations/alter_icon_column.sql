-- Alter icon column to allow longer URLs
-- Run this SQL against your PostgreSQL database

ALTER TABLE tools 
ALTER COLUMN icon TYPE VARCHAR(500);

-- Verify the change
\d tools
