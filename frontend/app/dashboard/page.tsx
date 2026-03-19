"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { WorldResponse } from '@/lib/types';

export default function DashboardPage() {
  const [worlds, setWorlds] = useState<WorldResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [newWorldName, setNewWorldName] = useState('');
  const [newWorldDomain, setNewWorldDomain] = useState('');

  const fetchWorlds = async () => {
    try {
      const data = await api.listWorlds();
      setWorlds(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorlds();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createWorld({
        name: newWorldName,
        domain: newWorldDomain,
        config: {}
      });
      setIsCreating(false);
      setNewWorldName('');
      setNewWorldDomain('');
      fetchWorlds();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="p-4">Loading worlds...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Your Worlds</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Create New World
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="mb-8 p-4 bg-white dark:bg-gray-800 rounded shadow">
          <h2 className="text-lg font-medium mb-4 dark:text-white">Create a New World</h2>
          <div className="flex gap-4">
            <input
              type="text"
              required
              placeholder="World Name"
              className="flex-1 p-2 border rounded dark:bg-gray-700 dark:text-white dark:border-gray-600"
              value={newWorldName}
              onChange={(e) => setNewWorldName(e.target.value)}
            />
            <input
              type="text"
              required
              placeholder="Domain (e.g. Politics)"
              className="flex-1 p-2 border rounded dark:bg-gray-700 dark:text-white dark:border-gray-600"
              value={newWorldDomain}
              onChange={(e) => setNewWorldDomain(e.target.value)}
            />
            <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
              Save
            </button>
            <button type="button" onClick={() => setIsCreating(false)} className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {worlds.map(world => (
          <Link href={`/dashboard/worlds/${world.id}`} key={world.id}>
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg p-5 cursor-pointer hover:border-indigo-500 border-2 border-transparent transition">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">{world.name}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Domain: {world.domain}</p>
              <div className="mt-4 flex justify-between text-sm">
                <span className="text-gray-500">Status: {world.status}</span>
                <span className="text-gray-500">Agents: {world.agent_count}</span>
              </div>
            </div>
          </Link>
        ))}
        {worlds.length === 0 && !isCreating && (
          <div className="col-span-full text-center py-12 text-gray-500">
            You don't have any worlds yet. Create one to get started.
          </div>
        )}
      </div>
    </div>
  );
}
