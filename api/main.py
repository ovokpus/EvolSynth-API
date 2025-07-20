"""
EvolSynth API - Production-Ready FastAPI Application
Advanced Synthetic Data Generation with comprehensive documentation, monitoring, and optimization
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import tempfile
import os
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Performance imports
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("🚀 Using uvloop for better async performance")
except ImportError:
    print("⚠️  uvloop not available, using default event loop")

# Local imports
from api.config import settings, validate_api_keys, setup_environment
from api.models.requests import GenerationRequest, EvaluationRequest
from api.models.responses import (
    GenerationResponse, EvaluationResponse, HealthResponse, 
    ErrorResponse, StatusResponse
)
from api.models.core import DocumentInput, PerformanceMetrics

# Enhanced documentation
from api.docs import (
    create_custom_openapi_schema, 
    get_api_description, 
    customize_swagger_ui,
    OPENAPI_TAGS
)

# Standard services
from api.services.evol_instruct_service import EvolInstructService
from api.services.evaluation_service import EvaluationService
from api.services.document_service import DocumentService

# Utilities and monitoring
from api.utils.error_handling import global_exception_handler
from api.utils.security import configure_cors, rate_limit_dependency, RateLimit
from api.utils.health_checks import initialize_health_checks, get_health_status, get_health_summary

# Performance optimizations
try:
    from api.utils.cache_manager import cache_manager, result_cache, document_cache
    CACHE_AVAILABLE = True
except ImportError:
    print("⚠️  Cache manager not available, caching disabled")
    CACHE_AVAILABLE = False

try:
    from api.config import performance_monitor, get_optimization_config, OptimizationLevel
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    print("⚠️  Performance monitoring not available")
    PERFORMANCE_MONITORING_AVAILABLE = False

# Initialize FastAPI app with enhanced configuration
app = FastAPI(
    title="EvolSynth API",
    description=get_api_description(),
    version=f"{settings.app_version}",
    docs_url=None,  # Custom docs endpoint
    redoc_url=None,  # Custom redoc endpoint
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "EvolSynth API Support",
        "url": "https://github.com/your-org/evolsynth-api",
        "email": "support@evolsynth.ai"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS with security best practices
configure_cors(app)

# Add global exception handler
app.exception_handler(Exception)(global_exception_handler)

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
    """Enhanced middleware for performance tracking and request monitoring"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
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
        
        # Add performance and tracking headers
        if 'response' in locals():
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            response.headers["X-Request-ID"] = request_id
            response.headers["X-API-Version"] = settings.app_version
            response.headers["X-Powered-By"] = "EvolSynth"
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize services with comprehensive error handling and monitoring"""
    global evol_instruct_service, evaluation_service, document_service
    
    try:
        print("🚀 Starting EvolSynth API initialization...")
        
        # Validate API keys
        validate_api_keys()
        setup_environment()
        print("✅ API keys validated and environment configured")
        
        # Initialize services
        evol_instruct_service = EvolInstructService()
        evaluation_service = EvaluationService()
        document_service = DocumentService()
        print("✅ Core services initialized")
        
        # Test cache connection
        if CACHE_AVAILABLE:
            cache_stats = cache_manager.get_stats()
            print(f"✅ Cache system: {cache_stats['cache_type']} (enabled: {cache_stats['cache_enabled']})")
            
            # Clear cache on startup to ensure fresh deployment
            try:
                cleared_docs = cache_manager.clear_prefix("docs")
                cleared_results = cache_manager.clear_prefix("results")
                cleared_sessions = cache_manager.clear_prefix("sessions")
                cleared_evolsynth = cache_manager.clear_prefix("evolsynth")
                cleared_generation = cache_manager.clear_prefix("generation")
                total_cleared = cleared_docs + cleared_results + cleared_sessions + cleared_evolsynth + cleared_generation
                
                if total_cleared > 0:
                    print(f"🧹 Deployment cache clear: {total_cleared} entries removed")
                else:
                    print("🧹 Deployment cache clear: No entries to remove")
            except Exception as cache_error:
                print(f"⚠️  Cache clear failed on startup: {cache_error}")
        else:
            print("⚠️  Cache system not available")
        
        # Initialize health checks
        initialize_health_checks()
        print("✅ Health check system initialized")
        
        # Load performance configuration
        if PERFORMANCE_MONITORING_AVAILABLE:
            config = get_optimization_config(OptimizationLevel.PRODUCTION)
            print(f"✅ Performance monitoring: {config.max_concurrent_requests} max concurrent requests")
        else:
            print("⚠️  Performance monitoring not available")
        
        # Set custom OpenAPI schema
        app.openapi_schema = create_custom_openapi_schema(app)
        print("✅ Enhanced OpenAPI documentation configured")
        
        print(f"🎉 {settings.app_name} v{settings.app_version} started successfully!")
        print(f"📊 Environment: {'Development' if settings.debug else 'Production'}")
        print(f"📚 Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


# Enhanced documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling and features"""
    return HTMLResponse(customize_swagger_ui())


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Enhanced ReDoc documentation"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="EvolSynth API Documentation",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return a simple favicon to prevent 404 logs"""
    # Simple 1x1 transparent PNG favicon
    favicon_content = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
        0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
        0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    return Response(content=favicon_content, media_type="image/png")


# Core API endpoints with enhanced documentation
@app.api_route(
    "/", 
    methods=["GET", "HEAD"],
    response_model=HealthResponse,
    tags=["Health"],
    summary="API Status and Information",
    description="Get basic API information, version, and service status",
    responses={
        200: {
            "description": "API status information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "dependencies": {
                            "cache_enabled": "true",
                            "optimized_service": "true",
                            "performance_monitoring": "true"
                        }
                    }
                }
            }
        }
    }
)
async def root():
    """Enhanced root endpoint with comprehensive status information"""
    return HealthResponse(
        status="healthy",
        version=f"{settings.app_version}",
        timestamp=datetime.now(),
        dependencies={
            "cache_enabled": str(CACHE_AVAILABLE),
            "performance_monitoring": str(PERFORMANCE_MONITORING_AVAILABLE),
            "redis_available": str(CACHE_AVAILABLE and cache_manager.cache_enabled if CACHE_AVAILABLE else False),
            "optimization_level": "production"
        }
    )


@app.get(
    "/health", 
    response_model=HealthResponse,
    tags=["Health"],
    summary="Basic Health Check",
    description="Perform a basic health check of the API and its dependencies",
    responses={
        200: {"description": "Service is healthy"},
        503: {"description": "Service is unhealthy", "model": ErrorResponse}
    }
)
async def health_check():
    """Enhanced health check with dependency validation"""
    dependencies = {
        "openai": "connected",
        "langsmith": "connected" if settings.langchain_api_key else "not_configured",
        "evol_instruct_service": "running" if evol_instruct_service else "not_initialized",
        "evaluation_service": "running" if evaluation_service else "not_initialized",
        "document_service": "running" if document_service else "not_initialized"
    }
    
    # Check cache status
    if CACHE_AVAILABLE:
        try:
            cache_stats = cache_manager.get_stats()
            dependencies["redis_cache"] = "connected" if cache_stats["cache_enabled"] else "disconnected"
            dependencies["cache_type"] = cache_stats["cache_type"]
        except Exception:
            dependencies["redis_cache"] = "disconnected"
    else:
        dependencies["redis_cache"] = "not_configured"
    
    # Check for any unhealthy services
    unhealthy_services = [k for k, v in dependencies.items() if v in ["disconnected", "not_initialized", "failed"]]
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE if unhealthy_services else status.HTTP_200_OK
    
    return HealthResponse(
        status="healthy" if not unhealthy_services else "degraded",
        version=f"{settings.app_version}",
        timestamp=datetime.now(),
        dependencies=dependencies
    )


@app.get(
    "/health/detailed",
    tags=["Health"],
    summary="Detailed Health Check",
    description="Comprehensive health check with detailed dependency status and performance metrics",
    responses={
        200: {"description": "Detailed health information"},
        503: {"description": "One or more services are unhealthy"}
    }
)
async def detailed_health_check():
    """Comprehensive health check with detailed metrics"""
    try:
        health_data = await get_health_status()
        return JSONResponse(content=health_data)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get(
    "/health/summary",
    tags=["Health"],
    summary="Health Summary",
    description="Get a quick summary of system health status",
)
async def health_summary():
    """Quick health summary for monitoring systems"""
    try:
        summary = await get_health_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post(
    "/generate",
    response_model=GenerationResponse,
    tags=["Generation"],
    summary="Generate Synthetic Data",
    description="""
    Generate high-quality synthetic data using the Evol-Instruct methodology.
    
    This endpoint processes input documents and generates evolved questions, answers, and contexts
    using advanced language models and LangGraph workflows.
    
    **Features:**
    - Multiple evolution types (simple, multi-context, reasoning, complex)
    - Concurrent processing for improved performance
    - Comprehensive quality metrics
    - Redis caching for repeated requests
    
    **Performance:**
    - Typical response time: 3-8 seconds
    - Supports up to 10 documents per request
    - Automatic caching of results
    """,
    responses={
        200: {"description": "Successfully generated synthetic data"},
        422: {"$ref": "#/components/responses/ValidationError"},
        429: {"$ref": "#/components/responses/RateLimitError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    },
    dependencies=[Depends(rate_limit_dependency)]
)
async def generate_synthetic_data(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """Enhanced generation endpoint with comprehensive error handling and monitoring"""
    start_time = time.time()
    request_id = f"gen_{uuid.uuid4()}"
    
    try:
        if not evol_instruct_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Generation service not initialized"
            )
        
        # Check cache first
        if CACHE_AVAILABLE:
            cache_key = cache_manager.generate_key("generation", request.dict())
            cached_result = result_cache.get_generation_result(cache_key)
            if cached_result:
                cached_result["cache_hit"] = True
                return GenerationResponse(**cached_result)
        
        # Track generation status
        generation_status[request_id] = {
            "status": "processing",
            "start_time": start_time,
            "documents_count": len(request.documents)
        }
        
        # Convert DocumentInput objects to Document objects for service
        from langchain_core.documents import Document
        documents = [
            Document(page_content=doc.content, metadata=doc.metadata or {})
            for doc in request.documents
        ]
         
        # Process generation using fast or standard method
        if request.fast_mode:
            print(f"🚀 Using FAST mode for generation")
            result = await evol_instruct_service.generate_synthetic_data_fast(
                documents=documents,
                settings=request.settings
            )
        else:
            print(f"🐌 Using STANDARD mode for generation")
            result = await evol_instruct_service.generate_synthetic_data_async(
                documents=documents,
                settings=request.settings
            )
        
        # Add metadata to match GenerationResponse model
        execution_time = time.time() - start_time
        evolved_questions = result.get("evolved_questions", [])
        question_answers = result.get("question_answers", [])
        question_contexts = result.get("question_contexts", [])
        
        result_with_metadata = {
            "success": True,
            "evolved_questions": evolved_questions,
            "question_answers": question_answers,
            "question_contexts": question_contexts,
            "performance_metrics": {
                "execution_time_seconds": round(execution_time, 2),
                "questions_generated": len(evolved_questions),
                "answers_generated": len(question_answers),
                "contexts_extracted": len(question_contexts),
                "questions_per_second": len(evolved_questions) / execution_time if execution_time > 0 else 0,
                "execution_mode": getattr(request.settings, 'execution_mode', 'concurrent') if request.settings else 'concurrent'
            },
            "generation_id": request_id,
            "timestamp": datetime.now(),
            "cache_hit": False
        }
        
        # Cache result
        if CACHE_AVAILABLE:
            background_tasks.add_task(
                result_cache.save_generation_result, 
                cache_key, 
                result_with_metadata
            )
        
        # Update status
        generation_status[request_id] = {
            "status": "completed",
            "execution_time": execution_time,
            "questions_generated": len(result.get("evolved_questions", []))
        }
        
        return GenerationResponse(**result_with_metadata)
        
    except Exception as e:
        generation_status[request_id] = {
            "status": "failed",
            "error": str(e),
            "execution_time": time.time() - start_time
        }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@app.post(
    "/evaluate",
    response_model=EvaluationResponse,
    tags=["Evaluation"],
    summary="Evaluate Synthetic Data Quality",
    description="""
    Evaluate the quality of generated synthetic data using LLM-as-judge methodology.
    
    This endpoint analyzes evolved questions, answers, and contexts to provide
    comprehensive quality metrics and scoring.
    
    **Features:**
    - Question quality assessment (clarity, specificity, educational value)
    - Answer accuracy evaluation (correctness, completeness, relevance)
    - Evolution effectiveness scoring (complexity achievement for evolution type)
    - Detailed per-question metrics and overall scores
    
    **Performance:**
    - Typical response time: 5-15 seconds depending on question count
    - Supports evaluation of up to 50 questions per request
    - Quality scores capped at 95% maximum for realistic assessment
    """,
    responses={
        200: {"description": "Successfully evaluated synthetic data quality"},
        422: {"$ref": "#/components/responses/ValidationError"},
        500: {"$ref": "#/components/responses/InternalServerError"}
    }
)
async def evaluate_synthetic_data(request: EvaluationRequest):
    """Evaluate the quality of generated synthetic data"""
    try:
        if not evaluation_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Evaluation service not initialized"
            )
        
        # Perform evaluation
        result = evaluation_service.evaluate_synthetic_data(
            evolved_questions=request.evolved_questions,
            question_answers=request.question_answers,
            question_contexts=request.question_contexts,
            evaluation_metrics=request.evaluation_metrics
        )
        
        return EvaluationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


# Cache management endpoints with enhanced documentation
if CACHE_AVAILABLE:
    @app.delete(
        "/cache/clear",
        tags=["Cache"],
        summary="Clear All Cache",
        description="Clear all cached data including documents and generation results",
        responses={
            200: {"description": "Cache cleared successfully"},
            500: {"description": "Cache clear operation failed"}
        }
    )
    async def clear_cache():
        """Clear all cache entries with detailed reporting"""
        try:
            cleared_docs = cache_manager.clear_prefix("docs")
            cleared_results = cache_manager.clear_prefix("results")
            cleared_sessions = cache_manager.clear_prefix("sessions")
            cleared_evolsynth = cache_manager.clear_prefix("evolsynth")  # Clear service cache
            cleared_generation = cache_manager.clear_prefix("generation")  # Clear API cache
            
            return {
                "success": True,
                "cleared_entries": {
                    "documents": cleared_docs,
                    "results": cleared_results,
                    "sessions": cleared_sessions,
                    "evolsynth_service": cleared_evolsynth,
                    "generation_api": cleared_generation,
                    "total": cleared_docs + cleared_results + cleared_sessions + cleared_evolsynth + cleared_generation
                },
                "timestamp": datetime.now().isoformat(),
                "cache_type": cache_manager.get_stats()["cache_type"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Cache clear failed: {str(e)}"
            )
    
    @app.get(
        "/cache/stats",
        tags=["Cache"],
        summary="Cache Statistics", 
        description="Get detailed cache performance statistics and metrics",
        responses={
            200: {"description": "Cache statistics retrieved successfully"},
            503: {"description": "Cache system unavailable"}
        }
    )
    async def get_cache_stats():
        """Get comprehensive cache statistics"""
        try:
            stats = cache_manager.get_stats()
            health = cache_manager.health_check()
            
            return {
                **stats,
                "health": health,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cache stats unavailable: {str(e)}"
            )


# Performance monitoring endpoints
if PERFORMANCE_MONITORING_AVAILABLE:
    @app.get(
        "/metrics/performance",
        tags=["Performance"],
        summary="Performance Metrics",
        description="Get real-time performance metrics and system statistics",
    )
    async def get_performance_metrics():
        """Get current performance metrics"""
        try:
            metrics = performance_monitor.get_current_metrics()
            return {
                **metrics,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - performance_monitor.request_count * 0.1  # Approximate
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Performance metrics unavailable: {str(e)}"
            )


# Document processing endpoints
@app.post(
    "/upload/extract-content",
    tags=["Documents"],
    summary="Extract Content from Uploaded File",
    description="Upload a file and extract its text content for processing",
    responses={
        200: {
            "description": "File content extracted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "filename": "document.pdf",
                        "content": "Extracted text content...",
                        "metadata": {
                            "file_size": 15432,
                            "file_type": "application/pdf",
                            "pages_or_chunks": 3,
                            "content_length": 2847
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid file or extraction failed"},
        413: {"description": "File too large"},
        500: {"description": "Content extraction error"}
    }
)
async def extract_file_content(file: UploadFile = File(...)):
    """Extract text content from uploaded file"""
    if not document_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not initialized"
        )
    
    # Validate file size (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size} bytes) exceeds 10MB limit"
            )
        
        # Validate file type
        allowed_types = {'application/pdf', 'text/plain', 'text/markdown'}
        allowed_extensions = {'.pdf', '.txt', '.md'}
        
        file_extension = Path(file.filename or '').suffix.lower()
        
        if file.content_type not in allowed_types and file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, TXT, MD"
            )
        
        # Extract content based on file type
        extracted_content = ""
        pages_or_chunks = 1
        
        if file.content_type == 'application/pdf' or file_extension == '.pdf':
            # Save file temporarily for PDF processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            try:
                # Use document service to load PDF
                documents = document_service.load_documents_from_files([temp_path])
                
                if documents:
                    extracted_content = "\n\n".join([doc.page_content for doc in documents])
                    pages_or_chunks = len(documents)
                else:
                    extracted_content = f"[PDF File: {file.filename}] - Content extraction failed"
                    
            except Exception as e:
                print(f"PDF extraction error: {e}")
                extracted_content = f"[PDF File: {file.filename}] - Error extracting content: {str(e)}"
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        elif file.content_type in ['text/plain', 'text/markdown'] or file_extension in ['.txt', '.md']:
            # Handle text files
            try:
                extracted_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    extracted_content = file_content.decode('latin-1')
                except:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Could not decode text file. Please ensure it's valid UTF-8 or Latin-1"
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type for content extraction"
            )
        
        return {
            "success": True,
            "filename": file.filename or "unknown",
            "content": extracted_content,
            "metadata": {
                "file_size": file_size,
                "file_type": file.content_type or "unknown",
                "pages_or_chunks": pages_or_chunks,
                "content_length": len(extracted_content)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )


# Enhanced utility endpoints
@app.get(
    "/documents/sample",
    tags=["Utilities"],
    summary="Get Sample Documents",
    description="Retrieve sample documents for testing and development purposes",
    responses={
        200: {
            "description": "Sample documents for testing",
            "content": {
                "application/json": {
                    "example": {
                        "documents": [
                            {
                                "content": "Sample document content...",
                                "metadata": {"source": "sample.pdf"},
                                "source": "sample.pdf"
                            }
                        ],
                        "count": 1
                    }
                }
            }
        }
    }
)
async def get_sample_documents():
    """Get sample documents for testing purposes"""
    if not document_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not initialized"
        )
    
    sample_docs = document_service.create_sample_documents()
    
    # Convert LangChain Documents to API format
    sample_documents = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "source": doc.metadata.get("source", "sample.txt")
        }
        for doc in sample_docs
    ]
     
    return {
        "documents": sample_documents,
        "count": len(sample_documents),
        "description": "Sample documents for testing EvolSynth API"
    }


@app.get(
    "/status/{request_id}",
    tags=["Utilities"],
    summary="Get Generation Status",
    description="Check the status of a synthetic data generation request",
    responses={
        200: {"description": "Generation status retrieved"},
        404: {"description": "Request ID not found"}
    }
)
async def get_generation_status(request_id: str):
    """Get the status of a generation request"""
    if request_id not in generation_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request ID {request_id} not found"
        )
    
    status_info = generation_status[request_id]
    return {
        "request_id": request_id,
        **status_info,
        "timestamp": datetime.now().isoformat()
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        loop="uvloop" if 'uvloop' in globals() else "asyncio"
    ) 