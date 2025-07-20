"""
Unit tests for validation utilities
Tests all validation classes and functions for comprehensive coverage
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports  
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from api.utils.validation import (
    validate_generation_request,
    validate_evaluation_request,
    ValidationUtilities,
    FileValidator,
    DataValidator,
    APIKeyValidator,
    ValidationResult,
    comprehensive_request_validation
)
from api.models.requests import GenerationRequest, EvaluationRequest, Document


class TestValidationUtilities:
    """Test ValidationUtilities class"""
    
    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert ValidationUtilities.validate_email("test@example.com") is True
        assert ValidationUtilities.validate_email("user.name+tag@domain.co.uk") is True
        assert ValidationUtilities.validate_email("valid.email@subdomain.example.org") is True
    
    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert ValidationUtilities.validate_email("invalid-email") is False
        assert ValidationUtilities.validate_email("@domain.com") is False
        assert ValidationUtilities.validate_email("user@") is False
        assert ValidationUtilities.validate_email("") is False
        assert ValidationUtilities.validate_email("user@domain") is False  # No TLD
    
    def test_validate_url_valid(self):
        """Test valid URL validation"""
        assert ValidationUtilities.validate_url("https://example.com") is True
        assert ValidationUtilities.validate_url("http://test.org/path") is True
        assert ValidationUtilities.validate_url("https://sub.domain.com/path?query=1") is True
    
    def test_validate_url_invalid(self):
        """Test invalid URL validation"""
        assert ValidationUtilities.validate_url("not-a-url") is False
        assert ValidationUtilities.validate_url("ftp://example.com") is False  # Invalid scheme
        assert ValidationUtilities.validate_url("") is False
        assert ValidationUtilities.validate_url("http://") is False  # No domain
    
    def test_validate_url_custom_schemes(self):
        """Test URL validation with custom allowed schemes"""
        assert ValidationUtilities.validate_url("ftp://example.com", ["ftp"]) is True
        assert ValidationUtilities.validate_url("https://example.com", ["ftp"]) is False
    
    def test_validate_uuid_valid(self):
        """Test valid UUID validation"""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert ValidationUtilities.validate_uuid(valid_uuid) is True
        assert ValidationUtilities.validate_uuid(valid_uuid.upper()) is True
    
    def test_validate_uuid_invalid(self):
        """Test invalid UUID validation"""
        assert ValidationUtilities.validate_uuid("invalid-uuid") is False
        assert ValidationUtilities.validate_uuid("550e8400-e29b-41d4-a716") is False  # Too short
        assert ValidationUtilities.validate_uuid("") is False
    
    def test_validate_json_data_valid(self):
        """Test valid JSON data validation"""
        data = {"field1": "value1", "field2": "value2"}
        is_valid, errors = ValidationUtilities.validate_json_data(data, ["field1"])
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_json_data_missing_fields(self):
        """Test JSON data validation with missing required fields"""
        data = {"field1": "value1"}
        is_valid, errors = ValidationUtilities.validate_json_data(data, ["field1", "field2"])
        assert is_valid is False
        assert "Missing required field: field2" in errors
    
    def test_validate_json_data_null_values(self):
        """Test JSON data validation with null values"""
        data = {"field1": None, "field2": "value2"}
        is_valid, errors = ValidationUtilities.validate_json_data(data, ["field1"])
        assert is_valid is False
        assert "Field 'field1' cannot be null" in errors
    
    def test_validate_json_data_invalid_type(self):
        """Test JSON data validation with invalid data type"""
        data = "not a dict"
        is_valid, errors = ValidationUtilities.validate_json_data(data)
        assert is_valid is False
        assert "Data must be a JSON object" in errors
    
    def test_validate_text_length_valid(self):
        """Test valid text length validation"""
        is_valid, error = ValidationUtilities.validate_text_length("test", 1, 10)
        assert is_valid is True
        assert error == ""
    
    def test_validate_text_length_too_short(self):
        """Test text length validation - too short"""
        is_valid, error = ValidationUtilities.validate_text_length("hi", 5, 10)
        assert is_valid is False
        assert "must be at least 5 characters" in error
    
    def test_validate_text_length_too_long(self):
        """Test text length validation - too long"""
        is_valid, error = ValidationUtilities.validate_text_length("very long text", 1, 5)
        assert is_valid is False
        assert "must not exceed 5 characters" in error
    
    def test_validate_numeric_range_valid(self):
        """Test valid numeric range validation"""
        is_valid, error = ValidationUtilities.validate_numeric_range(5, 1, 10)
        assert is_valid is True
        assert error == ""
        
        is_valid, error = ValidationUtilities.validate_numeric_range(3.5, 0.0, 10.0)
        assert is_valid is True
        assert error == ""
    
    def test_validate_numeric_range_too_low(self):
        """Test numeric range validation - too low"""
        is_valid, error = ValidationUtilities.validate_numeric_range(0, 5, 10)
        assert is_valid is False
        assert "must be at least 5" in error
    
    def test_validate_numeric_range_too_high(self):
        """Test numeric range validation - too high"""
        is_valid, error = ValidationUtilities.validate_numeric_range(15, 1, 10)
        assert is_valid is False
        assert "must not exceed 10" in error


class TestFileValidator:
    """Test FileValidator class"""
    
    def test_validate_filename_valid(self):
        """Test valid filename validation"""
        is_valid, errors = FileValidator.validate_filename("test.txt")
        assert is_valid is True
        assert len(errors) == 0
        
        is_valid, errors = FileValidator.validate_filename("document_123.pdf")
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_filename_invalid_characters(self):
        """Test filename validation with invalid characters"""
        is_valid, errors = FileValidator.validate_filename("test<file>.txt")
        assert is_valid is False
        assert any("invalid characters" in error for error in errors)
    
    def test_validate_filename_directory_traversal(self):
        """Test filename validation against directory traversal"""
        is_valid, errors = FileValidator.validate_filename("../../../etc/passwd")
        assert is_valid is False
        assert any("invalid path characters" in error for error in errors)
        
        is_valid, errors = FileValidator.validate_filename("test\\file.txt")
        assert is_valid is False
        assert any("invalid path characters" in error for error in errors)
    
    def test_validate_filename_reserved_names(self):
        """Test filename validation against reserved names"""
        is_valid, errors = FileValidator.validate_filename("CON.txt")
        assert is_valid is False
        assert any("reserved system name" in error for error in errors)
        
        is_valid, errors = FileValidator.validate_filename("LPT1.pdf")
        assert is_valid is False
        assert any("reserved system name" in error for error in errors)
    
    def test_validate_filename_too_long(self):
        """Test filename validation - too long"""
        long_name = "a" * 300 + ".txt"
        is_valid, errors = FileValidator.validate_filename(long_name)
        assert is_valid is False
        assert any("too long" in error for error in errors)
    
    def test_validate_file_upload_valid(self):
        """Test valid file upload validation"""
        content = b"This is valid text content for testing"
        is_valid, errors = FileValidator.validate_file_upload("test.txt", content)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_file_upload_invalid_extension(self):
        """Test file upload validation with invalid extension"""
        content = b"test content"
        is_valid, errors = FileValidator.validate_file_upload("test.exe", content)
        assert is_valid is False
        assert any("not allowed" in error for error in errors)
    
    def test_validate_file_upload_too_large(self):
        """Test file upload validation - file too large"""
        large_content = b"x" * (60 * 1024 * 1024)  # 60MB
        is_valid, errors = FileValidator.validate_file_upload("test.txt", large_content)
        assert is_valid is False
        assert any("exceeds" in error and "limit" in error for error in errors)
    
    def test_validate_file_upload_security_issues(self):
        """Test file upload validation with security issues"""
        # Test executable header
        exe_header = b"\x4d\x5a"  # MZ header for PE files
        exe_content = exe_header + b"fake executable content"
        is_valid, errors = FileValidator.validate_file_upload("test.txt", exe_content)
        assert is_valid is False
        assert any("malicious" in error for error in errors)
        
        # Test script injection
        script_content = b"<script>alert('xss')</script>"
        is_valid, errors = FileValidator.validate_file_upload("test.txt", script_content)
        assert is_valid is False
        assert any("malicious" in error for error in errors)


class TestDataValidator:
    """Test DataValidator class"""
    
    def test_validate_document_structure_valid(self):
        """Test valid document structure validation"""
        document = {
            "content": "This is valid document content",
            "metadata": {"title": "Test Document"}
        }
        is_valid, errors = DataValidator.validate_document_structure(document)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_document_structure_missing_content(self):
        """Test document structure validation with missing content"""
        document = {"metadata": {"title": "Test"}}
        is_valid, errors = DataValidator.validate_document_structure(document)
        assert is_valid is False
        assert any("Missing required field: content" in error for error in errors)
    
    def test_validate_document_structure_empty_content(self):
        """Test document structure validation with empty content"""
        document = {"content": "   ", "metadata": {"title": "Test"}}
        is_valid, errors = DataValidator.validate_document_structure(document)
        assert is_valid is False
        assert any("cannot be empty" in error for error in errors)
    
    def test_validate_document_structure_invalid_content_type(self):
        """Test document structure validation with invalid content type"""
        document = {"content": 123, "metadata": {"title": "Test"}}
        is_valid, errors = DataValidator.validate_document_structure(document)
        assert is_valid is False
        assert any("must be a string" in error for error in errors)
    
    def test_validate_document_structure_invalid_metadata(self):
        """Test document structure validation with invalid metadata"""
        document = {"content": "test", "metadata": "not a dict"}
        is_valid, errors = DataValidator.validate_document_structure(document)
        assert is_valid is False
        assert any("must be a dictionary" in error for error in errors)
    
    def test_validate_generation_settings_valid(self):
        """Test valid generation settings validation"""
        settings = {
            "max_iterations": 3,
            "temperature": 0.7,
            "max_tokens": 500
        }
        is_valid, errors = DataValidator.validate_generation_settings(settings)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_generation_settings_invalid_iterations(self):
        """Test generation settings validation with invalid iterations"""
        settings = {"max_iterations": 15}  # Too high
        is_valid, errors = DataValidator.validate_generation_settings(settings)
        assert is_valid is False
        assert any("max_iterations" in error for error in errors)
    
    def test_validate_generation_settings_invalid_temperature(self):
        """Test generation settings validation with invalid temperature"""
        settings = {"temperature": 5.0}  # Too high
        is_valid, errors = DataValidator.validate_generation_settings(settings)
        assert is_valid is False
        assert any("temperature" in error for error in errors)
    
    def test_validate_generation_settings_invalid_tokens(self):
        """Test generation settings validation with invalid max_tokens"""
        settings = {"max_tokens": 10000}  # Too high
        is_valid, errors = DataValidator.validate_generation_settings(settings)
        assert is_valid is False
        assert any("max_tokens" in error for error in errors)


class TestAPIKeyValidator:
    """Test APIKeyValidator class"""
    
    def test_validate_openai_key_valid(self):
        """Test valid OpenAI API key validation"""
        is_valid, error = APIKeyValidator.validate_openai_key("sk-1234567890abcdef1234567890abcdef")
        assert is_valid is True
        assert error == ""
    
    def test_validate_openai_key_invalid_prefix(self):
        """Test OpenAI API key validation with invalid prefix"""
        is_valid, error = APIKeyValidator.validate_openai_key("invalid-1234567890abcdef")
        assert is_valid is False
        assert "must start with 'sk-'" in error
    
    def test_validate_openai_key_too_short(self):
        """Test OpenAI API key validation - too short"""
        is_valid, error = APIKeyValidator.validate_openai_key("sk-123")
        assert is_valid is False
        assert "too short" in error
    
    def test_validate_openai_key_invalid_characters(self):
        """Test OpenAI API key validation with invalid characters"""
        is_valid, error = APIKeyValidator.validate_openai_key("sk-123456789@#$%^&*()")
        assert is_valid is False
        assert "invalid characters" in error
    
    def test_validate_openai_key_empty(self):
        """Test OpenAI API key validation with empty key"""
        is_valid, error = APIKeyValidator.validate_openai_key("")
        assert is_valid is False
        assert "is required" in error
    
    def test_validate_langchain_key_valid(self):
        """Test valid LangChain API key validation"""
        is_valid, error = APIKeyValidator.validate_langchain_key("ls__1234567890abcdef1234567890abcdef")
        assert is_valid is True
        assert error == ""
    
    def test_validate_langchain_key_invalid_prefix(self):
        """Test LangChain API key validation with invalid prefix"""
        is_valid, error = APIKeyValidator.validate_langchain_key("invalid-1234567890abcdef")
        assert is_valid is False
        assert "must start with 'ls__'" in error
    
    def test_validate_langchain_key_too_short(self):
        """Test LangChain API key validation - too short"""
        is_valid, error = APIKeyValidator.validate_langchain_key("ls__123")
        assert is_valid is False
        assert "too short" in error
    
    def test_validate_langchain_key_empty(self):
        """Test LangChain API key validation with empty key"""
        is_valid, error = APIKeyValidator.validate_langchain_key("")
        assert is_valid is False
        assert "is required" in error
    
    def test_validate_api_keys_valid(self):
        """Test validation of multiple API keys - all valid"""
        openai_key = "sk-1234567890abcdef1234567890abcdef"
        langchain_key = "ls__1234567890abcdef1234567890abcdef"
        is_valid, errors = APIKeyValidator.validate_api_keys(openai_key, langchain_key)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_api_keys_mixed_validity(self):
        """Test validation of multiple API keys - mixed validity"""
        openai_key = "invalid-key"
        langchain_key = "ls__1234567890abcdef1234567890abcdef"
        is_valid, errors = APIKeyValidator.validate_api_keys(openai_key, langchain_key)
        assert is_valid is False
        assert any("OpenAI API key" in error for error in errors)
        assert not any("LangChain API key" in error for error in errors)


class TestValidationResult:
    """Test ValidationResult class"""
    
    def test_validation_result_initial_state(self):
        """Test ValidationResult initial state"""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validation_result_add_error(self):
        """Test adding error to ValidationResult"""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        assert result.is_valid is False
        assert "Test error" in result.errors
    
    def test_validation_result_add_warning(self):
        """Test adding warning to ValidationResult"""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        assert result.is_valid is True  # Warnings don't affect validity
        assert "Test warning" in result.warnings


class TestGenerationRequestValidation:
    """Test generation request validation functions"""
    
    def test_validate_generation_request_valid(self):
        """Test valid generation request validation"""
        doc1 = Document(content="Test document 1")
        doc2 = Document(content="Test document 2")
        request = GenerationRequest(documents=[doc1, doc2], max_iterations=3)
        
        is_valid, errors = validate_generation_request(request)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_generation_request_no_documents(self):
        """Test generation request validation with no documents"""
        request = GenerationRequest(documents=[], max_iterations=3)
        is_valid, errors = validate_generation_request(request)
        assert is_valid is False
        assert any("At least one document is required" in error for error in errors)
    
    def test_validate_generation_request_empty_content(self):
        """Test generation request validation with empty document content"""
        doc = Document(content="   ")  # Empty/whitespace content
        request = GenerationRequest(documents=[doc], max_iterations=3)
        is_valid, errors = validate_generation_request(request)
        assert is_valid is False
        assert any("empty content" in error for error in errors)
    
    def test_validate_generation_request_large_content(self):
        """Test generation request validation with large document content"""
        large_content = "x" * 1500000  # > 1MB
        doc = Document(content=large_content)
        request = GenerationRequest(documents=[doc], max_iterations=3)
        is_valid, errors = validate_generation_request(request)
        assert is_valid is False
        assert any("exceeds 1MB limit" in error for error in errors)
    
    def test_validate_generation_request_invalid_iterations(self):
        """Test generation request validation with invalid iterations"""
        doc = Document(content="Test content")
        request = GenerationRequest(documents=[doc], max_iterations=10)  # Too high
        is_valid, errors = validate_generation_request(request)
        assert is_valid is False
        assert any("between 1 and 5" in error for error in errors)


class TestEvaluationRequestValidation:
    """Test evaluation request validation functions"""
    
    def test_validate_evaluation_request_valid(self):
        """Test valid evaluation request validation"""
        request = EvaluationRequest(
            evolved_questions=[{"id": "q1", "question": "Test?"}],
            question_answers=[{"question_id": "q1", "answer": "Answer"}],
            question_contexts=[{"question_id": "q1", "context": "Context"}]
        )
        is_valid, errors = validate_evaluation_request(request)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_evaluation_request_missing_data(self):
        """Test evaluation request validation with missing data"""
        request = EvaluationRequest(
            evolved_questions=[],
            question_answers=[],
            question_contexts=[]
        )
        is_valid, errors = validate_evaluation_request(request)
        assert is_valid is False
        assert len(errors) >= 3  # Should have errors for all missing data
    
    def test_validate_evaluation_request_id_mismatch(self):
        """Test evaluation request validation with ID mismatches"""
        request = EvaluationRequest(
            evolved_questions=[{"id": "q1", "question": "Test?"}],
            question_answers=[{"question_id": "q2", "answer": "Answer"}],  # Wrong ID
            question_contexts=[{"question_id": "q1", "context": "Context"}]
        )
        is_valid, errors = validate_evaluation_request(request)
        assert is_valid is False
        assert any("mismatch" in error for error in errors)


class TestComprehensiveValidation:
    """Test comprehensive request validation"""
    
    def test_comprehensive_validation_generation_valid(self):
        """Test comprehensive validation for valid generation request"""
        request_data = {
            "documents": [
                {"content": "Test document 1"},
                {"content": "Test document 2"}
            ],
            "settings": {
                "max_iterations": 3,
                "temperature": 0.7
            }
        }
        result = comprehensive_request_validation(request_data, "generation")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_comprehensive_validation_generation_invalid(self):
        """Test comprehensive validation for invalid generation request"""
        request_data = {
            "documents": [],  # Empty documents
            "settings": {
                "max_iterations": 15,  # Too high
                "temperature": 5.0     # Too high
            }
        }
        result = comprehensive_request_validation(request_data, "generation")
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_comprehensive_validation_evaluation_valid(self):
        """Test comprehensive validation for valid evaluation request"""
        request_data = {
            "evolved_questions": [{"id": "q1", "question": "Test?"}],
            "question_answers": [{"question_id": "q1", "answer": "Answer"}],
            "question_contexts": [{"question_id": "q1", "context": "Context"}]
        }
        result = comprehensive_request_validation(request_data, "evaluation")
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_comprehensive_validation_evaluation_invalid(self):
        """Test comprehensive validation for invalid evaluation request"""
        request_data = {
            "evolved_questions": "not a list",  # Wrong type
            "question_answers": [],             # Empty
            "question_contexts": []             # Empty
        }
        result = comprehensive_request_validation(request_data, "evaluation")
        assert result.is_valid is False
        assert len(result.errors) > 0 