/**
 * Wrapper for the Fetch API providing typed requests to the FastAPI backend.
 */
import {
  WorldCreate,
  WorldResponse,
  AgentPersonaResponse,
  SimulationRunCreate,
  SimulationRunResponse,
  ScenarioCreate,
  ScenarioResponse,
  ReportResponse,
  CalibrationEntryCreate,
  CalibrationEntryResponse,
  ErrorResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  public code: string;
  public detail: Record<string, any>;
  public status: number;

  constructor(status: number, errorData: ErrorResponse['error']) {
    super(errorData.message);
    this.name = 'ApiError';
    this.code = errorData.code;
    this.detail = errorData.detail;
    this.status = status;
  }
}

/**
 * Core fetch wrapper that automatically handles Auth tokens and Error unwrapping
 */
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('simworld_token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If we're passing FormData (like for file uploads), remove Content-Type 
  // so the browser sets the correct multipart boundary automatically
  if (options.body && typeof (options.body as any).append === 'function') {
    delete (headers as Record<string, string>)['Content-Type'];
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: ErrorResponse['error'];
    try {
      const data = await response.json();
      errorData = data.error || { code: 'UNKNOWN', message: 'An unknown error occurred', detail: {} };
    } catch {
      errorData = { code: 'NETWORK_ERROR', message: response.statusText, detail: {} };
    }
    throw new ApiError(response.status, errorData);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // --- Worlds ---
  listWorlds: () => 
    fetchApi<WorldResponse[]>('/worlds/'),
    
  createWorld: (data: WorldCreate) => 
    fetchApi<WorldResponse>('/worlds/', { method: 'POST', body: JSON.stringify(data) }),
    
  getWorld: (worldId: string) => 
    fetchApi<WorldResponse>(`/worlds/${worldId}`),

  // --- Seed Material ---
  uploadSeedMaterial: (worldId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetchApi<{ status: string; material_id: string }>(`/worlds/${worldId}/seed`, {
      method: 'POST',
      body: formData,
    });
  },

  generateSeedMaterial: (worldId: string, prompt: string) =>
    fetchApi<{ status: string; material_id: string; preview: string }>(`/worlds/${worldId}/seed/generate`, {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    }),

  // --- Agents ---
  listAgents: (worldId: string) => 
    fetchApi<AgentPersonaResponse[]>(`/worlds/${worldId}/agents`),
    
  generateAgents: (worldId: string, count: number = 5) => 
    fetchApi<{ status: string; count: number }>(`/worlds/${worldId}/agents/generate?count=${count}`, { method: 'POST' }),

  // --- Simulations ---
  listSimulationRuns: (worldId: string) => 
    fetchApi<SimulationRunResponse[]>(`/worlds/${worldId}/runs`),
    
  createSimulationRun: (worldId: string, data: SimulationRunCreate) => 
    fetchApi<SimulationRunResponse>(`/worlds/${worldId}/runs`, { method: 'POST', body: JSON.stringify(data) }),

  // --- Scenarios ---
  listScenarios: (worldId: string) => 
    fetchApi<ScenarioResponse[]>(`/worlds/${worldId}/scenarios`),
    
  createScenario: (worldId: string, data: ScenarioCreate) => 
    fetchApi<ScenarioResponse>(`/worlds/${worldId}/scenarios`, { method: 'POST', body: JSON.stringify(data) }),

  // --- Reports ---
  listReports: (worldId: string) => 
    fetchApi<ReportResponse[]>(`/worlds/${worldId}/reports`),
    
  getReport: (worldId: string, reportId: string) => 
    fetchApi<ReportResponse>(`/worlds/${worldId}/reports/${reportId}`),

  // --- Calibrations ---
  listCalibrations: (worldId: string) => 
    fetchApi<CalibrationEntryResponse[]>(`/worlds/${worldId}/calibrations`),
    
  createCalibration: (worldId: string, data: CalibrationEntryCreate) => 
    fetchApi<CalibrationEntryResponse>(`/worlds/${worldId}/calibrations`, { method: 'POST', body: JSON.stringify(data) }),
};
