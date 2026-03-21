"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { WorldResponse, AgentPersonaResponse, SimulationRunResponse, ReportResponse } from '@/lib/types';
import {
  ArrowLeftIcon,
  CloudArrowUpIcon,
  CpuChipIcon,
  PlayIcon,
  DocumentChartBarIcon,
  UserGroupIcon,
  DocumentTextIcon,
  BeakerIcon,
  ChartBarIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

export default function WorldDetailPage() {
  const params = useParams();
  const router = useRouter();
  const worldId = params.id as string;

  const [world, setWorld] = useState<WorldResponse | null>(null);
  const [agents, setAgents] = useState<AgentPersonaResponse[]>([]);
  const [simulations, setSimulations] = useState<SimulationRunResponse[]>([]);
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [seedFile, setSeedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [seedMode, setSeedMode] = useState<'upload' | 'generate'>('upload');
  const [seedPrompt, setSeedPrompt] = useState('');
  const [isGeneratingSeed, setIsGeneratingSeed] = useState(false);
  const [generateSuccess, setGenerateSuccess] = useState(false);
  const [generatedPreview, setGeneratedPreview] = useState('');

  useEffect(() => {
    fetchData();
  }, [worldId]);

  // Poll every 4s while there is any pending work:
  // - simulation is queued/running
  // - simulation just completed but no report has appeared yet
  // - agents are being generated
  useEffect(() => {
    const hasActiveSimulation = simulations.some(
      s => s.status === 'queued' || s.status === 'running'
    );
    const awaitingReport =
      simulations.some(s => s.status === 'complete') && reports.length === 0;

    if (!isGenerating && !hasActiveSimulation && !awaitingReport) return;

    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [simulations, reports, isGenerating]);

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
    } finally {
      setLoading(false);
    }
  };

  const handleSeedUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!seedFile) return;
    setIsUploading(true);
    setUploadSuccess(false);
    try {
      await api.uploadSeedMaterial(worldId, seedFile);
      setSeedFile(null);
      setUploadSuccess(true);
      // Clear the file input value visually
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      setTimeout(() => setUploadSuccess(false), 5000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateSeed = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!seedPrompt.trim()) return;
    setIsGeneratingSeed(true);
    setGenerateSuccess(false);
    setGeneratedPreview('');
    try {
      const result = await api.generateSeedMaterial(worldId, seedPrompt);
      setGeneratedPreview(result.preview);
      setSeedPrompt('');
      setGenerateSuccess(true);
      setTimeout(() => setGenerateSuccess(false), 6000);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setIsGeneratingSeed(false);
    }
  };

  const handleGenerateAgents = async () => {
    setIsGenerating(true);
    try {
      await api.generateAgents(worldId, 5);
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
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
    </div>
  );

  if (!world) return (
    <div className="text-center py-24">
      <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">World not found</h3>
      <p className="mt-1 text-sm text-gray-500">The world you're looking for doesn't exist or you don't have access.</p>
      <div className="mt-6">
        <button onClick={() => router.push('/dashboard')} className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          <ArrowLeftIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
          Back to Dashboard
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white dark:bg-[#111827] shadow-sm border border-gray-200 dark:border-gray-800 p-6 rounded-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl"></div>
        <div className="relative z-10 flex items-center gap-4">
          <button 
            onClick={() => router.push('/dashboard')}
            className="p-2 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
              {world.name}
              <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${
                world.status === 'active' 
                  ? 'bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-500/10 dark:text-green-400 dark:ring-green-500/20' 
                  : 'bg-gray-50 text-gray-600 ring-gray-500/10 dark:bg-gray-400/10 dark:text-gray-400 dark:ring-gray-400/20'
              }`}>
                {world.status}
              </span>
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1.5">
              <span className="font-medium text-gray-700 dark:text-gray-300">Domain:</span> {world.domain}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        
        {/* Knowledge Base */}
        <div className="bg-white dark:bg-[#111827] shadow-sm border border-gray-200 dark:border-gray-800 p-6 sm:p-8 rounded-2xl flex flex-col">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-xl">
              <DocumentTextIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Knowledge Base</h2>
              <p className="text-sm text-gray-500">Seed the world with source material</p>
            </div>
          </div>

          {/* Mode toggle */}
          <div className="flex rounded-xl bg-gray-100 dark:bg-gray-800 p-1 mb-5">
            <button
              type="button"
              onClick={() => setSeedMode('upload')}
              className={`flex-1 flex items-center justify-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                seedMode === 'upload'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <CloudArrowUpIcon className="w-4 h-4" />
              Upload File
            </button>
            <button
              type="button"
              onClick={() => setSeedMode('generate')}
              className={`flex-1 flex items-center justify-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                seedMode === 'generate'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <SparklesIcon className="w-4 h-4" />
              Generate with AI
            </button>
          </div>

          {seedMode === 'upload' ? (
            <form onSubmit={handleSeedUpload} className="mt-auto">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <input
                    type="file"
                    id="file-upload"
                    onChange={(e) => {
                      const file = e.target.files?.[0] || null;
                      setSeedFile(file);
                    }}
                    className="hidden"
                  />
                  <label
                    htmlFor="file-upload"
                    className="flex items-center justify-center w-full h-full min-h-[42px] px-4 py-2 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl cursor-pointer hover:border-indigo-500 dark:hover:border-indigo-400 bg-gray-50/50 dark:bg-gray-800/30 text-sm font-medium text-gray-600 dark:text-gray-300 transition-colors"
                  >
                    <CloudArrowUpIcon className="w-5 h-5 mr-2 text-gray-400" />
                    {seedFile ? seedFile.name : 'Choose a .txt file'}
                  </label>
                </div>
                <button
                  type="submit"
                  disabled={!seedFile || isUploading}
                  className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed sm:w-auto w-full"
                >
                  {isUploading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Uploading
                    </>
                  ) : 'Upload'}
                </button>
              </div>
              {uploadSuccess && (
                <p className="mt-3 text-sm text-green-600 dark:text-green-400 flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  File uploaded! Processing in background...
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleGenerateSeed} className="mt-auto flex flex-col gap-3">
              <textarea
                value={seedPrompt}
                onChange={(e) => setSeedPrompt(e.target.value)}
                placeholder="Describe your world... e.g. 'A space station orbiting Mars with a crew of scientists facing budget cuts and a mysterious signal from underground.'"
                rows={4}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/30 text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
              <button
                type="submit"
                disabled={!seedPrompt.trim() || isGeneratingSeed}
                className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingSeed ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="-ml-0.5 mr-2 h-4 w-4" />
                    Generate &amp; Ingest
                  </>
                )}
              </button>
              {generateSuccess && generatedPreview && (
                <div className="mt-1 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-4">
                  <p className="text-xs font-semibold text-green-700 dark:text-green-400 mb-2">Generated &amp; queued for processing</p>
                  <p className="text-xs text-green-800 dark:text-green-300 leading-relaxed line-clamp-5">{generatedPreview}</p>
                </div>
              )}
            </form>
          )}
        </div>

        {/* Agents */}
        <div className="bg-white dark:bg-[#111827] shadow-sm border border-gray-200 dark:border-gray-800 p-6 sm:p-8 rounded-2xl flex flex-col h-[400px]">
          <div className="flex justify-between items-start mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400 rounded-xl">
                <UserGroupIcon className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  Agents
                  <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-bold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full">
                    {agents.length}
                  </span>
                </h2>
                <p className="text-sm text-gray-500">Autonomous personas in this world</p>
              </div>
            </div>
            <button 
              onClick={handleGenerateAgents}
              disabled={isGenerating}
              className="inline-flex items-center justify-center rounded-xl bg-green-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CpuChipIcon className="-ml-0.5 mr-1.5 h-4 w-4" />
              {isGenerating ? 'Generating...' : 'Generate Agents'}
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
            {agents.map(agent => (
              <div key={agent.id} className="flex items-center justify-between p-4 border border-gray-100 dark:border-gray-800/60 rounded-xl bg-gray-50/30 dark:bg-gray-800/20 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                    {agent.name.charAt(0)}
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">{agent.name}</span>
                </div>
                <div className="flex items-center gap-1.5 bg-white dark:bg-gray-900 px-2.5 py-1 rounded-md border border-gray-200 dark:border-gray-700">
                  <ChartBarIcon className="w-3.5 h-3.5 text-gray-400" />
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-300">{agent.influence_score}</span>
                </div>
              </div>
            ))}
            {agents.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl">
                <UserGroupIcon className="w-10 h-10 text-gray-300 dark:text-gray-600 mb-2" />
                <p className="text-sm text-gray-500">No agents have been generated yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Simulations */}
        <div className="bg-white dark:bg-[#111827] shadow-sm border border-gray-200 dark:border-gray-800 p-6 sm:p-8 rounded-2xl flex flex-col h-[400px]">
          <div className="flex justify-between items-start mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-xl">
                <BeakerIcon className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Simulations</h2>
                <p className="text-sm text-gray-500">Run interaction scenarios</p>
              </div>
            </div>
            <button 
              onClick={handleRunSimulation}
              disabled={agents.length === 0}
              className="inline-flex items-center justify-center rounded-xl bg-purple-600 px-3.5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <PlayIcon className="-ml-0.5 mr-1.5 h-4 w-4 group-disabled:opacity-50" />
              Run Simulation
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
            {simulations.map(sim => (
              <div key={sim.id} className="flex items-center justify-between p-4 border border-gray-100 dark:border-gray-800/60 rounded-xl bg-gray-50/30 dark:bg-gray-800/20">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                    ID: {sim.id.split('-')[0]}...
                  </span>
                </div>
                <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                  sim.status === 'complete' ? 'bg-green-50 text-green-700 ring-green-600/20 dark:bg-green-500/10 dark:text-green-400' : 
                  sim.status === 'failed' ? 'bg-red-50 text-red-700 ring-red-600/20 dark:bg-red-500/10 dark:text-red-400' : 
                  'bg-yellow-50 text-yellow-800 ring-yellow-600/20 dark:bg-yellow-500/10 dark:text-yellow-400'
                }`}>
                  {sim.status}
                </span>
              </div>
            ))}
            {simulations.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl">
                <BeakerIcon className="w-10 h-10 text-gray-300 dark:text-gray-600 mb-2" />
                <p className="text-sm text-gray-500">No simulations run yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Reports */}
        <div className="bg-white dark:bg-[#111827] shadow-sm border border-gray-200 dark:border-gray-800 p-6 sm:p-8 rounded-2xl flex flex-col lg:col-span-2">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-xl">
              <DocumentChartBarIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Analysis Reports</h2>
              <p className="text-sm text-gray-500">Insights generated from simulation runs</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            {reports.map(report => (
              <div key={report.id} className="p-5 sm:p-6 border border-gray-100 dark:border-gray-800 rounded-2xl bg-gray-50/50 dark:bg-gray-800/30">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <ChartBarIcon className="w-5 h-5 text-indigo-500" />
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">Confidence Score</span>
                  </div>
                  <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${
                    report.confidence_score > 0.8 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                    report.confidence_score > 0.5 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                  }`}>
                    {(report.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
                
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
                  {report.summary}
                </p>
                
                <div className="space-y-3">
                  {report.sections.map((sec, idx) => (
                    <details key={idx} className="group bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
                      <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-gray-900 dark:text-white bg-gray-50/50 dark:bg-gray-800/50 group-open:bg-gray-100 dark:group-open:bg-gray-800 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-between">
                        {sec.title}
                        <span className="text-gray-400 group-open:rotate-180 transition-transform">▼</span>
                      </summary>
                      <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-800">
                        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                          {sec.content}
                        </p>
                      </div>
                    </details>
                  ))}
                </div>
              </div>
            ))}
            {reports.length === 0 && (
              <div className="flex flex-col items-center justify-center text-center p-10 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-2xl">
                <DocumentChartBarIcon className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-3" />
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">No reports available</h3>
                <p className="mt-1 text-sm text-gray-500">Run simulations to generate insights and analysis.</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
