import {
  DocumentInput,
  UploadedDocument,
  GenerationRequest,
  GenerationResponse,
  GenerationResults,
  FrontendGenerationSettings,
  GenerationSettings,
  EvaluationRequest,
  EvaluationResponse,
  HealthResponse,
  APIResponse,
  DisplayQuestion,
  EvolvedQuestion,
  QuestionAnswer,
  QuestionContext,
  ExecutionMode,
} from '@/types';

import { API_CONFIG } from '@/lib/constants';

// =============================================================================
// LOGGING UTILITY
// =============================================================================

const logger = {
  info: (message: string, data?: unknown) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`ℹ️ ${message}`, data ? data : '');
    }
  },
  success: (message: string, data?: unknown) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${message}`, data ? data : '');
    }
  },
  warn: (message: string, data?: unknown) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn(`⚠️ ${message}`, data ? data : '');
    }
  },
};

// =============================================================================
// API CONFIGURATION
// =============================================================================

const API_BASE_URL = API_CONFIG.BASE_URL;

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: {
            detail: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
            status_code: response.status,
          },
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      return {
        success: false,
        error: {
          detail: error instanceof Error ? error.message : 'Network error occurred',
        },
      };
    }
  }

  // =============================================================================
  // CONVERSION HELPERS
  // =============================================================================

  private frontendToBackendDocument(doc: UploadedDocument): DocumentInput {
    return {
      content: doc.content,
      metadata: {
        ...doc.metadata,
        filename: doc.source,
        size: doc.size,
        type: doc.type,
        uploadedAt: doc.metadata.uploadedAt || new Date().toISOString(),
      },
      source: doc.source,
    };
  }

  private frontendToBackendSettings(settings: FrontendGenerationSettings): GenerationSettings {
    return {
      execution_mode: settings.concurrentProcessing ? 'concurrent' : 'sequential' as ExecutionMode,
      max_base_questions_per_doc: Math.ceil(settings.questionsPerLevel / settings.evolutionLevels),
      simple_evolution_count: settings.simpleEvolutionCount,
      multi_context_evolution_count: settings.multiContextEvolutionCount,
      reasoning_evolution_count: settings.reasoningEvolutionCount,
      complex_evolution_count: settings.complexEvolutionCount,
      temperature: settings.temperature,
      max_tokens: 500, // Default value
    };
  }

  private backendToDisplayQuestions(
    questions: EvolvedQuestion[],
    answers: QuestionAnswer[],
    contexts: QuestionContext[]
  ): DisplayQuestion[] {
    const answerMap = new Map(answers.map(a => [a.question_id, a.answer]));
    const contextMap = new Map(contexts.map(c => [c.question_id, c.contexts]));

    return questions.map(q => {
      const contextData = contextMap.get(q.id) || [];
      
      return {
        id: q.id,
        question: q.question,
        answer: answerMap.get(q.id) || 'No answer available',
        context: contextData,
        level: this.mapEvolutionTypeToLevel(q.evolution_type),
        metadata: {
          complexity_level: q.complexity_level,
          evolution_type: q.evolution_type,
          source: q.id || 'unknown',
        },
      };
    });
  }

  private mapEvolutionTypeToLevel(evolutionType: string): string {
    switch (evolutionType) {
      case 'simple_evolution':
        return 'simple';
      case 'multi_context_evolution':
        return 'multi-context';
      case 'reasoning_evolution':
        return 'reasoning';
      case 'complex_evolution':
        return 'complex';
      default:
        return 'unknown';
    }
  }

  private backendToFrontendResults(
    response: GenerationResponse,
    evaluation?: EvaluationResponse,
    originalSettings?: FrontendGenerationSettings
  ): GenerationResults {

    
    return {
      success: response.success,
      generation_id: response.generation_id,
      evolved_questions: response.evolved_questions,
      question_answers: response.question_answers,
      question_contexts: response.question_contexts,
      performance_metrics: response.performance_metrics,
      evaluation,
      settings: originalSettings,
      documentsProcessed: response.question_contexts.reduce((acc, qc) => {
        const contextCount = Array.isArray(qc.contexts) ? qc.contexts.length : 1;
        return Math.max(acc, contextCount);
      }, 1),
      totalQuestions: response.evolved_questions.length,
      processingTime: response.performance_metrics.execution_time_seconds,
      timestamp: response.timestamp,
    };
  }

  // =============================================================================
  // API METHODS
  // =============================================================================

  async healthCheck(): Promise<APIResponse<HealthResponse>> {
    return this.request<HealthResponse>('/health');
  }

  async checkGenerationStatus(generationId: string): Promise<APIResponse<{
    status: string;
    progress: number;
    current_stage: string;
    start_time: string;
    error?: string;
  }>> {
    return this.request<{
      status: string;
      progress: number;
      current_stage: string;
      start_time: string;
      error?: string;
    }>(`/generate/status/${generationId}`);
  }

  async extractFileContent(file: File): Promise<APIResponse<{
    success: boolean;
    filename: string;
    content: string;
    metadata: {
      file_size: number;
      file_type: string;
      pages_or_chunks: number;
      content_length: number;
    };
  }>> {
    const formData = new FormData();
    formData.append('file', file);

    // For file uploads, we need to handle the request differently
    const url = `${this.baseURL}/upload/extract-content`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type - let browser handle multipart/form-data
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        return {
          success: false,
          error: { detail: errorData.detail || `HTTP ${response.status}: ${response.statusText}` },
          data: undefined,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
        error: undefined,
      };
    } catch (error) {
      return {
        success: false,
        error: { detail: error instanceof Error ? error.message : 'Network error' },
        data: undefined,
      };
    }
  }

  async generateSyntheticData(
    documents: UploadedDocument[],
    settings: FrontendGenerationSettings,
    onProgress?: (progress: number, stage: string) => void
  ): Promise<APIResponse<GenerationResults>> {
    try {
      // Convert frontend data to backend format
      const backendDocuments = documents.map(doc => this.frontendToBackendDocument(doc));
      const backendSettings = this.frontendToBackendSettings(settings);

      const request: GenerationRequest = {
        documents: backendDocuments,
        settings: backendSettings,
        max_iterations: 1,
        fast_mode: settings.fastMode,  // Enable ultra-fast generation if selected
        skip_evaluation: !settings.evaluationEnabled,  // Skip evaluation if disabled
      };

      // Call generation endpoint
      const generationResponse = await this.request<GenerationResponse>('/generate', {
        method: 'POST',
        body: JSON.stringify(request),
      });

      // If onProgress callback is provided, report completion since backend returns immediately
      if (onProgress && generationResponse.success) {
        onProgress(100, 'completed');
      }

      if (!generationResponse.success || !generationResponse.data) {
        return generationResponse as APIResponse<GenerationResults>;
      }

      // Optionally call evaluation endpoint if enabled
      let evaluationResponse: EvaluationResponse | undefined;
      if (settings.evaluationEnabled && generationResponse.data.evolved_questions.length > 0) {
        try {
          logger.info('Calling evaluation endpoint...');
          const evalRequest: EvaluationRequest = {
            evolved_questions: generationResponse.data.evolved_questions,
            question_answers: generationResponse.data.question_answers,
            question_contexts: generationResponse.data.question_contexts,
            evaluation_metrics: ['question_quality', 'answer_accuracy', 'evolution_effectiveness'],
          };

          const evalResult = await this.request<EvaluationResponse>('/evaluate', {
            method: 'POST',
            body: JSON.stringify(evalRequest),
          });

          if (evalResult.success && evalResult.data) {
            evaluationResponse = evalResult.data;
            logger.success('Evaluation completed', evaluationResponse.overall_scores);
          } else {
                          logger.warn('Evaluation failed', evalResult.error);
          }
        } catch (error) {
          console.error('❌ Evaluation error:', error);
          // Continue without evaluation rather than failing the entire request
        }
      } else {
        logger.warn(`Evaluation skipped: enabled=${settings.evaluationEnabled}, questions=${generationResponse.data.evolved_questions.length}`);
      }

      // Convert to frontend format
      const frontendResults = this.backendToFrontendResults(
        generationResponse.data,
        evaluationResponse,
        settings
      );
      


      return {
        success: true,
        data: frontendResults,
      };
    } catch (error) {
      return {
        success: false,
        error: {
          detail: error instanceof Error ? error.message : 'Failed to generate synthetic data',
        },
      };
    }
  }

  async evaluateSyntheticData(
    questions: EvolvedQuestion[],
    answers: QuestionAnswer[],
    contexts: QuestionContext[]
  ): Promise<APIResponse<EvaluationResponse>> {
    const request: EvaluationRequest = {
      evolved_questions: questions,
      question_answers: answers,
      question_contexts: contexts,
      evaluation_metrics: ['question_quality', 'answer_accuracy', 'evolution_effectiveness'],
    };

    return this.request<EvaluationResponse>('/evaluate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  getDisplayQuestions(results: GenerationResults): DisplayQuestion[] {
    return this.backendToDisplayQuestions(
      results.evolved_questions,
      results.question_answers,
      results.question_contexts
    );
  }

  async checkBackendConnection(): Promise<boolean> {
    const health = await this.healthCheck();
    return health.success && health.data?.status === 'healthy';
  }
}

// =============================================================================
// EXPORT SINGLETON INSTANCE
// =============================================================================

export const apiClient = new APIClient();

// =============================================================================
// EXPORTED FUNCTIONS FOR COMPONENT USE
// =============================================================================

export async function generateSyntheticData(
  documents: UploadedDocument[],
  settings: FrontendGenerationSettings
): Promise<GenerationResults> {
  const response = await apiClient.generateSyntheticData(documents, settings);
  
  if (!response.success || !response.data) {
    throw new Error(response.error?.detail || 'Failed to generate synthetic data');
  }
  
  return response.data;
}

export async function evaluateSyntheticData(
  questions: EvolvedQuestion[],
  answers: QuestionAnswer[],
  contexts: QuestionContext[]
): Promise<EvaluationResponse> {
  const response = await apiClient.evaluateSyntheticData(questions, answers, contexts);
  
  if (!response.success || !response.data) {
    throw new Error(response.error?.detail || 'Failed to evaluate synthetic data');
  }
  
  return response.data;
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await apiClient.healthCheck();
  
  if (!response.success || !response.data) {
    throw new Error(response.error?.detail || 'Backend health check failed');
  }
  
  return response.data;
}

export function getDisplayQuestions(results: GenerationResults): DisplayQuestion[] {
  return apiClient.getDisplayQuestions(results);
}

export async function isBackendConnected(): Promise<boolean> {
  return apiClient.checkBackendConnection();
}

export async function extractFileContent(file: File) {
  return apiClient.extractFileContent(file);
} 