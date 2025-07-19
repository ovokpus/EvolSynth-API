"""
Response models for EvolSynth API
Pydantic models for API response validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from api.models.core import EvolvedQuestion, QuestionAnswer, QuestionContext, PerformanceMetrics


class GenerationResponse(BaseModel):
    """Response model for synthetic data generation"""
    success: bool = Field(..., description="Whether the generation was successful")
    evolved_questions: List[Dict[str, Any]] = Field(..., description="List of evolved questions with metadata")
    question_answers: List[Dict[str, Any]] = Field(..., description="List of question-answer pairs")
    question_contexts: List[Dict[str, Any]] = Field(..., description="List of question-context mappings")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics for the generation run")
    generation_id: str = Field(..., description="Unique identifier for this generation run")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "evolved_questions": [
                    {
                        "id": "q_001",
                        "question": "What are the specific eligibility requirements for federal student loans?",
                        "evolution_type": "simple_evolution",
                        "complexity_level": 2
                    }
                ],
                "question_answers": [
                    {
                        "question_id": "q_001",
                        "answer": "Federal student loan eligibility requires enrollment in an eligible program..."
                    }
                ],
                "question_contexts": [
                    {
                        "question_id": "q_001",
                        "contexts": ["Federal loan programs require...", "Eligibility criteria include..."]
                    }
                ],
                "performance_metrics": {
                    "execution_time_seconds": 25.64,
                    "questions_generated": 7,
                    "answers_generated": 7,
                    "contexts_extracted": 7,
                    "questions_per_second": 0.27,
                    "execution_mode": "concurrent"
                },
                "generation_id": "gen_12345",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class EvaluationResponse(BaseModel):
    """Response model for synthetic data evaluation"""
    success: bool = Field(..., description="Whether the evaluation was successful")
    evaluation_id: str = Field(..., description="Unique identifier for this evaluation run")
    overall_scores: Dict[str, float] = Field(..., description="Overall evaluation scores by metric")
    detailed_results: List[Dict[str, Any]] = Field(..., description="Detailed evaluation results per question")
    summary_statistics: Dict[str, Any] = Field(..., description="Summary statistics for the evaluation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Evaluation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "evaluation_id": "eval_12345",
                "overall_scores": {
                    "question_quality": 0.85,
                    "answer_accuracy": 0.78,
                    "evolution_effectiveness": 0.92
                },
                "detailed_results": [
                    {
                        "question_id": "q_001",
                        "question_quality": 0.9,
                        "answer_accuracy": 0.8,
                        "evolution_effectiveness": 1.0
                    }
                ],
                "summary_statistics": {
                    "total_questions_evaluated": 7,
                    "average_complexity": 2.8,
                    "evolution_type_distribution": {
                        "simple_evolution": 3,
                        "multi_context_evolution": 2,
                        "reasoning_evolution": 2
                    }
                },
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    dependencies: Dict[str, str] = Field(..., description="Status of external dependencies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-01T12:00:00",
                "dependencies": {
                    "openai": "connected",
                    "langsmith": "connected"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error cases"""
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid document format provided",
                "details": {
                    "field": "documents[0].content",
                    "issue": "Content cannot be empty"
                },
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class BatchGenerationResponse(BaseModel):
    """Response model for batch generation requests"""
    success: bool = Field(..., description="Whether the batch generation was successful")
    batch_results: List[GenerationResponse] = Field(..., description="Results for each batch")
    batch_names: Optional[List[str]] = Field(default=None, description="Names of processed batches")
    total_performance: PerformanceMetrics = Field(..., description="Aggregated performance metrics")
    batch_id: str = Field(..., description="Unique identifier for this batch run")
    timestamp: datetime = Field(default_factory=datetime.now, description="Batch processing timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "batch_results": [
                    # GenerationResponse objects for each batch
                ],
                "batch_names": ["Financial Aid Docs", "Loan Program Docs"],
                "total_performance": {
                    "execution_time_seconds": 45.32,
                    "questions_generated": 14,
                    "answers_generated": 14,
                    "contexts_extracted": 14,
                    "questions_per_second": 0.31,
                    "execution_mode": "concurrent"
                },
                "batch_id": "batch_12345",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class StatusResponse(BaseModel):
    """Response model for generation status checks"""
    generation_id: str = Field(..., description="Generation run identifier")
    status: str = Field(..., description="Current status (pending, running, completed, failed)")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0.0 to 1.0)")
    current_stage: str = Field(..., description="Current processing stage")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "generation_id": "gen_12345",
                "status": "running", 
                "progress": 0.65,
                "current_stage": "answer_generation",
                "estimated_completion": "2024-01-01T12:05:00"
            }
        } 