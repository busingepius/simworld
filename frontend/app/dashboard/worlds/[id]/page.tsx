"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { WorldResponse, AgentPersonaResponse, SimulationRunResponse, ReportResponse } from '@/lib/types';

export default function WorldDetailPage() {
  const params = useParams();
  const worldId = params.id as string;

  const [world, setWorld] = useState<WorldResponse | null>(null);
  const [agents, setAgents] = useState<AgentPersonaResponse[]>([]);
  const [simulations, setSimulations] = useState<SimulationRunResponse[]>([]);
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [seedFile, setSeedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    fetchData();
    // In a real app we'd poll or use websockets here
  }, [worldId]);

  const fetchData = async () => {
    try {
      const [w, a, s, r] = await Promise.all([
        api.getWorld(worldId),
        api.listAgents(worldId),
        api.listSimulationRuns(worldId),
        api.listReports(worldId)
      ]);
      setWorld(w);
      setAgents(a);
      setSimulations(s);
      setReports(r);
    } catch (err: any) {
      console.error(err);
      alert('Failed to load world data');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!seedFile) return;
    setIsUploading(true);
    try {
      await api.uploadSeedMaterial(worldId, seedFile);
      alert('Seed material uploaded and is processing via Celery!');
      setSeedFile(null);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateAgents = async () => {
    setIsGenerating(true);
    try {
      await api.generateAgents(worldId, 5);
      alert('Agents generated!');
      fetchData();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRunSimulation = async () => {
    try {
      await api.createSimulationRun(worldId, {
        rounds: 3,
        platform_config: {},
        scenario_id: null
      });
      alert('Simulation queued!');
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (!world) return <div className="p-4 text-red-500">World not found.</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow p-6 rounded-lg">
        <h1 className="text-3xl font-bold dark:text-white">{world.name}</h1>
        <p className="text-gray-500 mt-2">Domain: {world.domain} | Status: {world.status}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Knowledge Base */}
        <div className="bg-white dark:bg-gray-800 shadow p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Knowledge Base (Seed Material)</h2>
          <form onSubmit={handleSeedUpload} className="flex gap-4 items-center">
            <input 
              type="file" 
              onChange={(e) => setSeedFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
            <button 
              type="submit" 
              disabled={!seedFile || isUploading}
              className="bg-indigo-600 disabled:bg-gray-400 text-white px-4 py-2 rounded"
            >
              {isUploading ? 'Uploading...' : 'Upload'}
            </button>
          </form>
        </div>

        {/* Agents */}
        <div className="bg-white dark:bg-gray-800 shadow p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold dark:text-white">Agents ({agents.length})</h2>
            <button 
              onClick={handleGenerateAgents}
              disabled={isGenerating}
              className="bg-green-600 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
            >
              {isGenerating ? 'Generating...' : 'Generate AI Agents'}
            </button>
          </div>
          <div className="max-h-60 overflow-y-auto space-y-2">
            {agents.map(agent => (
              <div key={agent.id} className="p-3 border rounded dark:border-gray-700">
                <span className="font-medium dark:text-white">{agent.name}</span>
                <span className="text-xs ml-2 text-gray-500">Influence: {agent.influence_score}</span>
              </div>
            ))}
            {agents.length === 0 && <p className="text-gray-500">No agents yet.</p>}
          </div>
        </div>

        {/* Simulations */}
        <div className="bg-white dark:bg-gray-800 shadow p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold dark:text-white">Simulations</h2>
            <button 
              onClick={handleRunSimulation}
              disabled={agents.length === 0}
              className="bg-purple-600 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm"
            >
              Run Simulation
            </button>
          </div>
          <div className="space-y-2">
            {simulations.map(sim => (
              <div key={sim.id} className="p-3 border rounded flex justify-between dark:border-gray-700">
                <span className="dark:text-white text-sm">ID: {sim.id.split('-')[0]}...</span>
                <span className={`text-sm ${sim.status === 'complete' ? 'text-green-500' : sim.status === 'failed' ? 'text-red-500' : 'text-yellow-500'}`}>
                  {sim.status}
                </span>
              </div>
            ))}
            {simulations.length === 0 && <p className="text-gray-500">No simulations run yet.</p>}
          </div>
        </div>

        {/* Reports */}
        <div className="bg-white dark:bg-gray-800 shadow p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 dark:text-white">Reports</h2>
          <div className="space-y-4">
            {reports.map(report => (
              <div key={report.id} className="p-4 border rounded dark:border-gray-700">
                <h3 className="font-medium dark:text-white">Confidence: {(report.confidence_score * 100).toFixed(1)}%</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{report.summary}</p>
                <div className="mt-2">
                  {report.sections.map((sec, idx) => (
                    <details key={idx} className="mb-1">
                      <summary className="cursor-pointer text-sm font-medium text-indigo-600">{sec.title}</summary>
                      <p className="text-sm mt-1 text-gray-700 dark:text-gray-300 pl-4">{sec.content}</p>
                    </details>
                  ))}
                </div>
              </div>
            ))}
            {reports.length === 0 && <p className="text-gray-500">No reports generated yet.</p>}
          </div>
        </div>

      </div>
    </div>
  );
}
