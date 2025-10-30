-- Add unique constraint on candidates.email
-- This migration removes duplicate emails (keeping the earliest row per email) and then adds a unique constraint

-- Remove duplicates, keeping the earliest row per email (by created_at, then id)
WITH ranked AS (
  SELECT id, email,
         ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at NULLS LAST, id) AS rn
  FROM candidates
)
DELETE FROM candidates c
USING ranked r
WHERE c.id = r.id AND r.rn > 1;

-- Add unique constraint on email
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'candidates_email_key'
  ) THEN
    ALTER TABLE candidates ADD CONSTRAINT candidates_email_key UNIQUE (email);
  END IF;
END $$;

