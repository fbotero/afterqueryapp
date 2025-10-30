'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function InviteCandidatePage() {
  const params = useParams();
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  async function sendInvite() {
    if (!email) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/challenges/${params.id}/invites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_email: email, candidate_name: name || undefined }),
      });
      if (!res.ok) throw new Error(await res.text());
      alert('Invite sent');
      router.push(`/challenges/${params.id}`);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to send invite');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-4xl font-normal mb-6">Send to Candidate</h1>
      <div className="border border-gray-300 p-6 max-w-lg">
        <div className="mb-4">
          <label className="block text-sm text-gray-700 mb-1">Candidate Name</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
        </div>
        <div className="mb-6">
          <label className="block text-sm text-gray-700 mb-1">Candidate Email</label>
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="jane@example.com" />
        </div>
        {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
        <div className="flex gap-3">
          <Button className="bg-green-600 hover:bg-green-700 text-white" onClick={sendInvite} disabled={!email || loading}>
            {loading ? 'Sending…' : 'Send Invite'}
          </Button>
          <Button variant="outline" className="border-gray-300" onClick={() => router.push(`/challenges/${params.id}`)}>
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
}

