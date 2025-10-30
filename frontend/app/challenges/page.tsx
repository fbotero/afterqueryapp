'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase, Challenge } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function ChallengesPage() {
  const router = useRouter();
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChallenges();
  }, []);

  async function loadChallenges() {
    const { data, error } = await supabase
      .from('challenges')
      .select('*')
      .order('created_at', { ascending: false });

    if (data) {
      setChallenges(data);
    }
    setLoading(false);
  }

  const availableChallenges = challenges.filter(c => c.status === 'available');
  const archivedChallenges = challenges.filter(c => c.status === 'archived');

  return (
    <div className="min-h-screen bg-white p-8">
      <h1 className="text-4xl font-normal mb-8">Challenges</h1>

      <div className="border border-gray-300 p-8 mb-8">
        <p className="mb-4 text-gray-700">To create a new challenge click below:</p>
        <Button
          className="bg-green-600 hover:bg-green-700 text-white px-6"
          onClick={() => router.push('/challenges/create')}
        >
          Create Challenge
        </Button>
      </div>

      <Tabs defaultValue="available" className="w-full">
        <TabsList className="bg-transparent border-b border-gray-300 rounded-none h-auto p-0 w-full justify-start">
          <TabsTrigger
            value="available"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-6 py-3"
          >
            Available
          </TabsTrigger>
          <TabsTrigger
            value="archived"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-blue-600 data-[state=active]:bg-transparent px-6 py-3"
          >
            Archived
          </TabsTrigger>
        </TabsList>

        <TabsContent value="available" className="mt-6">
          {loading ? (
            <p>Loading...</p>
          ) : availableChallenges.length === 0 ? (
            <p className="text-gray-500">No available challenges</p>
          ) : (
            <div className="space-y-4">
              {availableChallenges.map((challenge) => (
                <div
                  key={challenge.id}
                  className="border border-gray-300 p-6 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <h3 className="text-xl font-normal mb-2">{challenge.name}</h3>
                    <p className="text-sm text-gray-600">{challenge.git_repo || 'No repository'}</p>
                    <div className="mt-3 text-sm text-gray-600">
                      <p className="font-medium mb-1">Assignments</p>
                      <div className="grid grid-cols-2 gap-x-8 gap-y-1">
                        <span>1 total</span>
                        <span>1 in progress</span>
                        <span>0 outstanding</span>
                        <span>0 finished</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    className="bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => router.push(`/challenges/${challenge.id}`)}
                  >
                    Send to Candidate
                  </Button>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="archived" className="mt-6">
          {archivedChallenges.length === 0 ? (
            <p className="text-gray-500">No archived challenges</p>
          ) : (
            <div className="space-y-4">
              {archivedChallenges.map((challenge) => (
                <div
                  key={challenge.id}
                  className="border border-gray-300 p-6"
                >
                  <h3 className="text-xl font-normal">{challenge.name}</h3>
                </div>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
