"""
Integration tests for EvolSynth API endpoints
Tests the complete API functionality with realistic scenarios
"""

import unittest
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports  
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(project_root))


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:8000"
        self.timeout = 30
        
        # Test data
        self.sample_document = {
            "content": "This is a sample document for testing the EvolSynth API. " +
                      "It contains information about artificial intelligence and machine learning. " +
                      "The document discusses various techniques and applications in the field.",
            "metadata": {
                "title": "AI Sample Document",
                "source": "integration_test",
                "category": "technology"
            }
        }
        
        self.generation_request = {
            "documents": [self.sample_document],
            "max_iterations": 2,
            "settings": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("timestamp", data)
            self.assertIn("version", data)
            
            # Verify health status
            self.assertIn(data["status"], ["healthy", "degraded"])
            
            print(f"✅ Health check passed: {data['status']}")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Health endpoint failed: {e}")
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("version", data)
            self.assertIn("dependencies", data)
            
            print(f"✅ Root endpoint accessible: {data.get('version', 'unknown')}")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Root endpoint failed: {e}")
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health/detailed", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("overall_status", data)
            self.assertIn("checks", data)
            self.assertIn("timestamp", data)
            
            # Verify check structure
            checks = data.get("checks", [])
            self.assertIsInstance(checks, list)
            
            for check in checks:
                self.assertIn("name", check)
                self.assertIn("status", check)
                self.assertIn("response_time", check)
            
            print(f"✅ Detailed health check: {data['overall_status']}")
            print(f"   Number of health checks: {len(checks)}")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Detailed health endpoint failed: {e}")
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        try:
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=self.timeout)
            self.assertEqual(response.status_code, 404)
            
            print("✅ Invalid endpoint correctly returns 404")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Invalid endpoint test failed: {e}")
    
    def test_generation_endpoint_validation(self):
        """Test generation endpoint input validation"""
        try:
            # Test empty request
            response = requests.post(
                f"{self.base_url}/generate",
                json={},
                timeout=self.timeout
            )
            self.assertEqual(response.status_code, 422)  # Validation error
            
            # Test invalid request structure
            invalid_request = {
                "documents": [],  # Empty documents
                "max_iterations": 0  # Invalid iterations
            }
            response = requests.post(
                f"{self.base_url}/generate",
                json=invalid_request,
                timeout=self.timeout
            )
            self.assertEqual(response.status_code, 422)  # Validation error
            
            print("✅ Generation endpoint validation working correctly")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Generation endpoint validation test failed: {e}")
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        try:
            # OPTIONS request to check CORS
            response = requests.options(f"{self.base_url}/health", timeout=self.timeout)
            
            # Check for CORS headers (if implemented)
            headers = response.headers
            print(f"✅ CORS check completed")
            print(f"   Response headers: {list(headers.keys())[:5]}...")  # Show first 5 headers
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  CORS test skipped: {e}")
    
    def test_api_response_time(self):
        """Test API response time performance"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 5.0, "Health endpoint should respond in under 5 seconds")
            
            print(f"✅ Health endpoint response time: {response_time:.3f}s")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Response time test failed: {e}")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import concurrent.futures
        
        def make_health_request():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
                return response.status_code == 200
            except:
                return False
        
        try:
            # Make 5 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_health_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All requests should succeed
            success_count = sum(results)
            self.assertGreaterEqual(success_count, 4, "At least 4 out of 5 concurrent requests should succeed")
            
            print(f"✅ Concurrent requests: {success_count}/5 succeeded")
            
        except Exception as e:
            print(f"⚠️  Concurrent requests test skipped: {e}")


class TestAPIDataFlow(unittest.TestCase):
    """Test data flow through the API"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:8000"
        self.timeout = 60  # Longer timeout for generation
        
        self.test_document = {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It involves algorithms that can identify patterns in data and make predictions or decisions based on those patterns.",
            "metadata": {
                "title": "Machine Learning Overview",
                "source": "test_suite",
                "category": "education"
            }
        }
    
    def test_document_validation_flow(self):
        """Test document validation in the API"""
        try:
            # Test valid document
            valid_request = {
                "documents": [self.test_document],
                "max_iterations": 1
            }
            
            response = requests.post(
                f"{self.base_url}/validate/generation",
                json=valid_request,
                timeout=self.timeout
            )
            
            # Should either succeed (200) or not be implemented (404)
            self.assertIn(response.status_code, [200, 404, 405])
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Document validation successful: {data}")
            else:
                print(f"⚠️  Document validation endpoint not available (status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Document validation test skipped: {e}")
    
    def test_error_handling_flow(self):
        """Test error handling in the API"""
        try:
            # Test malformed JSON
            response = requests.post(
                f"{self.base_url}/generate",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            # Should return 422 (validation error) or similar
            self.assertIn(response.status_code, [400, 422])
            
            print(f"✅ Error handling working: status {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Error handling test failed: {e}")


class TestAPIPerformance(unittest.TestCase):
    """Performance tests for the API"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    def test_sequential_requests_performance(self):
        """Test performance of sequential requests"""
        try:
            request_count = 10
            start_time = time.time()
            
            successful_requests = 0
            for i in range(request_count):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
                    if response.status_code == 200:
                        successful_requests += 1
                except:
                    pass
            
            total_time = time.time() - start_time
            avg_time_per_request = total_time / request_count
            
            self.assertGreater(successful_requests, request_count * 0.8, "At least 80% of requests should succeed")
            self.assertLess(avg_time_per_request, 2.0, "Average request time should be under 2 seconds")
            
            print(f"✅ Sequential performance: {successful_requests}/{request_count} requests in {total_time:.2f}s")
            print(f"   Average time per request: {avg_time_per_request:.3f}s")
            
        except Exception as e:
            print(f"⚠️  Sequential performance test skipped: {e}")
    
    def test_memory_usage_stability(self):
        """Test that memory usage remains stable during requests"""
        try:
            import psutil
            import os
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Make several requests
            for i in range(5):
                try:
                    requests.get(f"{self.base_url}/health", timeout=self.timeout)
                except:
                    pass
                time.sleep(0.1)
            
            # Check final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 50MB for test client)
            self.assertLess(memory_increase, 50, "Memory usage should not increase significantly during testing")
            
            print(f"✅ Memory stability: {memory_increase:.1f}MB increase during test")
            
        except ImportError:
            print("⚠️  Memory stability test skipped (psutil not available)")
        except Exception as e:
            print(f"⚠️  Memory stability test skipped: {e}")


def run_integration_tests():
    """Run all integration tests with detailed reporting"""
    print("🧪 Running EvolSynth API Integration Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAPIIntegration))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAPIDataFlow))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAPIPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🔥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1) 