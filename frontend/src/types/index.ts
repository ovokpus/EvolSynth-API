// =============================================================================
// CORE BACKEND TYPES (Matching FastAPI models)
// =============================================================================

export interface DocumentInput {
  content: string;
  metadata: Record<string, unknown>;
  source?: string;
}

export type EvolutionType = "simple_evolution" | "multi_context_evolution" | "reasoning_evolution" | "complex_evolution";
export type ExecutionMode = "concurrent" | "sequential";

export interface EvolvedQuestion {
  id: string;
  question: string;
  evolution_type: EvolutionType;
  complexity_level: number; // 1-5
}

export interface QuestionAnswer {
  question_id: string;
  answer: string;
}

// Enhanced context with source information
export interface EnhancedContext {
  text: string;
  source: string;
  document_index: number;
}

export interface QuestionContext {
  question_id: string;
  contexts: (string | EnhancedContext)[];  // Support both old and new format
}

export interface GenerationSettings {
  execution_mode: ExecutionMode;
  max_base_questions_per_doc: number;
  simple_evolution_count: number;
  multi_context_evolution_count: number;
  reasoning_evolution_count: number;
  complex_evolution_count: number;
  temperature: number;
  max_tokens: number;
}

export interface PerformanceMetrics {
  execution_time_seconds: number;
  questions_generated: number;
  answers_generated: number;
  contexts_extracted: number;
  questions_per_second: number;
  execution_mode: string;
}

// =============================================================================
// API REQUEST/RESPONSE TYPES
// =============================================================================

export interface GenerationRequest {
  documents: DocumentInput[];
  settings?: GenerationSettings;
  max_iterations: number;
  fast_mode: boolean;
  skip_evaluation: boolean;
}

export interface GenerationResponse {
  success: boolean;
  evolved_questions: EvolvedQuestion[];
  question_answers: QuestionAnswer[];
  question_contexts: QuestionContext[];
  performance_metrics: PerformanceMetrics;
  generation_id: string;
  timestamp: string;
}

export interface EvaluationRequest {
  evolved_questions: EvolvedQuestion[];
  question_answers: QuestionAnswer[];
  question_contexts: QuestionContext[];
  evaluation_metrics: string[];
}

export interface EvaluationResponse {
  success: boolean;
  evaluation_id: string;
  overall_scores: Record<string, number>;
  detailed_results: Record<string, unknown>;
  summary_statistics: Record<string, unknown>;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  dependencies: Record<string, string>;
}

// =============================================================================
// FRONTEND UI TYPES
// =============================================================================

// Frontend-specific document representation (before conversion to DocumentInput)
export interface UploadedDocument {
  id: string;
  source: string;
  content: string;
  metadata: Record<string, unknown>;
  size: number;
  type: string;
}

// Frontend generation settings (maps to backend GenerationSettings)
export interface FrontendGenerationSettings {
  evolutionLevels: number;
  questionsPerLevel: number;
  maxQuestions: number;
  // Individual evolution type counts
  simpleEvolutionCount: number;
  multiContextEvolutionCount: number;
  reasoningEvolutionCount: number;
  complexEvolutionCount: number;
  includeContextual: boolean;
  includeReasoning: boolean;
  evaluationEnabled: boolean;
  temperature: number;
  concurrentProcessing: boolean;
  fastMode: boolean;
  outputFormat: 'json' | 'csv' | 'both';
}

// Combined results for frontend display
export interface GenerationResults {
  success: boolean;
  generation_id: string;
  evolved_questions: EvolvedQuestion[];
  question_answers: QuestionAnswer[];
  question_contexts: QuestionContext[];
  performance_metrics: PerformanceMetrics;
  evaluation?: EvaluationResponse;
  settings?: FrontendGenerationSettings;
  documentsProcessed?: number;
  totalQuestions?: number;
  processingTime?: number;
  timestamp: string;
}

// Enhanced question type for frontend display
export interface DisplayQuestion {
  id: string;
  question: string;
  answer: string;
  context: (string | EnhancedContext)[] | string;  // Support enhanced contexts with source info
  level: string;
  metadata?: {
    confidence?: number;
    source?: string;
    complexity_level?: number;
    evolution_type?: EvolutionType;
  };
}

// =============================================================================
// COMPONENT PROPS
// =============================================================================

export interface DocumentUploadProps {
  documents: UploadedDocument[];
  setDocuments: (docs: UploadedDocument[]) => void;
  onNext: () => void;
}

export interface GenerationInterfaceProps {
  documents: UploadedDocument[];
  onComplete: (results: GenerationResults) => void;
  onBack: () => void;
}

export interface ResultsDisplayProps {
  results: GenerationResults | null;
  onReset: () => void;
}

// =============================================================================
// API ERROR TYPES
// =============================================================================

export interface APIError {
  detail: string;
  status_code?: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: APIError;
}

export type GenerationStatus = "idle" | "uploading" | "processing" | "generating" | "evaluating" | "completed" | "error";

export type GenerationStep = "upload" | "generate" | "results";

// =============================================================================
// HELPER FUNCTIONS TYPES
// =============================================================================

export interface ConversionHelpers {
  frontendToBackendDocument: (doc: UploadedDocument) => DocumentInput;
  frontendToBackendSettings: (settings: FrontendGenerationSettings) => GenerationSettings;
  backendToFrontendResults: (response: GenerationResponse, evaluation?: EvaluationResponse) => GenerationResults;
  backendToDisplayQuestions: (
    questions: EvolvedQuestion[], 
    answers: QuestionAnswer[], 
    contexts: QuestionContext[]
  ) => DisplayQuestion[];
} 