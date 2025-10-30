-- Rename assessments to challenges and related tables/columns/indexes

-- First, drop the old challenges table if it exists (from earlier migration)
-- This table has a different schema and will be replaced by the assessments table
DO $$ BEGIN
  DROP POLICY IF EXISTS "Anyone can read challenges" ON challenges;
EXCEPTION WHEN undefined_table THEN NULL; END $$;

DO $$ BEGIN
  DROP POLICY IF EXISTS "Anyone can insert challenges" ON challenges;
EXCEPTION WHEN undefined_table THEN NULL; END $$;

DO $$ BEGIN
  DROP POLICY IF EXISTS "Anyone can update challenges" ON challenges;
EXCEPTION WHEN undefined_table THEN NULL; END $$;

DROP TABLE IF EXISTS challenges CASCADE;

-- Now rename assessments to challenges
ALTER TABLE IF EXISTS assessments RENAME TO challenges;
ALTER TABLE IF EXISTS assessment_versions RENAME TO challenge_versions;
ALTER TABLE IF EXISTS assessment_invites RENAME TO challenge_invites;

-- Foreign keys: challenge_versions.assessment_id → challenge_id
DO $$ BEGIN
  ALTER TABLE challenge_versions
    DROP CONSTRAINT IF EXISTS assessment_versions_assessment_id_fkey;
EXCEPTION WHEN undefined_object THEN NULL; END $$;

ALTER TABLE challenge_versions
  RENAME COLUMN assessment_id TO challenge_id;

ALTER TABLE challenge_versions
  ADD CONSTRAINT challenge_versions_challenge_id_fkey
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE;

-- Foreign keys: challenge_invites.assessment_id → challenge_id
DO $$ BEGIN
  ALTER TABLE challenge_invites
    DROP CONSTRAINT IF EXISTS assessment_invites_assessment_id_fkey;
EXCEPTION WHEN undefined_object THEN NULL; END $$;

ALTER TABLE challenge_invites
  RENAME COLUMN assessment_id TO challenge_id;

ALTER TABLE challenge_invites
  ADD CONSTRAINT challenge_invites_challenge_id_fkey
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE;

-- Index renames (use IF EXISTS to avoid errors if they are absent)
DO $$ 
BEGIN
  ALTER INDEX idx_assessment_invites_token RENAME TO idx_challenge_invites_token;
EXCEPTION WHEN undefined_table OR undefined_object THEN NULL; 
END $$;

DO $$ 
BEGIN
  ALTER INDEX idx_assessment_invites_status RENAME TO idx_challenge_invites_status;
EXCEPTION WHEN undefined_table OR undefined_object THEN NULL; 
END $$;

-- Ensure RLS remains enabled (tables had it previously)

