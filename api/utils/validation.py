"""
Comprehensive validation utilities for the EvolSynth API
Provides validation for requests, files, data, and API configurations
"""

import os
import re
import mimetypes
from typing import List, Dict, Any, Tuple, Optional, Union
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, validator, ValidationError as PydanticValidationError

from api.models.requests import GenerationRequest, EvaluationRequest
from api.utils.logging_config import get_logger

logger = get_logger("api.validation")


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
        
        # Additional document validation
        if len(doc.content) > 1000000:  # 1MB limit
            errors.append(f"Document {i} content exceeds 1MB limit")
    
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
    
    # Validate data consistency
    question_ids = {q.get('id') for q in request.evolved_questions if q.get('id')}
    answer_ids = {qa.get('question_id') for qa in request.question_answers if qa.get('question_id')}
    context_ids = {qc.get('question_id') for qc in request.question_contexts if qc.get('question_id')}
    
    if question_ids != answer_ids:
        errors.append("Question IDs mismatch between questions and answers")
    
    if question_ids != context_ids:
        errors.append("Question IDs mismatch between questions and contexts")
    
    return len(errors) == 0, errors


class ValidationUtilities:
    """Comprehensive validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """Validate URL format and scheme"""
        if not url:
            return False
        
        allowed_schemes = allowed_schemes or ['http', 'https']
        
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in allowed_schemes and
                bool(parsed.netloc) and
                len(url) <= 2000
            )
        except Exception:
            return False
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_string.lower()))
    
    @staticmethod
    def validate_json_data(data: Any, required_fields: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """Validate JSON data structure"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a JSON object")
            return False, errors
        
        if required_fields:
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
                elif data[field] is None:
                    errors.append(f"Field '{field}' cannot be null")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 0, max_length: int = 10000) -> Tuple[bool, str]:
        """Validate text length constraints"""
        if len(text) < min_length:
            return False, f"Text must be at least {min_length} characters"
        
        if len(text) > max_length:
            return False, f"Text must not exceed {max_length} characters"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: Optional[float] = None, 
                             max_val: Optional[float] = None) -> Tuple[bool, str]:
        """Validate numeric value is within range"""
        if min_val is not None and value < min_val:
            return False, f"Value must be at least {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"Value must not exceed {max_val}"
        
        return True, ""


class FileValidator:
    """File validation utilities"""
    
    ALLOWED_MIME_TYPES = {
        'text/plain',
        'text/markdown', 
        'application/pdf',
        'application/json',
        'text/csv'
    }
    
    ALLOWED_EXTENSIONS = {'.txt', '.md', '.pdf', '.json', '.csv'}
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_file_upload(cls, file_path: str, content: bytes) -> Tuple[bool, List[str]]:
        """Validate uploaded file"""
        errors = []
        
        # Check file size
        if len(content) > cls.MAX_FILE_SIZE:
            errors.append(f"File size exceeds {cls.MAX_FILE_SIZE // (1024*1024)}MB limit")
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            errors.append(f"File extension '{file_ext}' not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}")
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type not in cls.ALLOWED_MIME_TYPES:
            errors.append(f"MIME type '{mime_type}' not allowed")
        
        # Check for potential security issues
        if cls._has_security_issues(file_path, content):
            errors.append("File contains potentially malicious content")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, List[str]]:
        """Validate filename for security"""
        errors = []
        
        # Check for directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            errors.append("Filename contains invalid path characters")
        
        # Check for reserved names (Windows)
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            errors.append("Filename uses reserved system name")
        
        # Check length
        if len(filename) > 255:
            errors.append("Filename too long (max 255 characters)")
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in filename for char in invalid_chars):
            errors.append("Filename contains invalid characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _has_security_issues(file_path: str, content: bytes) -> bool:
        """Basic security check for file content"""
        try:
            # Check for executable headers
            if content.startswith(b'\x4d\x5a') or content.startswith(b'\x7f\x45\x4c\x46'):
                return True
            
            # Check for script tags in text files
            if file_path.endswith(('.txt', '.md', '.csv')):
                content_str = content.decode('utf-8', errors='ignore').lower()
                dangerous_patterns = ['<script', 'javascript:', 'vbscript:', 'data:text/html']
                if any(pattern in content_str for pattern in dangerous_patterns):
                    return True
            
        except Exception:
            # If we can't decode or check, err on the side of caution
            return True
        
        return False


class DataValidator:
    """Data structure validation utilities"""
    
    @staticmethod
    def validate_document_structure(document: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate document data structure"""
        errors = []
        required_fields = ['content']
        
        for field in required_fields:
            if field not in document:
                errors.append(f"Missing required field: {field}")
        
        if 'content' in document:
            if not isinstance(document['content'], str):
                errors.append("Document content must be a string")
            elif len(document['content'].strip()) == 0:
                errors.append("Document content cannot be empty")
        
        if 'metadata' in document and not isinstance(document['metadata'], dict):
            errors.append("Document metadata must be a dictionary")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_generation_settings(settings: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate generation settings"""
        errors = []
        
        if 'max_iterations' in settings:
            is_valid, error = ValidationUtilities.validate_numeric_range(
                settings['max_iterations'], 1, 10
            )
            if not is_valid:
                errors.append(f"max_iterations: {error}")
        
        if 'temperature' in settings:
            is_valid, error = ValidationUtilities.validate_numeric_range(
                settings['temperature'], 0.0, 2.0
            )
            if not is_valid:
                errors.append(f"temperature: {error}")
        
        if 'max_tokens' in settings:
            is_valid, error = ValidationUtilities.validate_numeric_range(
                settings['max_tokens'], 1, 4000
            )
            if not is_valid:
                errors.append(f"max_tokens: {error}")
        
        return len(errors) == 0, errors


class APIKeyValidator:
    """API key validation utilities"""
    
    @staticmethod
    def validate_openai_key(api_key: str) -> Tuple[bool, str]:
        """Validate OpenAI API key format"""
        if not api_key:
            return False, "API key is required"
        
        if not api_key.startswith('sk-'):
            return False, "OpenAI API key must start with 'sk-'"
        
        if len(api_key) < 20:
            return False, "API key appears to be too short"
        
        # Check for valid characters (alphanumeric and some special chars)
        if not re.match(r'^sk-[A-Za-z0-9\-_]+$', api_key):
            return False, "API key contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_langchain_key(api_key: str) -> Tuple[bool, str]:
        """Validate LangChain API key format"""
        if not api_key:
            return False, "LangChain API key is required"
        
        if not api_key.startswith('ls__'):
            return False, "LangChain API key must start with 'ls__'"
        
        if len(api_key) < 20:
            return False, "API key appears to be too short"
        
        return True, ""
    
    @staticmethod
    def validate_api_keys(openai_key: Optional[str] = None, 
                         langchain_key: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Validate multiple API keys"""
        errors = []
        
        if openai_key:
            is_valid, error = APIKeyValidator.validate_openai_key(openai_key)
            if not is_valid:
                errors.append(f"OpenAI API key: {error}")
        
        if langchain_key:
            is_valid, error = APIKeyValidator.validate_langchain_key(langchain_key)
            if not is_valid:
                errors.append(f"LangChain API key: {error}")
        
        return len(errors) == 0, errors


# Enhanced validation with Pydantic models
class ValidationResult(BaseModel):
    """Validation result model"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    
    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)


def comprehensive_request_validation(
    request_data: Dict[str, Any],
    request_type: str = "generation"
) -> ValidationResult:
    """
    Comprehensive request validation with detailed feedback
    
    Args:
        request_data: The request data to validate
        request_type: Type of request ('generation' or 'evaluation')
    
    Returns:
        ValidationResult with detailed feedback
    """
    result = ValidationResult(is_valid=True)
    
    try:
        if request_type == "generation":
            # Validate generation request
            if 'documents' not in request_data:
                result.add_error("Missing 'documents' field")
            else:
                documents = request_data['documents']
                if not isinstance(documents, list) or not documents:
                    result.add_error("Documents must be a non-empty list")
                else:
                    for i, doc in enumerate(documents):
                        doc_valid, doc_errors = DataValidator.validate_document_structure(doc)
                        if not doc_valid:
                            for error in doc_errors:
                                result.add_error(f"Document {i}: {error}")
            
            # Validate settings if present
            if 'settings' in request_data:
                settings_valid, settings_errors = DataValidator.validate_generation_settings(
                    request_data['settings']
                )
                if not settings_valid:
                    for error in settings_errors:
                        result.add_error(f"Settings: {error}")
        
        elif request_type == "evaluation":
            # Add evaluation-specific validation
            required_fields = ['evolved_questions', 'question_answers', 'question_contexts']
            for field in required_fields:
                if field not in request_data:
                    result.add_error(f"Missing required field: {field}")
                elif not isinstance(request_data[field], list):
                    result.add_error(f"Field '{field}' must be a list")
    
    except Exception as e:
        result.add_error(f"Validation error: {str(e)}")
        logger.error(f"Validation exception: {e}", exc_info=True)
    
    return result 