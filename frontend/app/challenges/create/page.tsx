'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function CreateChallengePage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  async function handleCreate() {
    if (!name.trim()) return;

    setLoading(true);
    setError(null);
    try {
      // Create challenge using backend API with sensible defaults
      const res = await fetch(`${API_BASE}/api/admin/challenges`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: name.trim(),
          description: null,
          instructions: null,
          seed_github_url: 'https://github.com/fbotero/afterqueryexampe',
          start_window_hours: 72,
          complete_window_hours: 168,
          email_subject: null,
          email_body: null,
          slug: name.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || 'Failed to create challenge');
      }

      const json = await res.json();
      if (json?.challenge?.id) {
        router.push(`/challenges/${json.challenge.id}`);
      }
    } catch (e: any) {
      setError(e?.message ?? 'Failed to create challenge');
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-4xl font-normal mb-4">Create a Challenge</h1>

      <p className="text-gray-700 mb-2">Create a new challenge that can be sent out to a candidate.</p>
      <p className="text-gray-700 mb-8">Your challenge's name is shown to candidates. Make it brief, but informative.</p>

      <div className="max-w-md">
        <div className="mb-6 text-center">
          <Label htmlFor="challengeName" className="block text-lg mb-3">
            Challenge Name
          </Label>
          <Input
            id="challengeName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleCreate();
              }
            }}
          />
        </div>

        {error && (
          <div className="mb-4 text-red-600 text-sm text-center">{error}</div>
        )}

        <div className="text-center">
          <Button
            className="bg-green-600 hover:bg-green-700 text-white px-8"
            onClick={handleCreate}
            disabled={!name.trim() || loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </div>
      </div>
    </div>
  );
}
