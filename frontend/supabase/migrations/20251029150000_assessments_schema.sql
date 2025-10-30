/*
  Assessments core schema

  Notes:
  - RLS enabled without public policies; backend should use service role key.
*/

-- enums
DO $$ BEGIN
  CREATE TYPE invite_status AS ENUM ('pending', 'started', 'submitted', 'expired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- assessments
CREATE TABLE IF NOT EXISTS assessments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  instructions text,
  seed_github_url text NOT NULL,
  start_window_hours integer NOT NULL CHECK (start_window_hours > 0),
  complete_window_hours integer NOT NULL CHECK (complete_window_hours > 0),
  email_subject text,
  email_body text,
  seed_repo_name text,
  seed_repo_id bigint,
  seed_is_template boolean DEFAULT false,
  seed_main_head_sha text,
  last_seed_sync_at timestamptz,
  created_by text,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

-- assessment_versions
CREATE TABLE IF NOT EXISTS assessment_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id uuid NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  seed_head_sha text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE assessment_versions ENABLE ROW LEVEL SECURITY;

-- candidates
CREATE TABLE IF NOT EXISTS candidates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL,
  name text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- assessment_invites
CREATE TABLE IF NOT EXISTS assessment_invites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id uuid NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  candidate_id uuid NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
  start_token uuid NOT NULL DEFAULT gen_random_uuid(),
  start_deadline_at timestamptz NOT NULL,
  started_at timestamptz,
  complete_deadline_at timestamptz,
  status invite_status NOT NULL DEFAULT 'pending',
  candidate_repo_id bigint,
  candidate_repo_name text,
  candidate_repo_html_url text,
  candidate_repo_clone_url text,
  pinned_seed_sha text,
  final_commit_sha text,
  submitted_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assessment_invites_token ON assessment_invites(start_token);
CREATE INDEX IF NOT EXISTS idx_assessment_invites_status ON assessment_invites(status);

ALTER TABLE assessment_invites ENABLE ROW LEVEL SECURITY;

-- emails_sent
CREATE TABLE IF NOT EXISTS emails_sent (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  invite_id uuid REFERENCES assessment_invites(id) ON DELETE SET NULL,
  type text NOT NULL,
  to_email text NOT NULL,
  subject text,
  status text,
  message_id text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE emails_sent ENABLE ROW LEVEL SECURITY;

-- webhook_events (optional)
CREATE TABLE IF NOT EXISTS webhook_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,
  event text NOT NULL,
  payload jsonb NOT NULL,
  received_at timestamptz DEFAULT now()
);

ALTER TABLE webhook_events ENABLE ROW LEVEL SECURITY;


