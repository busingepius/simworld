/**
 * TypeScript types mirroring the FastAPI backend schemas perfectly.
 */

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    detail: Record<string, any>;
  };
}

export interface Organisation {
  id: string;
  name: string;
  subscription_tier: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorldBase {
  name: string;
  domain: string;
  config: Record<string, any>;
}

export interface WorldCreate extends WorldBase {}

export interface WorldResponse extends WorldBase {
  id: string;
  org_id: string;
  status: string;
  agent_count: number;
  created_at: string;
  updated_at: string;
}

export interface AgentPersonaBase {
  name: string;
  personality: Record<string, any>;
  stance: Record<string, any>;
  influence_score: number;
}

export interface AgentPersonaResponse extends AgentPersonaBase {
  id: string;
  world_id: string;
  org_id: string;
  zep_user_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SimulationRunBase {
  scenario_id: string | null;
  rounds: number;
  platform_config: Record<string, any>;
}

export interface SimulationRunCreate extends SimulationRunBase {}

export interface SimulationRunResponse extends SimulationRunBase {
  id: string;
  world_id: string;
  org_id: string;
  status: 'queued' | 'running' | 'complete' | 'failed';
  llm_call_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScenarioBase {
  description: string;
  strength: number;
  target_agent_ids: string[];
}

export interface ScenarioCreate extends ScenarioBase {}

export interface ScenarioResponse extends ScenarioBase {
  id: string;
  world_id: string;
  org_id: string;
  linked_run_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReportSection {
  title: string;
  content: string;
}

export interface ReportBase {
  summary: string;
  sections: ReportSection[];
  confidence_score: number;
  motif_scene?: any;
}

export interface ReportResponse extends ReportBase {
  id: string;
  world_id: string;
  run_id: string;
  org_id: string;
  created_at: string;
  updated_at: string;
}

export interface CalibrationEntryBase {
  prediction_text: string;
  outcome_text: string;
  match_score: number;
}

export interface CalibrationEntryCreate extends CalibrationEntryBase {
  report_id: string;
}

export interface CalibrationEntryResponse extends CalibrationEntryBase {
  id: string;
  world_id: string;
  org_id: string;
  report_id: string;
  submitted_at: string;
  created_at: string;
  updated_at: string;
}
