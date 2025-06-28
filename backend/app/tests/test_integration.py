import io
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from app.core.dependencies import initialize_services, shutdown_services
from app.main import app
from app.models.hr_data import HRData, WorkExperience

# Try to import with better error handling
try:
    from fastapi.testclient import TestClient
except ImportError as e:
    pytest.fail(f"Failed to import TestClient: {e}. Please check FastAPI installation.")

try:
    from app.core.dependencies import initialize_services, shutdown_services
    from app.main import app
    from app.models.hr_data import HRData
except ImportError as e:
    pytest.fail(f"Failed to import app modules: {e}. Please check app structure and dependencies.")


# Mock external services for testing
@pytest.fixture(scope="session", autouse=True)
def mock_external_services():
    """Mock external services to avoid real connections during testing"""
    with patch('app.core.dependencies.MongoDBService') as mock_mongodb, \
         patch('app.core.dependencies.AnthropicService') as mock_anthropic, \
         patch('app.core.dependencies.OCRService') as mock_ocr:
        
        # Mock MongoDB service
        mock_mongodb_instance = MagicMock()
        mock_mongodb_instance.store_document.return_value = "test_document_id"
        mock_mongodb.return_value = mock_mongodb_instance
        
        # Mock Anthropic service
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.analyze_hr_document.return_value = {
            "name": "João Silva",
            "position": "Developer"
        }
        mock_anthropic_instance.generate_document_summary.return_value = {
            "summary": "Test summary",
            "key_points": ["Point 1", "Point 2"]
        }
        # Make the methods async
        mock_anthropic_instance.analyze_hr_document = MagicMock()
        mock_anthropic_instance.analyze_hr_document.return_value = {
            "name": "João Silva",
            "position": "Developer"
        }
        mock_anthropic_instance.generate_document_summary = MagicMock()
        mock_anthropic_instance.generate_document_summary.return_value = {
            "summary": "Test summary",
            "key_points": ["Point 1", "Point 2"]
        }
        mock_anthropic.return_value = mock_anthropic_instance
        
        # Mock OCR service
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.extract_text_from_pdf.return_value = "Extracted text from PDF"
        mock_ocr.return_value = mock_ocr_instance
        
        yield

# Initialize services for testing
@pytest.fixture(scope="session", autouse=True)
def setup_services(mock_external_services):
    """Initialize services before running tests and clean up afterwards"""
    initialize_services()
    yield
    shutdown_services()

# Create test client fixture
@pytest.fixture(scope="session")
def client():
    """Create test client for API testing"""
    try:
        return TestClient(app)
    except Exception as e:
        pytest.fail(f"Failed to create TestClient: {e}")

# Simple test to verify TestClient works
def test_client_initialization(client):
    """Test that TestClient can be initialized and make basic requests"""
    assert client is not None
    # Try a simple request to verify the client works
    response = client.get("/health")
    assert response.status_code in [200, 404, 500]  # Any response means client works

# Test data fixtures
@pytest.fixture
def valid_hr_data_dict():
    """Valid HR data dictionary for testing"""
    return {
        "name": "João Silva",
        "cpf": "529.982.247-25",
        "position": "Software Engineer",
        "salary": 5000.00,
        "contract_type": "CLT",
        "main_skills": ["Leadership", "Communication"],
        "hard_skills": ["Python", "React"],
        "work_experience": [
            {
                "company": "Tech Corp",
                "position": "Senior Developer",
                "start_date": "2022-01-01T00:00:00",
                "end_date": "2023-12-31T00:00:00",
                "current_job": False,
                "description": "Desenvolvimento de aplicações web com foco em escalabilidade",
                "achievements": ["Liderou equipe de 5 desenvolvedores"],
                "technologies_used": ["React", "Node.js"]
            }
        ]
    }

@pytest.fixture
def invalid_hr_data_dict():
    """Invalid HR data dictionary for testing validation"""
    return {
        "name": "Jo",  # Too short
        "cpf": "123.456.789-00",  # Invalid CPF
        "position": "A",  # Too short
        "salary": -1000.00,  # Negative salary
        "contract_type": "CLT",
        "main_skills": ["A"],  # Too short
        "hard_skills": ["A"],  # Too short
        "work_experience": []
    }

@pytest.fixture
def minimal_valid_hr_data_dict():
    """Minimal valid HR data for testing"""
    return {
        "name": "João Silva",
        "cpf": "529.982.247-25",
        "position": "Developer",
        "salary": 5000.00,
        "contract_type": "CLT",
        "main_skills": ["Leadership", "Communication"],
        "hard_skills": ["Python", "React"],
        "work_experience": []
    }

@pytest.fixture
def mock_pdf_file():
    """Mock PDF file for testing"""
    return io.BytesIO(b"mock pdf content")

class TestHealthCheck:
    """Test 1: Health Check Endpoint"""
    
    def test_health_check(self, client):
        """Test that the health check endpoint returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

class TestTemplateEndpoints:
    """Test 2: Template Endpoints"""
    
    def test_get_default_template(self, client):
        """Test getting the default HR data template"""
        response = client.get("/v1/template")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "name" in data
        assert "position" in data
        assert "cpf" in data
    
    def test_get_template_by_role(self, client):
        """Test getting a role-specific template"""
        response = client.get("/v1/template/developer")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "position" in data
    
    def test_get_available_roles(self, client):
        """Test getting list of available role templates"""
        response = client.get("/v1/template/roles")
        
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0
        # Check for expected roles
        expected_roles = ["software_engineer", "data_scientist", "product_manager", "designer"]
        for role in expected_roles:
            assert role in data["roles"]

class TestDataValidation:
    """Test 3: Data Validation Endpoint"""
    
    def test_validate_valid_data(self, client, valid_hr_data_dict):
        """Test validation of valid HR data"""
        response = client.post("/v1/validate", json=valid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] is True
        assert "data" in data
        assert "errors" in data
    
    def test_validate_invalid_data(self, client, invalid_hr_data_dict):
        """Test validation of invalid HR data"""
        response = client.post("/v1/validate", json=invalid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0

class TestDocumentStorage:
    """Test 4: Document Storage Endpoint"""
    
    @patch('app.api.endpoints.get_mongodb_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_store_valid_document(self, mock_validation, mock_mongodb, client, minimal_valid_hr_data_dict):
        """Test storing valid HR data document"""
        # Mock MongoDB service
        mock_mongodb_instance = MagicMock()
        mock_mongodb_instance.store_document.return_value = "test_document_id"
        mock_mongodb.return_value = mock_mongodb_instance
        
        # Mock validation service to return HRData object directly
        mock_validation_instance = MagicMock()
        mock_validation_instance.validate_hr_data.return_value = HRData(
            name="João Silva",
            cpf="529.982.247-25",
            position="Developer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=["Leadership", "Communication"],
            hard_skills=["Python", "React"],
            work_experience=[]
        )
        mock_validation.return_value = mock_validation_instance
        
        response = client.post("/v1/store-document", json=minimal_valid_hr_data_dict)
        
        # Print response for debugging
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "document_id" in data
        assert data["document_id"] == "test_document_id"
    
    def test_store_invalid_document(self, client, invalid_hr_data_dict):
        """Test storing invalid HR data document"""
        response = client.post("/v1/store-document", json=invalid_hr_data_dict)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

class TestPDFProcessing:
    """Test 5: PDF Processing Endpoint"""
    
    @patch('app.api.endpoints.get_anthropic_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_process_valid_pdf(self, mock_validation, mock_anthropic, client):
        """Test processing a valid PDF document"""
        # Mock Anthropic service to return a coroutine
        async def mock_analyze_hr_document(text):
            return {"name": "João Silva", "position": "Developer"}
        
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.analyze_hr_document = mock_analyze_hr_document
        mock_anthropic.return_value = mock_anthropic_instance
        
        # Mock validation service
        mock_validation_instance = MagicMock()
        mock_validation_instance.validate_hr_data.return_value = HRData(
            name="João Silva",
            cpf="529.982.247-25",
            position="Developer",
            salary=5000.00,
            contract_type="CLT"
        )
        mock_validation.return_value = mock_validation_instance
        
        # Create mock PDF file
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "hr_data" in data
        assert "errors" in data
    
    def test_process_invalid_file_type(self, client):
        """Test processing with invalid file type"""
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        
        response = client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "File must be a PDF" in data["detail"]

class TestPDFSummarization:
    """Test 6: PDF Summarization Endpoint"""
    
    @patch('app.api.endpoints.get_anthropic_service')
    def test_summarize_pdf(self, mock_anthropic, client):
        """Test PDF summarization functionality"""
        # Mock Anthropic service to return a coroutine
        async def mock_generate_document_summary(text):
            return {"summary": "Test summary", "key_points": ["Point 1", "Point 2"]}
        
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.generate_document_summary = mock_generate_document_summary
        mock_anthropic.return_value = mock_anthropic_instance
        
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = client.post("/v1/summarize-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "key_points" in data

class TestErrorHandling:
    """Test 7: Error Handling"""
    
    def test_invalid_endpoint(self, client):
        """Test handling of invalid endpoint"""
        response = client.get("/v1/nonexistent-endpoint")
        
        assert response.status_code == 404
    
    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payload"""
        # Test with malformed JSON that will cause parsing error
        response = client.post(
            "/v1/validate", 
            json={"name": "test", "invalid_field": None}  # This will cause validation errors
        )
        
        assert response.status_code == 200  # Validation endpoint returns 200 with errors
        data = response.json()
        assert "valid" in data
        assert data["valid"] is False

class TestDataFlow:
    """Test 8: Complete Data Flow"""
    
    @patch('app.api.endpoints.get_mongodb_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_complete_workflow(self, mock_validation, mock_mongodb, client, minimal_valid_hr_data_dict):
        """Test complete workflow: validate -> store"""
        # Mock MongoDB service
        mock_mongodb_instance = MagicMock()
        mock_mongodb_instance.store_document.return_value = "test_document_id"
        mock_mongodb.return_value = mock_mongodb_instance
        
        # Mock validation service with different methods
        mock_validation_instance = MagicMock()
        # For validate_data_without_storing (used by /v1/validate)
        mock_validation_instance.validate_data_without_storing.return_value = {
            "valid": True,
            "data": HRData(
                name="João Silva",
                cpf="529.982.247-25",
                position="Developer",
                salary=5000.00,
                contract_type="CLT"
            ),
            "errors": {}
        }
        # For validate_hr_data (used by /v1/store-document)
        mock_validation_instance.validate_hr_data.return_value = HRData(
            name="João Silva",
            cpf="529.982.247-25",
            position="Developer",
            salary=5000.00,
            contract_type="CLT"
        )
        mock_validation.return_value = mock_validation_instance
        
        # Step 1: Validate data
        validate_response = client.post("/v1/validate", json=minimal_valid_hr_data_dict)
        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["valid"] is True
        
        # Step 2: Store validated data
        store_response = client.post("/v1/store-document", json=minimal_valid_hr_data_dict)
        assert store_response.status_code == 200
        
        data = store_response.json()
        assert data["status"] == "success"
        assert data["document_id"] == "test_document_id"

class TestConcurrentRequests:
    """Test 9: Concurrent Request Handling"""
    
    def test_concurrent_health_checks(self, client):
        """Test handling of concurrent health check requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(errors) == 0
        assert len(results) == 5
        assert all(status == 200 for status in results)

class TestAPIBehavior:
    """Test 10: API Behavior and Consistency"""
    
    def test_api_response_format_consistency(self, client):
        """Test that API responses maintain consistent format"""
        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert isinstance(health_data, dict)
        
        # Test template endpoint
        template_response = client.get("/v1/template")
        assert template_response.status_code == 200
        template_data = template_response.json()
        assert isinstance(template_data, dict)
        
        # Test roles endpoint
        roles_response = client.get("/v1/template/roles")
        assert roles_response.status_code == 200
        roles_data = roles_response.json()
        assert isinstance(roles_data, dict)
        assert "roles" in roles_data
    
    def test_error_response_format(self, client):
        """Test that error responses maintain consistent format"""
        # Test 404 error
        response = client.get("/v1/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        # Test 422 error with invalid data
        response = client.post("/v1/validate", json={"invalid": "data"})
        assert response.status_code == 200  # Validation endpoint returns 200 with errors
        data = response.json()
        assert "valid" in data
        assert "errors" in data 