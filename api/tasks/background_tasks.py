"""
Background Tasks - Celery-based async task processing
Handles long-running operations like document processing and data generation
"""

from celery import Celery
from typing import Dict, List, Any, Optional
import time
import uuid
from datetime import datetime

from api.config import settings
from api.utils.cache_manager import session_cache, result_cache
from api.services.evol_instruct_service import EvolInstructService
from api.services.document_service import DocumentService


# Initialize Celery app
celery_app = Celery(
    'evolsynth_tasks',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1',
    include=['api.tasks.background_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='pickle',
    accept_content=['pickle'],
    result_serializer='pickle',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
)


@celery_app.task(bind=True)
def process_documents_async(self, documents_data: List[Dict], task_id: str) -> Dict[str, Any]:
    """Process documents asynchronously"""
    try:
        # Update task progress
        self.update_state(
            state='PROCESSING',
            meta={'progress': 0.1, 'status': 'Processing documents...'}
        )
        
        # Initialize services
        doc_service = DocumentService()
        
        # Process documents
        documents = doc_service.process_document_inputs(documents_data)
        
        # Update progress
        self.update_state(
            state='PROCESSING', 
            meta={'progress': 0.5, 'status': 'Documents processed'}
        )
        
        # Validate documents
        validation_result = doc_service.validate_documents(documents)
        
        if not validation_result['valid']:
            raise Exception(f"Document validation failed: {validation_result['issues']}")
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'progress': 1.0, 'status': 'Documents ready for generation'}
        )
        
        # Save processed documents to cache
        from api.utils.cache_manager import document_cache
        doc_hash = str(hash(str(documents_data)))
        document_cache.save_processed_document(doc_hash, {
            'documents': documents,
            'validation': validation_result,
            'processed_at': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'document_count': len(documents),
            'document_hash': doc_hash,
            'validation': validation_result
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        raise


@celery_app.task(bind=True)
def generate_synthetic_data_async(
    self,
    documents_data: List[Dict],
    settings_data: Dict,
    task_id: str
) -> Dict[str, Any]:
    """Generate synthetic data asynchronously"""
    try:
        # Initialize progress
        progress_stages = {
            'initializing': 0.1,
            'base_questions': 0.3,
            'evolution': 0.7,
            'answers': 0.9,
            'completed': 1.0
        }
        
        # Update initial state
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': progress_stages['initializing'],
                'stage': 'initializing',
                'status': 'Initializing synthetic data generation...'
            }
        )
        
        # Initialize services
        evol_service = EvolInstructService()
        doc_service = DocumentService()
        
        # Process documents
        documents = doc_service.process_document_inputs(documents_data)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': progress_stages['base_questions'],
                'stage': 'base_questions',
                'status': 'Generating base questions...'
            }
        )
        
        # Generate synthetic data
        result = evol_service.generate_synthetic_data(
            documents=documents,
            settings=settings_data
        )
        
        # Update progress - evolution stage
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': progress_stages['evolution'],
                'stage': 'evolution',
                'status': 'Evolving questions...'
            }
        )
        
        # Simulate some processing time for evolution
        time.sleep(2)
        
        # Update progress - answers stage
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': progress_stages['answers'],
                'stage': 'answers',
                'status': 'Generating answers...'
            }
        )
        
        # Complete generation
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': progress_stages['completed'],
                'stage': 'completed', 
                'status': 'Generation completed successfully',
                'questions_generated': len(result.get('evolved_questions', [])),
                'execution_time': result.get('performance_metrics', {}).get('execution_time_seconds', 0)
            }
        )
        
        # Cache the result
        request_hash = str(hash(str(documents_data) + str(settings_data)))
        result_cache.save_generation_result(request_hash, result)
        
        return result
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'progress': 0,
                'status': f'Generation failed: {str(e)}'
            }
        )
        raise


@celery_app.task(bind=True)
def evaluate_synthetic_data_async(
    self,
    evolved_questions: List[Dict],
    question_answers: List[Dict],
    question_contexts: List[Dict],
    evaluation_metrics: List[str],
    task_id: str
) -> Dict[str, Any]:
    """Evaluate synthetic data quality asynchronously"""
    try:
        self.update_state(
            state='PROCESSING',
            meta={'progress': 0.1, 'status': 'Starting evaluation...'}
        )
        
        from api.services.evaluation_service import EvaluationService
        eval_service = EvaluationService()
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'progress': 0.5, 'status': 'Running quality assessment...'}
        )
        
        # Perform evaluation
        evaluation_result = eval_service.evaluate_synthetic_data(
            evolved_questions=evolved_questions,
            question_answers=question_answers,
            question_contexts=question_contexts,
            evaluation_metrics=evaluation_metrics
        )
        
        # Complete evaluation
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 1.0,
                'status': 'Evaluation completed',
                'overall_scores': evaluation_result.get('overall_scores', {}),
                'questions_evaluated': len(evolved_questions)
            }
        )
        
        return evaluation_result
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        raise


@celery_app.task(bind=True)
def batch_process_documents_async(
    self,
    batch_data: List[List[Dict]],
    settings_data: Dict,
    task_id: str
) -> Dict[str, Any]:
    """Process multiple document batches asynchronously"""
    try:
        total_batches = len(batch_data)
        results = []
        
        for i, batch in enumerate(batch_data):
            # Update progress
            progress = (i / total_batches) * 0.9  # Reserve 10% for final processing
            self.update_state(
                state='PROCESSING',
                meta={
                    'progress': progress,
                    'status': f'Processing batch {i+1}/{total_batches}...',
                    'current_batch': i+1,
                    'total_batches': total_batches
                }
            )
            
            # Process individual batch
            batch_result = generate_synthetic_data_async.apply_async(
                args=(batch, settings_data, f"{task_id}_batch_{i}")
            ).get()
            
            results.append(batch_result)
        
        # Final processing
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': 0.95,
                'status': 'Finalizing batch results...'
            }
        )
        
        # Aggregate results
        total_questions = sum(len(r.get('evolved_questions', [])) for r in results)
        total_execution_time = sum(r.get('performance_metrics', {}).get('execution_time_seconds', 0) for r in results)
        
        final_result = {
            'success': True,
            'batch_results': results,
            'total_batches': total_batches,
            'total_questions_generated': total_questions,
            'total_execution_time': total_execution_time,
            'average_questions_per_batch': total_questions / total_batches if total_batches > 0 else 0
        }
        
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 1.0,
                'status': 'Batch processing completed',
                'total_questions': total_questions,
                'total_batches': total_batches
            }
        )
        
        return final_result
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'progress': 0}
        )
        raise


# Task monitoring utilities
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a background task"""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'progress': 0,
            'status': 'Task is waiting to be processed...'
        }
    elif task.state == 'PROCESSING':
        response = {
            'state': task.state,
            'progress': task.info.get('progress', 0),
            'status': task.info.get('status', 'Processing...'),
            'stage': task.info.get('stage', 'unknown')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'progress': 1.0,
            'status': 'Task completed successfully',
            'result': task.result
        }
    else:  # FAILURE
        response = {
            'state': task.state,
            'progress': 0,
            'status': f'Task failed: {task.info.get("error", "Unknown error")}',
            'error': task.info.get('error', 'Unknown error')
        }
    
    return response


def cancel_task(task_id: str) -> bool:
    """Cancel a background task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return True
    except Exception as e:
        print(f"Error cancelling task {task_id}: {e}")
        return False


# Health check for Celery workers
def check_worker_health() -> Dict[str, Any]:
    """Check health of Celery workers"""
    try:
        # Check if workers are responding
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active_tasks = inspect.active()
        
        if not stats:
            return {
                'status': 'unhealthy',
                'message': 'No active workers found',
                'workers': 0
            }
        
        return {
            'status': 'healthy',
            'workers': len(stats),
            'active_tasks': sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0,
            'worker_details': stats
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error checking worker health: {e}'
        } 