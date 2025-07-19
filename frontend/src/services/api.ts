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
  APIError,
  DisplayQuestion,
  EvolvedQuestion,
  QuestionAnswer,
  QuestionContext,
  ExecutionMode,
} from '@/types';

// =============================================================================
// API CONFIGURATION
// =============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
      simple_evolution_count: settings.evolutionLevels >= 1 ? settings.questionsPerLevel : 0,
      multi_context_evolution_count: settings.evolutionLevels >= 2 && settings.includeContextual ? settings.questionsPerLevel : 0,
      reasoning_evolution_count: settings.evolutionLevels >= 3 && settings.includeReasoning ? settings.questionsPerLevel : 0,
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

    return questions.map(q => ({
      id: q.id,
      question: q.question,
      answer: answerMap.get(q.id) || 'No answer available',
      context: contextMap.get(q.id) || [],
      level: this.mapEvolutionTypeToLevel(q.evolution_type),
      metadata: {
        complexity_level: q.complexity_level,
        evolution_type: q.evolution_type,
        source: q.source_context_ids.join(', '),
      },
    }));
  }

  private mapEvolutionTypeToLevel(evolutionType: string): string {
    switch (evolutionType) {
      case 'simple_evolution':
        return 'simple';
      case 'multi_context_evolution':
        return 'multi-context';
      case 'reasoning_evolution':
        return 'reasoning';
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
      documentsProcessed: response.evolved_questions.reduce((acc, q) => {
        return Math.max(acc, q.source_context_ids.length);
      }, 0),
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

  async generateSyntheticData(
    documents: UploadedDocument[],
    settings: FrontendGenerationSettings
  ): Promise<APIResponse<GenerationResults>> {
    try {
      // Convert frontend data to backend format
      const backendDocuments = documents.map(doc => this.frontendToBackendDocument(doc));
      const backendSettings = this.frontendToBackendSettings(settings);

      const request: GenerationRequest = {
        documents: backendDocuments,
        settings: backendSettings,
        max_iterations: 1,
      };

      // Call generation endpoint
      const generationResponse = await this.request<GenerationResponse>('/generate', {
        method: 'POST',
        body: JSON.stringify(request),
      });

      if (!generationResponse.success || !generationResponse.data) {
        return generationResponse as APIResponse<GenerationResults>;
      }

      // Optionally call evaluation endpoint if enabled
      let evaluationResponse: EvaluationResponse | undefined;
      if (settings.evaluationEnabled && generationResponse.data.evolved_questions.length > 0) {
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
        }
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