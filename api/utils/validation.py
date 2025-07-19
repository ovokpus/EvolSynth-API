"""
Validation utilities for the EvolSynth API
"""

from typing import List, Dict, Any, Tuple
from api.models.requests import GenerationRequest, EvaluationRequest


def validate_generation_request(request: GenerationRequest) -> Tuple[bool, List[str]]:
    """
    Validate a generation request
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check documents
    if not request.documents:
        errors.append("At least one document is required")
    
    for i, doc in enumerate(request.documents):
        if not doc.content.strip():
            errors.append(f"Document {i} has empty content")
    
    # Check max_iterations
    if request.max_iterations < 1 or request.max_iterations > 5:
        errors.append("max_iterations must be between 1 and 5")
    
    return len(errors) == 0, errors


def validate_evaluation_request(request: EvaluationRequest) -> Tuple[bool, List[str]]:
    """
    Validate an evaluation request
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required data
    if not request.evolved_questions:
        errors.append("At least one evolved question is required")
    
    if not request.question_answers:
        errors.append("At least one question-answer pair is required")
    
    if not request.question_contexts:
        errors.append("At least one question-context mapping is required")
    
    return len(errors) == 0, errors 