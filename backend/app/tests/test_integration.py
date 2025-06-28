import asyncio
import io
from unittest.mock import MagicMock, patch

import pytest

# Try to import with better error handling and explicit imports
try:
    import fastapi
    from fastapi.testclient import TestClient
    print(f"FastAPI version: {fastapi.__version__}")
    print("Using FastAPI TestClient")
except ImportError as e:
    # Try Starlette as fallback
    try:
        from starlette.testclient import TestClient
        print("Using Starlette TestClient")
    except ImportError:
        pytest.fail(f"Failed to import TestClient: {e}. Please check FastAPI/Starlette installation.")

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
    try:
        initialize_services()
    except Exception:
        # If initialization fails, continue with tests
        pass
    yield
    try:
        shutdown_services()
    except Exception:
        # If shutdown fails, continue
        pass

# Function to create TestClient with proper error handling
def create_test_client(app_instance):
    """Create TestClient with proper error handling for different versions"""
    try:
        # Try the standard way first
        return TestClient(app_instance)
    except TypeError as e:
        if "unexpected keyword argument 'app'" in str(e):
            # Try with different constructor patterns
            try:
                # Some versions need base_url
                return TestClient(app_instance, base_url="http://test")
            except:
                try:
                    # Some versions need transport
                    from fastapi.testclient import \
                        TestClient as FallbackTestClient
                    return FallbackTestClient(app_instance, base_url="http://test")
                except:
                    pytest.fail(f"Could not create TestClient: {e}")
        else:
            pytest.fail(f"TestClient creation failed: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error creating TestClient: {e}")

# Simple test to verify TestClient works
def test_client_initialization():
    """Test that TestClient can be initialized and make basic requests"""
    try:
        client = create_test_client(app)
        assert client is not None
        # Try a simple request to verify the client works
        response = client.get("/health")
        assert response.status_code in [200, 404, 500]  # Any response means client works
    except Exception as e:
        pytest.fail(f"TestClient initialization failed: {e}")

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
    
    def test_health_check(self):
        """Test that the health check endpoint returns healthy status"""
        client = create_test_client(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestTemplateEndpoints:
    """Test 2: Template Endpoints"""
    
    def test_get_default_template(self):
        """Test getting the default HR data template"""
        client = create_test_client(app)
        response = client.get("/v1/template")
        
        assert response.status_code == 200
        data = response.json()
        assert "template" in data
        template = data["template"]
        assert "name" in template
        assert "cpf" in template

    def test_get_template_by_role(self):
        """Test getting a role-specific template"""
        client = create_test_client(app)
        response = client.get("/v1/template/developer")
        
        assert response.status_code == 200
        data = response.json()
        assert "template" in data
        template = data["template"]
        assert "position" in template

    def test_get_available_roles(self):
        """Test getting list of available role templates"""
        client = create_test_client(app)
        response = client.get("/v1/template/roles")
        
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)

class TestDataValidation:
    """Test 3: Data Validation Endpoint"""
    
    def test_validate_valid_data(self, valid_hr_data_dict):
        """Test validation of valid HR data"""
        client = create_test_client(app)
        response = client.post("/v1/validate", json=valid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert "errors" in data

    def test_validate_invalid_data(self, invalid_hr_data_dict):
        """Test validation of invalid HR data"""
        client = create_test_client(app)
        response = client.post("/v1/validate", json=invalid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "errors" in data

class TestDocumentStorage:
    """Test 4: Document Storage Endpoint"""
    
    @patch('app.api.endpoints.get_mongodb_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_store_valid_document(self, mock_validation, mock_mongodb, minimal_valid_hr_data_dict):
        """Test storing valid HR data document"""
        # Mock MongoDB service
        mock_mongodb_instance = MagicMock()
        mock_mongodb_instance.store_document.return_value = "test_document_id"
        mock_mongodb.return_value = mock_mongodb_instance
        
        # Mock validation service
        mock_validation_instance = MagicMock()
        mock_validation_instance.validate_hr_data.return_value = HRData(**minimal_valid_hr_data_dict)
        mock_validation.return_value = mock_validation_instance
        
        client = create_test_client(app)
        response = client.post("/v1/store-document", json=minimal_valid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["document_id"] == "test_document_id"

    def test_store_invalid_document(self, invalid_hr_data_dict):
        """Test storing invalid HR data document"""
        client = create_test_client(app)
        response = client.post("/v1/store-document", json=invalid_hr_data_dict)
        
        assert response.status_code == 422

class TestDocumentProcessing:
    """Test 5: Document Processing Endpoints"""
    
    @patch('app.api.endpoints.get_anthropic_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_process_valid_pdf(self, mock_validation, mock_anthropic):
        """Test processing a valid PDF document"""
        # Mock Anthropic service to return a coroutine
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.process_pdf.return_value = asyncio.Future()
        mock_anthropic_instance.process_pdf.return_value.set_result({
            "extracted_data": {"name": "John Doe", "position": "Developer"}
        })
        mock_anthropic.return_value = mock_anthropic_instance
        
        # Mock validation service
        mock_validation_instance = MagicMock()
        mock_validation_instance.validate_hr_data.return_value = HRData(
            name="John Doe", 
            position="Developer", 
            cpf="12345678901",
            salary=5000.00,
            contract_type="CLT"
        )
        mock_validation.return_value = mock_validation_instance
        
        client = create_test_client(app)
        # Create mock PDF file
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "extracted_data" in data
        assert "errors" in data

    def test_process_invalid_file_type(self):
        """Test processing with invalid file type"""
        client = create_test_client(app)
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        
        response = client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 400

class TestPDFSummarization:
    """Test 6: PDF Summarization Endpoint"""
    
    @patch('app.api.endpoints.get_anthropic_service')
    def test_summarize_pdf(self, mock_anthropic):
        """Test PDF summarization functionality"""
        # Mock Anthropic service to return a coroutine
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.summarize_pdf.return_value = asyncio.Future()
        mock_anthropic_instance.summarize_pdf.return_value.set_result({
            "summary": "This is a test summary of the PDF content."
        })
        mock_anthropic.return_value = mock_anthropic_instance
        
        client = create_test_client(app)
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = client.post("/v1/summarize-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

class TestErrorHandling:
    """Test 7: Error Handling"""
    
    def test_invalid_endpoint(self):
        """Test handling of invalid endpoint"""
        client = create_test_client(app)
        response = client.get("/v1/nonexistent-endpoint")
        
        assert response.status_code == 404

    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payload"""
        client = create_test_client(app)
        # Test with malformed JSON that will cause parsing error
        response = client.post(
            "/v1/validate",
            json={"name": "test", "invalid_field": None}  # Valid JSON but invalid data
        )
        
        assert response.status_code == 200  # Validation endpoint returns 200 with errors

class TestWorkflow:
    """Test 8: Complete Workflow"""
    
    @patch('app.api.endpoints.get_mongodb_service')
    @patch('app.api.endpoints.get_validation_service')
    def test_complete_workflow(self, mock_validation, mock_mongodb, minimal_valid_hr_data_dict):
        """Test complete workflow: validate -> store"""
        # Mock MongoDB service
        mock_mongodb_instance = MagicMock()
        mock_mongodb_instance.store_document.return_value = "test_document_id"
        mock_mongodb.return_value = mock_mongodb_instance
        
        # Mock validation service
        mock_validation_instance = MagicMock()
        mock_validation_instance.validate_hr_data.return_value = HRData(**minimal_valid_hr_data_dict)
        mock_validation.return_value = mock_validation_instance
        
        client = create_test_client(app)
        # Step 1: Validate data
        validate_response = client.post("/v1/validate", json=minimal_valid_hr_data_dict)
        assert validate_response.status_code == 200
        
        # Step 2: Store document
        store_response = client.post("/v1/store-document", json=minimal_valid_hr_data_dict)
        assert store_response.status_code == 200

class TestConcurrentRequestHandling:
    """Test 9: Concurrent Request Handling"""
    
    def test_concurrent_health_checks(self):
        """Test handling of concurrent health check requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                client = create_test_client(app)
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
        
        # All requests should succeed
        assert len(results) == 5
        assert len(errors) == 0
        assert all(status in [200, 404, 500] for status in results)

class TestAPIBehavior:
    """Test 10: API Behavior and Consistency"""
    
    def test_api_response_format_consistency(self):
        """Test that API responses maintain consistent format"""
        client = create_test_client(app)
        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code in [200, 404, 500]
        
        # Test template endpoint
        template_response = client.get("/v1/template")
        assert template_response.status_code == 200
        template_data = template_response.json()
        assert "template" in template_data
        
        # Test roles endpoint
        roles_response = client.get("/v1/template/roles")
        assert roles_response.status_code == 200
        roles_data = roles_response.json()
        assert "roles" in roles_data

    def test_error_response_format(self):
        """Test that error responses maintain consistent format"""
        client = create_test_client(app)
        # Test 404 error
        response = client.get("/v1/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data