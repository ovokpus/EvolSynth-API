"""
EvolSynth API - Main FastAPI Application
Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Local imports
from api.config import settings, validate_api_keys, setup_environment
from api.models.requests import GenerationRequest, EvaluationRequest, BatchGenerationRequest
from api.models.responses import (
    GenerationResponse, EvaluationResponse, HealthResponse, 
    ErrorResponse, BatchGenerationResponse, StatusResponse
)
from api.models.core import DocumentInput, PerformanceMetrics
from api.services.evol_instruct_service import EvolInstructService
from api.services.evaluation_service import EvaluationService
from api.services.document_service import DocumentService

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
evol_instruct_service: Optional[EvolInstructService] = None
evaluation_service: Optional[EvaluationService] = None
document_service: Optional[DocumentService] = None

# Generation status tracking
generation_status: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services and validate configuration on startup"""
    global evol_instruct_service, evaluation_service, document_service
    
    try:
        # Validate API keys
        validate_api_keys()
        setup_environment()
        
        # Initialize services
        evol_instruct_service = EvolInstructService()
        evaluation_service = EvaluationService()
        document_service = DocumentService()
        
        print(f"✅ {settings.app_name} started successfully")
        print(f"📊 Environment: {'Development' if settings.debug else 'Production'}")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


def get_evol_instruct_service() -> EvolInstructService:
    """Dependency to get EvolInstructService instance"""
    if evol_instruct_service is None:
        raise HTTPException(status_code=500, detail="EvolInstruct service not initialized")
    return evol_instruct_service


def get_evaluation_service() -> EvaluationService:
    """Dependency to get EvaluationService instance"""
    if evaluation_service is None:
        raise HTTPException(status_code=500, detail="Evaluation service not initialized")
    return evaluation_service


def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    if document_service is None:
        raise HTTPException(status_code=500, detail="Document service not initialized")
    return document_service


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns API information"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        dependencies={
            "openai": "connected" if settings.openai_api_key else "not configured",
            "langsmith": "connected" if settings.langchain_api_key else "not configured"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        dependencies={
            "openai": "connected" if settings.openai_api_key else "not configured",
            "langsmith": "connected" if settings.langchain_api_key else "not configured",
            "evol_instruct_service": "running" if evol_instruct_service else "not initialized",
            "evaluation_service": "running" if evaluation_service else "not initialized",
            "document_service": "running" if document_service else "not initialized"
        }
    )


@app.post("/generate", response_model=GenerationResponse)
async def generate_synthetic_data(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    service: EvolInstructService = Depends(get_evol_instruct_service),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Generate synthetic data using LangGraph-based Evol-Instruct methodology
    
    This endpoint takes input documents and generates evolved questions, answers, and contexts
    using the sophisticated Evol-Instruct approach with concurrent or sequential execution.
    """
    try:
        generation_id = str(uuid.uuid4())
        
        # Initialize generation status
        generation_status[generation_id] = {
            "status": "running",
            "progress": 0.0,
            "current_stage": "document_processing",
            "start_time": datetime.now()
        }
        
        # Process input documents
        documents = doc_service.process_document_inputs(request.documents)
        
        # Validate documents
        validation_result = doc_service.validate_documents(documents)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Document validation failed: {validation_result['issues']}"
            )
        
        # Update status
        generation_status[generation_id]["progress"] = 0.1
        generation_status[generation_id]["current_stage"] = "synthetic_generation"
        
        # Generate synthetic data
        result = service.generate_synthetic_data(
            documents=documents,
            settings=request.settings,
            max_iterations=request.max_iterations
        )
        
        # Update final status
        generation_status[generation_id]["status"] = "completed"
        generation_status[generation_id]["progress"] = 1.0
        generation_status[generation_id]["current_stage"] = "completed"
        
        # Create response
        response = GenerationResponse(
            success=True,
            evolved_questions=result["evolved_questions"],
            question_answers=result["question_answers"],
            question_contexts=result["question_contexts"],
            performance_metrics=result["performance_metrics"],
            generation_id=generation_id,
            timestamp=datetime.now()
        )
        
        return response
        
    except Exception as e:
        # Update error status
        if generation_id in generation_status:
            generation_status[generation_id]["status"] = "failed"
            generation_status[generation_id]["error"] = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"Synthetic data generation failed: {str(e)}"
        )


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_synthetic_data(
    request: EvaluationRequest,
    service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Evaluate the quality of generated synthetic data
    
    This endpoint assesses synthetic data using various metrics including question quality,
    answer accuracy, and evolution effectiveness using LLM-as-judge approaches.
    """
    try:
        # Evaluate synthetic data
        result = service.evaluate_synthetic_data(
            evolved_questions=request.evolved_questions,
            question_answers=request.question_answers,
            question_contexts=request.question_contexts,
            evaluation_metrics=request.evaluation_metrics
        )
        
        # Create response
        response = EvaluationResponse(
            success=result["success"],
            evaluation_id=result["evaluation_id"],
            overall_scores=result["overall_scores"],
            detailed_results=result["detailed_results"],
            summary_statistics=result["summary_statistics"],
            timestamp=result["timestamp"]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.post("/generate/batch", response_model=BatchGenerationResponse)
async def generate_batch_synthetic_data(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    service: EvolInstructService = Depends(get_evol_instruct_service),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Generate synthetic data for multiple document batches
    
    This endpoint processes multiple batches of documents concurrently, generating
    synthetic data for each batch and returning aggregated results.
    """
    try:
        batch_id = str(uuid.uuid4())
        batch_results = []
        
        # Process each batch
        for i, document_batch in enumerate(request.document_batches):
            # Process documents for this batch
            documents = doc_service.process_document_inputs(document_batch)
            
            # Generate synthetic data for this batch
            result = service.generate_synthetic_data(
                documents=documents,
                settings=request.settings,
                max_iterations=1
            )
            
            # Create batch result
            batch_result = GenerationResponse(
                success=True,
                evolved_questions=result["evolved_questions"],
                question_answers=result["question_answers"],
                question_contexts=result["question_contexts"],
                performance_metrics=result["performance_metrics"],
                generation_id=f"{batch_id}_batch_{i}",
                timestamp=datetime.now()
            )
            
            batch_results.append(batch_result)
        
        # Calculate total performance metrics
        total_execution_time = sum(result.performance_metrics.execution_time_seconds for result in batch_results)
        total_questions = sum(result.performance_metrics.questions_generated for result in batch_results)
        
        total_performance = PerformanceMetrics(
            execution_time_seconds=total_execution_time,
            questions_generated=total_questions,
            answers_generated=sum(result.performance_metrics.answers_generated for result in batch_results),
            contexts_extracted=sum(result.performance_metrics.contexts_extracted for result in batch_results),
            questions_per_second=total_questions / total_execution_time if total_execution_time > 0 else 0,
            execution_mode="batch"
        )
        
        # Create response
        response = BatchGenerationResponse(
            success=True,
            batch_results=batch_results,
            batch_names=request.batch_names,
            total_performance=total_performance,
            batch_id=batch_id,
            timestamp=datetime.now()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch generation failed: {str(e)}"
        )


@app.get("/generate/status/{generation_id}", response_model=StatusResponse)
async def get_generation_status(generation_id: str):
    """
    Get the status of a generation job
    
    This endpoint allows clients to check the progress of long-running generation tasks.
    """
    if generation_id not in generation_status:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    status_info = generation_status[generation_id]
    
    return StatusResponse(
        generation_id=generation_id,
        status=status_info["status"],
        progress=status_info["progress"],
        current_stage=status_info["current_stage"],
        estimated_completion=None  # Could implement ETA calculation
    )


@app.get("/documents/sample", response_model=List[DocumentInput])
async def get_sample_documents(
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Get sample documents for testing the API
    
    This endpoint provides pre-defined sample documents that can be used
    to test the synthetic data generation functionality.
    """
    try:
        sample_docs = doc_service.create_sample_documents()
        
        # Convert to DocumentInput format
        document_inputs = []
        for doc in sample_docs:
            document_inputs.append(DocumentInput(
                content=doc.page_content,
                metadata=doc.metadata,
                source=doc.metadata.get("source", "unknown")
            ))
        
        return document_inputs
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sample documents: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message=str(exc),
            details={"request_url": str(request.url)}
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 