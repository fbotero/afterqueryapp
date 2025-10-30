'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';

type StartView = {
  title: string;
  description?: string;
  instructions?: string;
  branch: string;
  start_deadline_at: string;
  complete_window_hours: number;
};

export default function CandidateStartPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<StartView | null>(null);
  const [cloneUrl, setCloneUrl] = useState<string | null>(null);
  const [repoHtmlUrl, setRepoHtmlUrl] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<'start' | 'refresh' | 'submit' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startDeadline = useMemo(() => (view ? new Date(view.start_deadline_at) : null), [view]);

  const fetchView = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/candidate/start/${token}`);
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      setView(json as StartView);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, [API_BASE, token]);

  useEffect(() => {
    fetchView();
  }, [fetchView]);

  async function doStart() {
    if (!token) return;
    setActionLoading('start');
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/candidate/start/${token}`, { method: 'POST' });
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      setCloneUrl(json.clone_url);
      setRepoHtmlUrl(json.repo_html_url);
    } catch (e: any) {
      setError(e?.message ?? 'Start failed');
    } finally {
      setActionLoading(null);
    }
  }

  async function doRefresh() {
    if (!token) return;
    setActionLoading('refresh');
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/candidate/refresh/${token}`, { method: 'POST' });
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      setCloneUrl(json.clone_url);
    } catch (e: any) {
      setError(e?.message ?? 'Refresh failed');
    } finally {
      setActionLoading(null);
    }
  }

  async function doSubmit() {
    if (!token) return;
    setActionLoading('submit');
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/candidate/submit/${token}`, { method: 'POST' });
      if (!res.ok) throw new Error(await res.text());
      await res.json();
      // After submit, disable further actions.
      setCloneUrl(null);
    } catch (e: any) {
      setError(e?.message ?? 'Submit failed');
    } finally {
      setActionLoading(null);
    }
  }

  function copy(text: string) {
    navigator.clipboard.writeText(text);
  }

  if (!token) {
    return <div className="p-8 text-red-600">Missing token</div>;
  }

  if (loading) {
    return <div className="p-8">Loading…</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-4xl font-normal mb-2">{view?.title ?? 'Assessment'}</h1>
      <div className="h-px bg-gray-300 mb-6"></div>

      {view?.description && <p className="text-gray-700 mb-4">{view.description}</p>}
      {view?.instructions && <p className="text-gray-700 mb-6">{view.instructions}</p>}

      <div className="border border-gray-300 p-6 mb-6 max-w-3xl">
        <div className="text-sm text-gray-700 mb-3">Branch: <span className="font-mono">{view?.branch ?? 'main'}</span></div>
        {startDeadline && (
          <div className="text-sm text-gray-700">Start before: {startDeadline.toLocaleString()}</div>
        )}
      </div>

      <div className="flex gap-3 mb-6">
        <Button className="bg-green-600 hover:bg-green-700 text-white" disabled={actionLoading === 'start'} onClick={doStart}>
          {actionLoading === 'start' ? 'Starting…' : 'Start'}
        </Button>
        <Button variant="outline" className="border-gray-300" disabled={actionLoading === 'refresh'} onClick={doRefresh}>
          {actionLoading === 'refresh' ? 'Refreshing…' : 'Refresh Git URL'}
        </Button>
        <Button variant="outline" className="border-gray-300" disabled={actionLoading === 'submit'} onClick={doSubmit}>
          {actionLoading === 'submit' ? 'Submitting…' : 'Submit'}
        </Button>
      </div>

      {cloneUrl && (
        <div className="border border-gray-300 p-6 max-w-3xl">
          <h2 className="text-xl font-medium mb-3">Clone Instructions</h2>
          <div className="bg-gray-50 border border-gray-300 p-4 mb-3 font-mono text-sm relative">
            <button
              onClick={() => copy(`git clone ${cloneUrl}`)}
              className="absolute top-2 right-2 p-2 bg-yellow-400 hover:bg-yellow-500 rounded"
              title="Copy"
            >
              Copy
            </button>
            <pre className="whitespace-pre-wrap">{`git clone ${cloneUrl}`}</pre>
          </div>
          {repoHtmlUrl && (
            <p className="text-sm text-gray-700">
              Repository: <a href={repoHtmlUrl} className="text-blue-600" target="_blank" rel="noreferrer">{repoHtmlUrl}</a>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
