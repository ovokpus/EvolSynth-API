"""
EvolSynth API - Optimized FastAPI Application with Performance Enhancements
Advanced Synthetic Data Generation with Redis caching, async processing, and monitoring
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Performance imports
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("🚀 Using uvloop for better async performance")
except ImportError:
    print("⚠️  uvloop not available, using default event loop")

# Local imports
from api.config import settings, validate_api_keys, setup_environment
from api.models.requests import GenerationRequest, EvaluationRequest, BatchGenerationRequest
from api.models.responses import (
    GenerationResponse, EvaluationResponse, HealthResponse, 
    ErrorResponse, BatchGenerationResponse, StatusResponse
)
from api.models.core import DocumentInput, PerformanceMetrics

# Standard services
from api.services.evol_instruct_service import EvolInstructService
from api.services.evaluation_service import EvaluationService
from api.services.document_service import DocumentService

# Performance optimizations (now integrated into standard service)

try:
    from api.utils.cache_manager import cache_manager, result_cache, document_cache
    CACHE_AVAILABLE = True
except ImportError:
    print("⚠️  Cache manager not available, caching disabled")
    CACHE_AVAILABLE = False

try:
    from api.performance_optimization_config import performance_monitor, get_optimization_config, OptimizationLevel
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    print("⚠️  Performance monitoring not available")
    PERFORMANCE_MONITORING_AVAILABLE = False

# Initialize FastAPI app with optimizations
app = FastAPI(
    title=f"{settings.app_name} (Optimized)",
    description=f"{settings.app_description} - Enhanced with Redis caching and async processing",
    version=f"{settings.app_version}-optimized",
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

# Performance tracking
request_times: List[float] = []


@app.middleware("http")
async def performance_middleware(request, call_next):
    """Middleware to track performance metrics"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        success = response.status_code < 400
    except Exception as e:
        success = False
        raise
    finally:
        process_time = time.time() - start_time
        
        # Record metrics
        if PERFORMANCE_MONITORING_AVAILABLE:
            performance_monitor.record_request(process_time, success)
        
        # Add performance headers
        if 'response' in locals():
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Optimized"] = "true"
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize services with performance optimizations"""
    global evol_instruct_service, evaluation_service, document_service
    
    try:
        # Validate API keys
        validate_api_keys()
        setup_environment()
        
        # Initialize services
        evol_instruct_service = EvolInstructService()
        print("✅ Using optimized EvolInstructService with async processing")
        
        evaluation_service = EvaluationService()
        document_service = DocumentService()
        
        # Test cache connection
        if CACHE_AVAILABLE:
            cache_stats = cache_manager.get_stats()
            print(f"✅ Cache system initialized: {cache_stats['cache_type']}")
        
        # Load performance configuration
        if PERFORMANCE_MONITORING_AVAILABLE:
            config = get_optimization_config(OptimizationLevel.PRODUCTION)
            print(f"✅ Performance monitoring enabled: {config.max_concurrent_requests} max concurrent requests")
        
        print(f"🚀 {settings.app_name} started successfully with optimizations")
        print(f"📊 Environment: {'Development' if settings.debug else 'Production'}")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown with cache cleanup"""
    if CACHE_AVAILABLE:
        print("🧹 Cleaning up cache connections...")


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
    """Root endpoint with optimization info"""
    return HealthResponse(
        status="healthy",
        version=f"{settings.app_version}-optimized",
        timestamp=datetime.now(),
        dependencies={
            "cache_enabled": CACHE_AVAILABLE,
            "optimized_service": True,  # Always optimized now
            "performance_monitoring": PERFORMANCE_MONITORING_AVAILABLE
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with cache and performance status"""
    dependencies = {
        "openai": "connected",
        "langsmith": "connected",
        "evol_instruct_service": "running",
        "evaluation_service": "running",
        "document_service": "running"
    }
    
    # Check cache status
    if CACHE_AVAILABLE:
        try:
            cache_stats = cache_manager.get_stats()
            dependencies["redis_cache"] = "connected"
            dependencies["cache_type"] = cache_stats["cache_type"]
        except Exception:
            dependencies["redis_cache"] = "disconnected"
    else:
        dependencies["redis_cache"] = "not_configured"
    
    return HealthResponse(
        status="healthy",
        version=f"{settings.app_version}-optimized",
        timestamp=datetime.now(),
        dependencies=dependencies
    )


@app.get("/metrics/performance")
async def get_performance_metrics():
    """Get real-time performance metrics"""
    if not PERFORMANCE_MONITORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Performance monitoring not available")
    
    # Get performance metrics
    perf_metrics = performance_monitor.get_current_metrics()
    
    # Get cache statistics
    cache_stats = {}
    if CACHE_AVAILABLE:
        cache_stats = cache_manager.get_stats()
    
    return {
        "performance": perf_metrics,
        "cache": cache_stats,
        "timestamp": datetime.now().isoformat(),
        "optimization_level": "production"
    }


@app.post("/generate", response_model=GenerationResponse)
async def generate_synthetic_data_optimized(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    service: EvolInstructService = Depends(get_evol_instruct_service),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Optimized synthetic data generation with caching and async processing
    """
    try:
        generation_id = str(uuid.uuid4())
        
        # Check cache first if available
        if CACHE_AVAILABLE:
            cache_key = str(hash(str(request.documents) + str(request.settings)))
            cached_result = result_cache.get_generation_result(cache_key)
            
            if cached_result:
                print("🎯 Cache hit! Returning cached result")
                try:
                    # Handle performance_metrics conversion if it's a dict
                    perf_metrics = cached_result["performance_metrics"]
                    if isinstance(perf_metrics, dict):
                        perf_metrics = PerformanceMetrics(**perf_metrics)
                    
                    # Create proper response from cached result
                    response = GenerationResponse(
                        success=True,
                        evolved_questions=cached_result["evolved_questions"],
                        question_answers=cached_result["question_answers"],
                        question_contexts=cached_result["question_contexts"],
                        performance_metrics=perf_metrics,
                        generation_id=generation_id,
                        timestamp=datetime.now()
                    )
                    return response
                except (KeyError, TypeError) as e:
                    print(f"⚠️  Cache data corrupted, regenerating: {e}")
                    # Continue with normal generation if cache data is invalid
        
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
        
        # Generate synthetic data using optimized async implementation
        if hasattr(service, 'generate_synthetic_data_async'):
            print("🚀 Using async optimized generation")
            result = await service.generate_synthetic_data_async(
                documents=documents,
                settings=request.settings
            )
        else:
            print("🚀 Using optimized generation (sync wrapper)")
            result = service.generate_synthetic_data(
                documents=documents,
                settings=request.settings,
                max_iterations=request.max_iterations
            )
        
        # Update final status
        generation_status[generation_id]["status"] = "completed"
        generation_status[generation_id]["progress"] = 1.0
        generation_status[generation_id]["current_stage"] = "completed"
        
        # Cache the result if caching is available
        if CACHE_AVAILABLE:
            result_cache.save_generation_result(cache_key, result)
            print("💾 Result cached for future requests")
        
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


@app.get("/generate/status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get status of a generation task"""
    if generation_id not in generation_status:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    return generation_status[generation_id]


# Keep the existing endpoints from the original main.py
@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_synthetic_data(
    request: EvaluationRequest,
    service: EvaluationService = Depends(get_evaluation_service)
):
    """Evaluate synthetic data quality"""
    try:
        result = service.evaluate_synthetic_data(
            evolved_questions=request.evolved_questions,
            question_answers=request.question_answers,
            question_contexts=request.question_contexts,
            evaluation_metrics=request.evaluation_metrics
        )
        
        return EvaluationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@app.get("/documents/sample")
async def get_sample_documents():
    """Get sample documents for testing"""
    doc_service = get_document_service()
    sample_docs = doc_service.create_sample_documents()
    
    return {
        "documents": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in sample_docs
        ],
        "count": len(sample_docs),
        "message": "Sample documents for testing EvolSynth API"
    }


# Cache management endpoints
if CACHE_AVAILABLE:
    @app.delete("/cache/clear")
    async def clear_cache():
        """Clear all cache entries"""
        try:
            cleared_docs = cache_manager.clear_prefix("docs")
            cleared_results = cache_manager.clear_prefix("results")
            
            return {
                "success": True,
                "cleared_entries": {
                    "documents": cleared_docs,
                    "results": cleared_results
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")
    
    @app.get("/cache/stats")
    async def get_cache_stats():
        """Get cache statistics"""
        return cache_manager.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="uvloop" if 'uvloop' in globals() else "asyncio") 