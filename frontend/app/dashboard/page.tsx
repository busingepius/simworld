"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { WorldResponse } from '@/lib/types';
import { PlusIcon, GlobeAltIcon, ServerIcon, SignalIcon } from '@heroicons/react/24/outline';

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

  if (loading) return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
    </div>
  );

  if (error) return (
    <div className="rounded-xl bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800/30">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400 dark:text-red-500" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-300">Error loading worlds</h3>
          <div className="mt-2 text-sm text-red-700 dark:text-red-400">{error}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Simulated Worlds
          </h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Manage your agent-driven simulations across different domains.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={() => setIsCreating(true)}
            className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all active:scale-95"
          >
            <PlusIcon className="-ml-0.5 mr-2 h-5 w-5" aria-hidden="true" />
            New World
          </button>
        </div>
      </div>

      {isCreating && (
        <div className="bg-white dark:bg-[#111827] rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden ring-1 ring-black/5 dark:ring-white/5 animate-in fade-in slide-in-from-top-4 duration-300">
          <form onSubmit={handleCreate} className="p-6 sm:p-8">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Create New World</h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="worldName" className="block text-sm font-medium leading-6 text-gray-900 dark:text-gray-300">
                  World Name
                </label>
                <div className="mt-2">
                  <input
                    type="text"
                    id="worldName"
                    required
                    placeholder="e.g. Avalon"
                    className="block w-full rounded-xl border-0 py-2.5 text-gray-900 dark:text-white dark:bg-gray-800/50 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-700 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 transition-colors"
                    value={newWorldName}
                    onChange={(e) => setNewWorldName(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label htmlFor="worldDomain" className="block text-sm font-medium leading-6 text-gray-900 dark:text-gray-300">
                  Domain Segment
                </label>
                <div className="mt-2">
                  <input
                    type="text"
                    id="worldDomain"
                    required
                    placeholder="e.g. Politics, Economics"
                    className="block w-full rounded-xl border-0 py-2.5 text-gray-900 dark:text-white dark:bg-gray-800/50 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-700 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 transition-colors"
                    value={newWorldDomain}
                    onChange={(e) => setNewWorldDomain(e.target.value)}
                  />
                </div>
              </div>
            </div>
            <div className="mt-8 flex items-center justify-end gap-x-4">
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="text-sm font-semibold leading-6 text-gray-900 dark:text-gray-300 hover:text-gray-600 dark:hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all active:scale-95"
              >
                Create & Initialize
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:gap-8">
        {worlds.map(world => (
          <Link href={`/dashboard/worlds/${world.id}`} key={world.id} className="group flex flex-col bg-white dark:bg-[#111827] rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-md hover:border-indigo-500/50 dark:hover:border-indigo-400/50 transition-all duration-300 hover:-translate-y-1">
            <div className="p-6 flex-1">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                  <GlobeAltIcon className="w-6 h-6" />
                </div>
                <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                  world.status === 'active' 
                    ? 'bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-500/10 dark:text-green-400 dark:ring-green-500/20' 
                    : 'bg-gray-50 text-gray-600 ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-400 dark:ring-gray-400/20'
                }`}>
                  {world.status}
                </span>
              </div>
              <h3 className="mt-4 text-xl font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                {world.name}
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
                <ServerIcon className="w-4 h-4" />
                {world.domain}
              </p>
            </div>
            <div className="px-6 py-4 bg-gray-50/50 dark:bg-gray-800/30 border-t border-gray-100 dark:border-gray-800/50 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                <SignalIcon className="w-4 h-4 text-indigo-500" />
                {world.agent_count} <span className="text-gray-500 dark:text-gray-500 font-normal">Active Agents</span>
              </div>
              <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400 group-hover:translate-x-1 transition-transform">
                Enter →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {worlds.length === 0 && !isCreating && (
        <div className="text-center rounded-3xl border-2 border-dashed border-gray-300 dark:border-gray-800 px-6 py-16 sm:py-24 animate-in fade-in duration-500">
          <GlobeAltIcon className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No worlds initialized</h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
            Get started by creating your first simulated world. You can define the domain and let agents interact.
          </p>
          <div className="mt-8">
            <button
              onClick={() => setIsCreating(true)}
              className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all active:scale-95"
            >
              <PlusIcon className="-ml-0.5 mr-2 h-5 w-5" aria-hidden="true" />
              Create First World
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
