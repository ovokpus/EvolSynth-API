"""
Core Pydantic models for EvolSynth API
Based on the LangGraph Evol-Instruct implementation
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvolutionType(str, Enum):
    """Evolution type enumeration matching the notebook implementation"""
    SIMPLE = "simple_evolution"
    MULTI_CONTEXT = "multi_context_evolution"
    REASONING = "reasoning_evolution"


class ExecutionMode(str, Enum):
    """Execution mode for the LangGraph workflow"""
    CONCURRENT = "concurrent"
    SEQUENTIAL = "sequential"


class DocumentInput(BaseModel):
    """Input document model"""
    content: str = Field(..., description="Document content text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    source: Optional[str] = Field(None, description="Document source identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "This document describes federal student loan programs and eligibility requirements...",
                "metadata": {"source": "loan_guide.pdf", "page": 1},
                "source": "loan_guide.pdf"
            }
        }


class EvolvedQuestion(BaseModel):
    """Evolved question model matching the notebook structure"""
    id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="The evolved question text")
    evolution_type: EvolutionType = Field(..., description="Type of evolution applied")
    source_context_ids: List[str] = Field(..., description="IDs of source contexts used")
    complexity_level: int = Field(..., ge=1, le=5, description="Question complexity level (1-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "q_12345",
                "question": "What are the specific eligibility requirements for federal student loans that require synthesis across multiple programs?",
                "evolution_type": "multi_context_evolution",
                "source_context_ids": ["ctx_001", "ctx_002"],
                "complexity_level": 3
            }
        }


class QuestionAnswer(BaseModel):
    """Question-answer pair model"""
    question_id: str = Field(..., description="ID of the associated question")
    answer: str = Field(..., description="Generated answer text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q_12345",
                "answer": "Federal student loan eligibility requires enrollment in an eligible program, satisfactory academic progress, financial need demonstration..."
            }
        }


class QuestionContext(BaseModel):
    """Question context model"""
    question_id: str = Field(..., description="ID of the associated question")
    contexts: List[str] = Field(..., description="Relevant context texts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q_12345",
                "contexts": [
                    "Federal Pell Grant eligibility requirements include...",
                    "Direct Loan program requirements specify..."
                ]
            }
        }


class GenerationSettings(BaseModel):
    """Settings for synthetic data generation"""
    execution_mode: ExecutionMode = Field(default=ExecutionMode.CONCURRENT, description="Execution mode for the workflow")
    max_base_questions_per_doc: int = Field(default=3, ge=1, le=10, description="Maximum base questions per document")
    simple_evolution_count: int = Field(default=3, ge=0, le=10, description="Number of simple evolution questions")
    multi_context_evolution_count: int = Field(default=2, ge=0, le=10, description="Number of multi-context evolution questions")
    reasoning_evolution_count: int = Field(default=2, ge=0, le=10, description="Number of reasoning evolution questions")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature setting")
    max_tokens: int = Field(default=500, ge=100, le=2000, description="Maximum tokens for LLM responses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_mode": "concurrent",
                "max_base_questions_per_doc": 3,
                "simple_evolution_count": 3,
                "multi_context_evolution_count": 2,
                "reasoning_evolution_count": 2,
                "temperature": 0.7,
                "max_tokens": 500
            }
        }


class PerformanceMetrics(BaseModel):
    """Performance metrics for generation runs"""
    execution_time_seconds: float = Field(..., description="Total execution time")
    questions_generated: int = Field(..., description="Total questions generated")
    answers_generated: int = Field(..., description="Total answers generated")
    contexts_extracted: int = Field(..., description="Total contexts extracted")
    questions_per_second: float = Field(..., description="Generation rate")
    execution_mode: str = Field(..., description="Execution mode used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_time_seconds": 25.64,
                "questions_generated": 7,
                "answers_generated": 7,
                "contexts_extracted": 7,
                "questions_per_second": 0.27,
                "execution_mode": "concurrent"
            }
        } 