"""
Comprehensive testing and validation script for the platform.
Tests all critical components and functionality.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import requests

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

class PlatformTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.test_results = []
        self.user_id = None

    def log_test(self, test_name: str, passed: bool, message: str = "", duration: float = 0):
        """Log a test result."""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        status = "PASS" if passed else "FAIL"
        print(f"{status} | {test_name} ({duration:.2f}s)")
        if message:
            print(f"         {message}")

    def test_api_health(self) -> bool:
        """Test API health endpoint."""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, 
                            f"Status: {data.get('status')}, Environment: {data.get('environment')}", 
                            duration)
                return True
            else:
                self.log_test("API Health Check", False, 
                            f"Unexpected status code: {response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("API Health Check", False, f"Error: {str(e)}", duration)
            return False

    def test_auth_login(self) -> bool:
        """Test user authentication login."""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=TEST_USER,
                timeout=10
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.user_id = data.get("user", {}).get("id")
                    self.log_test("Authentication Login", True, 
                                f"User logged in: {data.get('user', {}).get('email')}", 
                                duration)
                    return True
                else:
                    self.log_test("Authentication Login", False, 
                                "No access token in response", 
                                duration)
                    return False
            else:
                self.log_test("Authentication Login", False, 
                            f"Login failed with status: {response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Authentication Login", False, f"Error: {str(e)}", duration)
            return False

    def test_auth_me(self) -> bool:
        """Test getting current user info."""
        if not self.token:
            self.log_test("Get Current User", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers,
                timeout=5
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Current User", True, 
                            f"User: {data.get('email', 'Unknown')}", 
                            duration)
                return True
            else:
                self.log_test("Get Current User", False, 
                            f"Failed with status: {response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Get Current User", False, f"Error: {str(e)}", duration)
            return False

    def test_competitors_list(self) -> bool:
        """Test getting competitors list."""
        if not self.token:
            self.log_test("Competitors List", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/competitors",
                headers=headers,
                timeout=5
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                competitors = data.get("competitors", [])
                self.log_test("Competitors List", True, 
                            f"Found {len(competitors)} competitors", 
                            duration)
                return True
            else:
                self.log_test("Competitors List", False, 
                            f"Failed with status: {response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Competitors List", False, f"Error: {str(e)}", duration)
            return False

    def test_alerts_crud(self) -> bool:
        """Test alerts CRUD operations."""
        if not self.token:
            self.log_test("Alerts CRUD", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test Create Alert
            alert_data = {
                "title": "Test Alert",
                "message": "This is a test alert",
                "alert_type": "competitor_activity",
                "priority": "high",
                "status": "pending"
            }
            
            create_response = requests.post(
                f"{self.base_url}/api/v1/alerts",
                headers=headers,
                json=alert_data,
                timeout=5
            )
            
            if create_response.status_code != 201:
                duration = time.time() - start_time
                self.log_test("Alerts CRUD", False, 
                            f"Create alert failed: {create_response.status_code}", 
                            duration)
                return False
            
            alert_id = create_response.json().get("id")
            
            # Test Read Alert
            read_response = requests.get(
                f"{self.base_url}/api/v1/alerts",
                headers=headers,
                timeout=5
            )
            
            # Test Update Alert
            update_data = {"title": "Updated Test Alert"}
            update_response = requests.put(
                f"{self.base_url}/api/v1/alerts/{alert_id}",
                headers=headers,
                json=update_data,
                timeout=5
            )
            
            # Test Delete Alert
            delete_response = requests.delete(
                f"{self.base_url}/api/v1/alerts/{alert_id}",
                headers=headers,
                timeout=5
            )
            
            duration = time.time() - start_time
            
            if all([
                read_response.status_code == 200,
                update_response.status_code == 200,
                delete_response.status_code == 200
            ]):
                self.log_test("Alerts CRUD", True, 
                            "Create, Read, Update, Delete operations successful", 
                            duration)
                return True
            else:
                self.log_test("Alerts CRUD", False, 
                            f"Some operations failed: Read={read_response.status_code}, "
                            f"Update={update_response.status_code}, Delete={delete_response.status_code}", 
                            duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Alerts CRUD", False, f"Error: {str(e)}", duration)
            return False

    def test_reports_generation(self) -> bool:
        """Test report generation and download."""
        if not self.token:
            self.log_test("Reports Generation", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test Generate Report
            report_data = {
                "title": "Test Report",
                "description": "This is a test report",
                "report_type": "competitor",
                "format": "pdf",
                "parameters": {}
            }
            
            generate_response = requests.post(
                f"{self.base_url}/api/v1/reports/generate",
                headers=headers,
                json=report_data,
                timeout=10
            )
            
            if generate_response.status_code != 201:
                duration = time.time() - start_time
                self.log_test("Reports Generation", False, 
                            f"Generate report failed: {generate_response.status_code}", 
                            duration)
                return False
            
            report_id = generate_response.json().get("id")
            
            # Test Download Report
            download_response = requests.get(
                f"{self.base_url}/api/v1/reports/{report_id}/download",
                headers=headers,
                timeout=10
            )
            
            duration = time.time() - start_time
            
            if download_response.status_code == 200:
                file_size = len(download_response.content)
                self.log_test("Reports Generation", True, 
                            f"Report generated and downloaded: {file_size} bytes", 
                            duration)
                return True
            else:
                self.log_test("Reports Generation", False, 
                            f"Download failed: {download_response.status_code}", 
                            duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Reports Generation", False, f"Error: {str(e)}", duration)
            return False

    def test_market_trends(self) -> bool:
        """Test market trends endpoint."""
        if not self.token:
            self.log_test("Market Trends", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/market/trends",
                headers=headers,
                timeout=5
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                trends = data.get("trends", [])
                self.log_test("Market Trends", True, 
                            f"Found {len(trends)} market trends", 
                            duration)
                return True
            else:
                self.log_test("Market Trends", False, 
                            f"Failed with status: {response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Market Trends", False, f"Error: {str(e)}", duration)
            return False

    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        start_time = time.time()
        try:
            # Test /docs redirect
            docs_response = requests.get(f"{self.base_url}/docs", timeout=5, allow_redirects=False)
            
            # Test API spec
            spec_response = requests.get(f"{self.base_url}/api/v1/openapi.json", timeout=5)
            
            duration = time.time() - start_time
            
            if docs_response.status_code in [200, 307, 308] and spec_response.status_code == 200:
                self.log_test("API Documentation", True, 
                            "Documentation endpoints accessible", 
                            duration)
                return True
            else:
                self.log_test("API Documentation", False, 
                            f"Docs: {docs_response.status_code}, Spec: {spec_response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("API Documentation", False, f"Error: {str(e)}", duration)
            return False

    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests."""
        if not self.token:
            self.log_test("Error Handling", False, "No authentication token")
            return False

        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test invalid endpoint
            invalid_response = requests.get(
                f"{self.base_url}/api/v1/invalid_endpoint",
                headers=headers,
                timeout=5
            )
            
            # Test invalid method
            invalid_method_response = requests.post(
                f"{self.base_url}/api/v1/health",
                headers=headers,
                timeout=5
            )
            
            duration = time.time() - start_time
            
            if invalid_response.status_code == 404 and invalid_method_response.status_code == 405:
                self.log_test("Error Handling", True, 
                            "Proper error responses for invalid requests", 
                            duration)
                return True
            else:
                self.log_test("Error Handling", False, 
                            f"Unexpected error responses: {invalid_response.status_code}, "
                            f"{invalid_method_response.status_code}", 
                            duration)
                return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling", False, f"Error: {str(e)}", duration)
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all platform tests."""
        print("=" * 60)
        print("STARTING COMPREHENSIVE PLATFORM TESTING")
        print("=" * 60)
        
        # Core functionality tests
        self.test_api_health()
        self.test_auth_login()
        self.test_auth_me()
        
        # API endpoint tests
        self.test_competitors_list()
        self.test_alerts_crud()
        self.test_reports_generation()
        self.test_market_trends()
        
        # Additional tests
        self.test_api_documentation()
        self.test_error_handling()
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate total duration
        total_duration = sum(result["duration"] for result in self.test_results)
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        print("=" * 60)
        
        if failed_tests == 0:
            print("ALL TESTS PASSED! PLATFORM IS FULLY FUNCTIONAL!")
        else:
            print(f"{failed_tests} TEST(S) FAILED. PLEASE REVIEW THE ISSUES.")
        
        print("=" * 60)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "results": self.test_results
        }

    def save_results(self, filename: str = "test_results.json"):
        """Save test results to file."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for result in self.test_results if result["passed"]),
            "failed_tests": sum(1 for result in self.test_results if not result["passed"]),
            "results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Test results saved to {filename}")

if __name__ == "__main__":
    tester = PlatformTester()
    results = tester.run_all_tests()
    tester.save_results()
    
    # Exit with appropriate code
    exit(0 if results["failed_tests"] == 0 else 1)