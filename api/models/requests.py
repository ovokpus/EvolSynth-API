"""
Request models for EvolSynth API
Pydantic models for API request validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from api.models.core import DocumentInput, GenerationSettings


class GenerationRequest(BaseModel):
    """Request model for synthetic data generation"""
    documents: List[DocumentInput] = Field(..., min_length=1, max_length=10, description="Input documents for synthetic data generation")
    settings: Optional[GenerationSettings] = Field(default=None, description="Generation settings (uses defaults if not provided)")
    max_iterations: int = Field(default=1, ge=1, le=5, description="Maximum number of generation iterations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "content": "Federal student loan programs provide funding for undergraduate and graduate students...",
                        "metadata": {"source": "loan_guide.pdf"},
                        "source": "loan_guide.pdf"
                    },
                    {
                        "content": "Pell Grant eligibility requirements include financial need demonstration...", 
                        "metadata": {"source": "pell_grant_guide.pdf"},
                        "source": "pell_grant_guide.pdf"
                    }
                ],
                "settings": {
                    "execution_mode": "concurrent",
                    "simple_evolution_count": 3,
                    "multi_context_evolution_count": 2,
                    "reasoning_evolution_count": 2
                },
                "max_iterations": 1
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request model for document upload and processing"""
    files: List[str] = Field(..., description="List of file paths or base64 encoded files")
    extract_text: bool = Field(default=True, description="Whether to extract text from documents")
    chunk_size: int = Field(default=1000, ge=100, le=5000, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=50, ge=0, le=500, description="Overlap between text chunks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "files": ["document1.pdf", "document2.pdf"],
                "extract_text": True,
                "chunk_size": 1000,
                "chunk_overlap": 50
            }
        }


class EvaluationRequest(BaseModel):
    """Request model for evaluating generated synthetic data"""
    evolved_questions: List[dict] = Field(..., description="List of evolved questions to evaluate")
    question_answers: List[dict] = Field(..., description="List of question-answer pairs")
    question_contexts: List[dict] = Field(..., description="List of question-context mappings")
    evaluation_metrics: List[str] = Field(
        default=["question_quality", "answer_accuracy", "evolution_effectiveness"],
        description="Metrics to evaluate"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "evolved_questions": [
                    {
                        "id": "q_001",
                        "question": "What are the eligibility requirements...",
                        "evolution_type": "simple_evolution",
                        "complexity_level": 2
                    }
                ],
                "question_answers": [
                    {
                        "question_id": "q_001",
                        "answer": "The eligibility requirements include..."
                    }
                ],
                "question_contexts": [
                    {
                        "question_id": "q_001", 
                        "contexts": ["Context text 1", "Context text 2"]
                    }
                ],
                "evaluation_metrics": ["question_quality", "answer_accuracy"]
            }
        }


class BatchGenerationRequest(BaseModel):
    """Request model for batch processing multiple document sets"""
    document_batches: List[List[DocumentInput]] = Field(..., description="List of document batches to process")
    settings: Optional[GenerationSettings] = Field(default=None, description="Generation settings for all batches")
    batch_names: Optional[List[str]] = Field(default=None, description="Optional names for each batch")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_batches": [
                    [
                        {"content": "Document 1 content...", "source": "doc1.pdf"},
                        {"content": "Document 2 content...", "source": "doc2.pdf"}
                    ],
                    [
                        {"content": "Document 3 content...", "source": "doc3.pdf"}
                    ]
                ],
                "batch_names": ["Financial Aid Docs", "Loan Program Docs"]
            }
        } 