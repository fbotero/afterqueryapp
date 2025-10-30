/*
  # Create challenges table

  1. New Tables
    - `challenges`
      - `id` (uuid, primary key)
      - `name` (text, not null) - The challenge name
      - `git_repo` (text) - Git repository identifier
      - `status` (text) - Challenge status (available, archived)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)
  
  2. Security
    - Enable RLS on `challenges` table
    - Add policy for public read access (since this is a demo app)
    - Add policy for public write access (since this is a demo app)
*/

CREATE TABLE IF NOT EXISTS challenges (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  git_repo text,
  status text DEFAULT 'available',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read challenges"
  ON challenges
  FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anyone can insert challenges"
  ON challenges
  FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Anyone can update challenges"
  ON challenges
  FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);