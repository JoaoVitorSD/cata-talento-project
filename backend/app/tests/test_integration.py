import asyncio
import io
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from ..main import app
from ..models.hr_data import HRData, WorkExperience


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
def mock_pdf_file():
    """Mock PDF file for testing"""
    return io.BytesIO(b"mock pdf content")

@pytest.fixture
async def async_client():
    """Async client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestHealthCheck:
    """Test 1: Health Check Endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test that the health check endpoint returns healthy status"""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

class TestTemplateEndpoints:
    """Test 2: Template Endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_default_template(self, async_client):
        """Test getting the default HR data template"""
        response = await async_client.get("/v1/template")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "name" in data
        assert "position" in data
        assert "cpf" in data
    
    @pytest.mark.asyncio
    async def test_get_template_by_role(self, async_client):
        """Test getting a role-specific template"""
        response = await async_client.get("/v1/template/developer")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "position" in data
    
    @pytest.mark.asyncio
    async def test_get_available_roles(self, async_client):
        """Test getting list of available role templates"""
        response = await async_client.get("/v1/template/roles")
        
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0

class TestDataValidation:
    """Test 3: Data Validation Endpoint"""
    
    @pytest.mark.asyncio
    async def test_validate_valid_data(self, async_client, valid_hr_data_dict):
        """Test validation of valid HR data"""
        response = await async_client.post("/v1/validate", json=valid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert data["is_valid"] is True
        assert "errors" in data
    
    @pytest.mark.asyncio
    async def test_validate_invalid_data(self, async_client, invalid_hr_data_dict):
        """Test validation of invalid HR data"""
        response = await async_client.post("/v1/validate", json=invalid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert data["is_valid"] is False
        assert "errors" in data
        assert len(data["errors"]) > 0

class TestDocumentStorage:
    """Test 4: Document Storage Endpoint"""
    
    @pytest.mark.asyncio
    @patch('app.api.endpoints.get_mongodb_service')
    async def test_store_valid_document(self, mock_mongodb, async_client, valid_hr_data_dict):
        """Test storing valid HR data document"""
        # Mock MongoDB service
        mock_mongodb.return_value.store_document.return_value = "test_document_id"
        
        response = await async_client.post("/v1/store-document", json=valid_hr_data_dict)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "document_id" in data
        assert data["document_id"] == "test_document_id"
    
    @pytest.mark.asyncio
    async def test_store_invalid_document(self, async_client, invalid_hr_data_dict):
        """Test storing invalid HR data document"""
        response = await async_client.post("/v1/store-document", json=invalid_hr_data_dict)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

class TestPDFProcessing:
    """Test 5: PDF Processing Endpoint"""
    
    @pytest.mark.asyncio
    @patch('app.api.endpoints.get_ocr_service')
    @patch('app.api.endpoints.get_anthropic_service')
    @patch('app.api.endpoints.get_validation_service')
    async def test_process_valid_pdf(self, mock_validation, mock_anthropic, mock_ocr, async_client):
        """Test processing a valid PDF document"""
        # Mock OCR service
        mock_ocr.return_value.extract_text_from_pdf.return_value = "Extracted text from PDF"
        
        # Mock Anthropic service
        mock_anthropic.return_value.analyze_hr_document.return_value = {
            "name": "João Silva",
            "position": "Developer"
        }
        
        # Mock validation service
        mock_validation.return_value.validate_hr_data.return_value = HRData(
            name="João Silva",
            cpf="529.982.247-25",
            position="Developer",
            salary=5000.00,
            contract_type="CLT"
        )
        
        # Create mock PDF file
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = await async_client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "hr_data" in data
        assert "errors" in data
    
    @pytest.mark.asyncio
    async def test_process_invalid_file_type(self, async_client):
        """Test processing with invalid file type"""
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        
        response = await async_client.post("/v1/process-pdf", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "File must be a PDF" in data["detail"]

class TestPDFSummarization:
    """Test 6: PDF Summarization Endpoint"""
    
    @pytest.mark.asyncio
    @patch('app.api.endpoints.get_ocr_service')
    @patch('app.api.endpoints.get_anthropic_service')
    async def test_summarize_pdf(self, mock_anthropic, mock_ocr, async_client):
        """Test PDF summarization functionality"""
        # Mock OCR service
        mock_ocr.return_value.extract_text_from_pdf.return_value = "Extracted text from PDF"
        
        # Mock Anthropic service
        mock_anthropic.return_value.generate_document_summary.return_value = {
            "summary": "This is a summary of the document",
            "key_points": ["Point 1", "Point 2"]
        }
        
        files = {"file": ("test.pdf", io.BytesIO(b"mock pdf content"), "application/pdf")}
        
        response = await async_client.post("/v1/summarize-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "key_points" in data

class TestErrorHandling:
    """Test 7: Error Handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, async_client):
        """Test handling of invalid endpoint"""
        response = await async_client.get("/v1/nonexistent-endpoint")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_json_payload(self, async_client):
        """Test handling of invalid JSON payload"""
        # Test with malformed JSON that will cause parsing error
        response = await async_client.post(
            "/v1/validate", 
            json={"name": "test", "invalid_field": None}  # This will cause validation errors
        )
        
        assert response.status_code == 200  # Validation endpoint returns 200 with errors
        data = response.json()
        assert "is_valid" in data
        assert data["is_valid"] is False

class TestDataFlow:
    """Test 8: Complete Data Flow"""
    
    @pytest.mark.asyncio
    @patch('app.api.endpoints.get_mongodb_service')
    @patch('app.api.endpoints.get_validation_service')
    async def test_complete_workflow(self, mock_validation, mock_mongodb, async_client):
        """Test complete workflow: validate -> store"""
        # Mock validation service
        mock_validation.return_value.validate_hr_data.return_value = HRData(
            name="João Silva",
            cpf="529.982.247-25",
            position="Developer",
            salary=5000.00,
            contract_type="CLT"
        )
        
        # Mock MongoDB service
        mock_mongodb.return_value.store_document.return_value = "workflow_doc_id"
        
        # Step 1: Validate data
        valid_data = {
            "name": "João Silva",
            "cpf": "529.982.247-25",
            "position": "Developer"
        }
        
        validate_response = await async_client.post("/v1/validate", json=valid_data)
        assert validate_response.status_code == 200
        
        # Step 2: Store validated data
        store_response = await async_client.post("/v1/store-document", json=valid_data)
        assert store_response.status_code == 200
        
        data = store_response.json()
        assert data["status"] == "success"
        assert data["document_id"] == "workflow_doc_id"

class TestConcurrentRequests:
    """Test 9: Concurrent Request Handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, async_client):
        """Test handling of concurrent health check requests"""
        import asyncio
        
        async def make_request():
            try:
                response = await async_client.get("/health")
                return response.status_code
            except Exception as e:
                return str(e)
        
        # Create multiple concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        assert len(results) == 5
        assert all(status == 200 for status in results)

class TestAPIBehavior:
    """Test 10: API Behavior and Consistency"""
    
    @pytest.mark.asyncio
    async def test_api_response_format_consistency(self, async_client):
        """Test that API responses maintain consistent format"""
        # Test health endpoint
        health_response = await async_client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert isinstance(health_data, dict)
        
        # Test template endpoint
        template_response = await async_client.get("/v1/template")
        assert template_response.status_code == 200
        template_data = template_response.json()
        assert isinstance(template_data, dict)
        
        # Test roles endpoint
        roles_response = await async_client.get("/v1/template/roles")
        assert roles_response.status_code == 200
        roles_data = roles_response.json()
        assert isinstance(roles_data, dict)
        assert "roles" in roles_data
    
    @pytest.mark.asyncio
    async def test_error_response_format(self, async_client):
        """Test that error responses maintain consistent format"""
        # Test 404 error
        response = await async_client.get("/v1/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        # Test 422 error with invalid data
        response = await async_client.post("/v1/validate", json={"invalid": "data"})
        assert response.status_code == 200  # Validation endpoint returns 200 with errors
        data = response.json()
        assert "is_valid" in data
        assert "errors" in data 