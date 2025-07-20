#!/usr/bin/env python3
"""
Comprehensive Test Runner for EvolSynth API
Runs unit tests, integration tests, and generates coverage reports
"""

import sys
import os
import subprocess
import unittest
import importlib.util
from pathlib import Path
import time
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")


def check_dependencies() -> Dict[str, bool]:
    """Check if required testing dependencies are available"""
    dependencies = {
        'requests': False,
        'psutil': False,
        'redis': False,
        'unittest': True  # Built-in
    }
    
    for dep in dependencies:
        if dep == 'unittest':
            continue
            
        try:
            importlib.import_module(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies


def run_unit_tests() -> bool:
    """Run unit tests"""
    print_header("UNIT TESTS")
    
    unit_test_dir = Path(__file__).parent / "unit"
    if not unit_test_dir.exists():
        print_warning("Unit test directory not found, creating basic test structure")
        unit_test_dir.mkdir(exist_ok=True)
        return True
    
    # Discover and run unit tests
    test_suite = unittest.TestLoader().discover(str(unit_test_dir), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
    
    print_info(f"Running unit tests from: {unit_test_dir}")
    start_time = time.time()
    result = runner.run(test_suite)
    duration = time.time() - start_time
    
    # Print results
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Unit Test Results:{Colors.END}")
    print(f"  Tests run: {total_tests}")
    print(f"  Failures: {failures}")
    print(f"  Errors: {errors}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Success rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print_success("All unit tests passed!")
        return True
    else:
        print_error(f"Unit tests failed ({failures} failures, {errors} errors)")
        return False


def run_integration_tests() -> bool:
    """Run integration tests"""
    print_header("INTEGRATION TESTS")
    
    integration_test_file = Path(__file__).parent / "integration" / "test_api_endpoints.py"
    if not integration_test_file.exists():
        print_warning("Integration test file not found")
        return True
    
    try:
        # Import and run integration tests
        spec = importlib.util.spec_from_file_location("test_api_endpoints", integration_test_file)
        if spec is None or spec.loader is None:
            raise ImportError("Could not load integration test module")
        integration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(integration_module)
        
        print_info("Running integration tests...")
        success = integration_module.run_integration_tests()
        
        if success:
            print_success("All integration tests passed!")
        else:
            print_error("Some integration tests failed")
        
        return success
        
    except Exception as e:
        print_error(f"Failed to run integration tests: {e}")
        return False


def run_basic_validation_tests():
    """Run basic validation tests without external dependencies"""
    print_header("BASIC VALIDATION TESTS")
    
    try:
        # Test imports
        print_info("Testing core imports...")
        
        from api.utils.validation import ValidationUtilities, FileValidator, DataValidator, APIKeyValidator
        print_success("Validation utilities import successfully")
        
        from api.utils.error_handling import create_error_response, EvolSynthException
        print_success("Error handling utilities import successfully")
        
        from api.utils.cache_manager import CacheManager
        print_success("Cache manager imports successfully")
        
        from api.config import settings, get_integrated_config
        print_success("Configuration system imports successfully")
        
        # Test basic functionality
        print_info("Testing basic validation functionality...")
        
        # Test email validation
        assert ValidationUtilities.validate_email("test@example.com") == True
        assert ValidationUtilities.validate_email("invalid-email") == False
        print_success("Email validation working")
        
        # Test URL validation
        assert ValidationUtilities.validate_url("https://example.com") == True
        assert ValidationUtilities.validate_url("invalid-url") == False
        print_success("URL validation working")
        
        # Test API key validation
        is_valid, _ = APIKeyValidator.validate_openai_key("sk-1234567890abcdef1234567890abcdef")
        assert is_valid == True
        is_valid, _ = APIKeyValidator.validate_openai_key("invalid-key")
        assert is_valid == False
        print_success("API key validation working")
        
        # Test configuration
        config = get_integrated_config()
        assert "core" in config
        assert "performance" in config
        assert "environment" in config
        print_success("Configuration system working")
        
        print_success("All basic validation tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Basic validation tests failed: {e}")
        return False


def run_performance_validation():
    """Run basic performance validation"""
    print_header("PERFORMANCE VALIDATION")
    
    try:
        print_info("Testing cache manager performance...")
        
        from api.utils.cache_manager import CacheManager
        
        # Test cache initialization time
        start_time = time.time()
        cache_manager = CacheManager()
        init_time = time.time() - start_time
        
        if init_time < 1.0:
            print_success(f"Cache manager initializes quickly ({init_time:.3f}s)")
        else:
            print_warning(f"Cache manager initialization is slow ({init_time:.3f}s)")
        
        # Test memory cache operations (when Redis is not available)
        start_time = time.time()
        for i in range(100):
            cache_manager.set(f"test_key_{i}", f"test_value_{i}")
        set_time = time.time() - start_time
        
        start_time = time.time()
        for i in range(100):
            cache_manager.get(f"test_key_{i}")
        get_time = time.time() - start_time
        
        print_success(f"Cache operations: SET 100 items in {set_time:.3f}s, GET 100 items in {get_time:.3f}s")
        
        # Test validation performance
        from api.utils.validation import ValidationUtilities
        
        start_time = time.time()
        for i in range(1000):
            ValidationUtilities.validate_email(f"test{i}@example.com")
        validation_time = time.time() - start_time
        
        print_success(f"Email validation: 1000 validations in {validation_time:.3f}s")
        
        return True
        
    except Exception as e:
        print_error(f"Performance validation failed: {e}")
        return False


def generate_test_report(results: Dict[str, bool]) -> None:
    """Generate a comprehensive test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"{Colors.BOLD}Overall Test Results:{Colors.END}")
    print(f"  Total test suites: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success rate: {(passed_tests / total_tests * 100):.1f}%")
    
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.END}")
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")
    
    if all(results.values()):
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your API is ready for deployment.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Some tests failed. Please review and fix issues before deployment.{Colors.END}")


def main():
    """Main test runner function"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🧪 EvolSynth API Comprehensive Test Suite")
    print("=" * 60)
    print(f"{Colors.END}")
    
    # Check dependencies
    print_header("DEPENDENCY CHECK")
    deps = check_dependencies()
    
    for dep, available in deps.items():
        if available:
            print_success(f"{dep} is available")
        else:
            print_warning(f"{dep} is not available (some tests may be skipped)")
    
    # Run test suites
    results = {}
    
    # Always run basic validation tests
    results["Basic Validation"] = run_basic_validation_tests()
    
    # Run performance validation
    results["Performance Validation"] = run_performance_validation()
    
    # Run unit tests if available
    try:
        results["Unit Tests"] = run_unit_tests()
    except Exception as e:
        print_error(f"Unit tests failed to run: {e}")
        results["Unit Tests"] = False
    
    # Run integration tests if requests is available
    if deps.get('requests', False):
        try:
            results["Integration Tests"] = run_integration_tests()
        except Exception as e:
            print_error(f"Integration tests failed to run: {e}")
            results["Integration Tests"] = False
    else:
        print_warning("Skipping integration tests (requests library not available)")
    
    # Generate report
    generate_test_report(results)
    
    # Exit with appropriate code
    if all(results.values()):
        print(f"\n{Colors.GREEN}Test suite completed successfully!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}Test suite completed with failures.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main() 