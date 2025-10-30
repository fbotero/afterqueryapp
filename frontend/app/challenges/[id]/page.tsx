'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { supabase, Challenge } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Copy, X } from 'lucide-react';

export default function ChallengeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [loading, setLoading] = useState(true);
  const [inviteId, setInviteId] = useState('');
  const [seedGitCloneUrl, setSeedGitCloneUrl] = useState<string | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareResult, setCompareResult] = useState<{ added: string[]; removed: string[]; unchanged_count: number } | null>(null);
  const [followUpLoading, setFollowUpLoading] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  useEffect(() => {
    loadChallenge();
  }, []);

  async function loadChallenge() {
    try {
      const res = await fetch(`${API_BASE}/api/admin/challenges/${params.id}`);
      if (!res.ok) {
        setLoading(false);
        return;
      }
      const json = await res.json();
      const challengeData = json?.challenge;
      if (challengeData) {
        // Map backend challenge data to frontend Challenge type
        setChallenge({
          id: challengeData.id,
          name: challengeData.title || challengeData.seed_repo_name || 'Untitled Challenge',
          git_repo: challengeData.seed_repo_name || challengeData.git_clone_url,
          status: 'available',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as Challenge);
        setSeedGitCloneUrl(challengeData.git_clone_url ?? null);
      }
    } catch (error) {
      console.error('Failed to load challenge:', error);
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!challenge) {
    return <div className="p-8">Challenge not found</div>;
  }

  const derivedFromChallenge = (() => {
    const repo = challenge?.git_repo?.trim();
    if (!repo) return null;
    if (repo.startsWith('http://') || repo.startsWith('https://')) {
      return repo.endsWith('.git') ? repo : `${repo}.git`;
    }
    if (repo.includes('/')) {
      const suffixed = repo.endsWith('.git') ? repo : `${repo}.git`;
      return `https://github.com/${suffixed}`;
    }
    return null;
  })();

  const gitCloneUrl = seedGitCloneUrl ?? derivedFromChallenge ?? `https://github.com/fbotero/afterqueryexampe.git`;

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-4xl font-normal mb-8">{challenge?.name || 'Challenge'}</h1>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <div className="flex gap-3 mb-6">
          <Button className="bg-green-600 hover:bg-green-700 text-white" onClick={() => router.push(`/challenges/${params.id}/invite`)}>
            Send to Candidate
          </Button>
          <Button variant="outline" className="border-gray-300">
            Edit
          </Button>
          <Button variant="outline" className="border-gray-300">
            Archive
          </Button>
        </div>
      </div>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <h2 className="text-xl font-medium mb-4">Assignments</h2>
        <div className="grid grid-cols-4 gap-4 text-sm text-gray-700">
          <span>0 total</span>
          <span>0 outstanding</span>
          <span>0 in progress</span>
          <span>0 finished</span>
        </div>
      </div>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <h2 className="text-xl font-medium mb-3">Review</h2>
        <p className="text-gray-700 mb-3">Enter an Invite ID to view a diff summary or send a follow-up email.</p>
        <div className="flex gap-3 items-center mb-4">
          <Input
            placeholder="Invite ID"
            value={inviteId}
            onChange={(e) => setInviteId(e.target.value)}
            className="max-w-sm"
          />
          <Button
            variant="outline"
            className="border-gray-300"
            disabled={!inviteId || compareLoading}
            onClick={async () => {
              setCompareLoading(true);
              setCompareResult(null);
              try {
                const res = await fetch(`${API_BASE}/api/admin/invites/${inviteId}/compare`);
                const json = await res.json();
                setCompareResult(json?.diff_summary ?? null);
              } finally {
                setCompareLoading(false);
              }
            }}
          >
            {compareLoading ? 'Loading…' : 'View Compare'}
          </Button>
          <Button
            className="bg-green-600 hover:bg-green-700 text-white"
            disabled={!inviteId || followUpLoading}
            onClick={async () => {
              setFollowUpLoading(true);
              try {
                await fetch(`${API_BASE}/api/admin/invites/${inviteId}/follow-up`, { method: 'POST' });
                alert('Follow-up email sent');
              } finally {
                setFollowUpLoading(false);
              }
            }}
          >
            {followUpLoading ? 'Sending…' : 'Send Follow-Up'}
          </Button>
        </div>

        {compareResult && (
          <div className="mt-4 text-sm text-gray-700">
            <div className="mb-2"><span className="font-medium">Added files:</span> {compareResult.added.length}</div>
            <div className="mb-2"><span className="font-medium">Removed files:</span> {compareResult.removed.length}</div>
            <div className="mb-2"><span className="font-medium">Unchanged files:</span> {compareResult.unchanged_count}</div>
            {compareResult.added.length > 0 && (
              <details className="mt-3">
                <summary className="cursor-pointer text-blue-600">Show added</summary>
                <ul className="list-disc pl-6 mt-2">
                  {compareResult.added.slice(0, 100).map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </details>
            )}
            {compareResult.removed.length > 0 && (
              <details className="mt-3">
                <summary className="cursor-pointer text-blue-600">Show removed</summary>
                <ul className="list-disc pl-6 mt-2">
                  {compareResult.removed.slice(0, 100).map((p) => (
                    <li key={p}>{p}</li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </div>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <h2 className="text-xl font-medium mb-3">Watchers</h2>
        <p className="text-gray-700 mb-4">
          The following team members will recieve notifications about this challenge:
        </p>
        <div className="flex gap-2">
          <Badge className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-sm flex items-center gap-2">
            derijk8@gmail.com
            <X className="w-4 h-4 cursor-pointer" />
          </Badge>
        </div>
      </div>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <h2 className="text-xl font-medium mb-3">Challenge template repository</h2>
        <p className="text-gray-700 mb-4">
          The main branch of this repository acts as a template for the coding challenges you send to candidates.
        </p>

        <div className="bg-gray-50 border border-gray-300 p-4 mb-3 font-mono text-sm relative">
          <button
            onClick={() => copyToClipboard(gitCloneUrl)}
            className="absolute top-2 right-2 p-2 bg-yellow-400 hover:bg-yellow-500 rounded"
            title="Copy to clipboard"
          >
            <Copy className="w-4 h-4" />
          </button>
          <pre>git clone {gitCloneUrl}</pre>
        </div>

        <div className="bg-green-50 border border-green-200 p-4">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> access to this repository requires you to supply your Code Candidate login credentials when prompted.
          </p>
        </div>
      </div>

      <div className="border border-gray-300 p-6 mb-6 max-w-5xl">
        <h2 className="text-xl font-medium mb-3">Instructions to candidate</h2>
        <p className="text-gray-700">
          No instructions have been provided for this challenge.{' '}
          <span className="text-blue-600 cursor-pointer">Why not add some?</span>
        </p>
      </div>

      <div className="max-w-5xl">
        <h2 className="text-3xl font-normal mb-4">Further Information</h2>
        <p className="text-gray-700">
          This repository linked above acts as a template for the challenge. When this challenge is assigned to a candidate,
          the contents of the main branch will be copied to a new repository created for the candidate. The commit history
          in their copy will be squashed down to a single 'Initial Commit'.
        </p>
      </div>
    </div>
  );
}
