import json
import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from app.services.anthropic_service import AnthropicService


class TestAnthropicService:
    """Test suite for AnthropicService class"""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client to avoid real API calls"""
        with patch('app.services.anthropic_service.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def anthropic_service(self, mock_anthropic_client):
        """Create AnthropicService instance with mocked client"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'}):
            return AnthropicService()

    def test_initialization_success(self, mock_anthropic_client):
        """Test successful service initialization"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_api_key'}):
            service = AnthropicService()
            assert service.client == mock_anthropic_client

    def test_initialization_missing_api_key(self):
        """Test initialization fails when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY environment variable is required"):
                AnthropicService()

    def test_build_extraction_prompt(self, anthropic_service):
        """Test prompt building functionality"""
        test_text = "John Doe is a software engineer with 5 years of experience"
        prompt = anthropic_service._build_extraction_prompt(test_text)
        
        # Check that the prompt contains the expected structure
        assert "Extract the following fields" in prompt
        assert "name" in prompt
        assert "cpf" in prompt
        assert "position" in prompt
        assert "salary" in prompt
        assert "contract_type" in prompt
        assert "main_skills" in prompt
        assert "hard_skills" in prompt
        assert "work_experience" in prompt
        assert test_text in prompt

    @pytest.mark.asyncio
    async def test_analyze_hr_document_success(self, anthropic_service, mock_anthropic_client):
        """Test successful HR document analysis"""
        # Mock response structure
        mock_content = Mock()
        mock_content.text = json.dumps({
            "name": "John Doe",
            "position": "Software Engineer",
            "salary": 75000,
            "contract_type": "CLT",
            "main_skills": ["Leadership", "Communication"],
            "hard_skills": ["Python", "React"],
            "work_experience": []
        })
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        # Test with minimal text
        test_text = "John Doe, Software Engineer, 5 years experience"
        result = await anthropic_service.analyze_hr_document(test_text)
        
        # Verify the result
        assert isinstance(result, dict)
        assert result["name"] == "John Doe"
        assert result["position"] == "Software Engineer"
        
        # Verify API call was made with correct parameters
        mock_anthropic_client.messages.create.assert_called_once()
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args[1]["model"] == "claude-3-haiku-20240307"
        assert call_args[1]["max_tokens"] == 3000
        assert call_args[1]["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_analyze_hr_document_invalid_json(self, anthropic_service, mock_anthropic_client):
        """Test handling of invalid JSON response"""
        # Mock response with invalid JSON
        mock_content = Mock()
        mock_content.text = "This is not valid JSON"
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        test_text = "John Doe, Software Engineer"
        result = await anthropic_service.analyze_hr_document(test_text)
        
        # Should return empty dict on JSON parse error
        assert result == {}

    @pytest.mark.asyncio
    async def test_analyze_hr_document_api_error(self, anthropic_service, mock_anthropic_client):
        """Test handling of API errors"""
        # Mock API exception
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        test_text = "John Doe, Software Engineer"
        result = await anthropic_service.analyze_hr_document(test_text)
        
        # Should return empty dict on API error
        assert result == {}

    @pytest.mark.asyncio
    async def test_analyze_hr_document_empty_response(self, anthropic_service, mock_anthropic_client):
        """Test handling of empty API response"""
        # Mock empty response
        mock_response = Mock()
        mock_response.content = []
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        test_text = "John Doe, Software Engineer"
        result = await anthropic_service.analyze_hr_document(test_text)
        
        # Should return empty dict
        assert result == {}

    @pytest.mark.asyncio
    async def test_generate_document_summary_success(self, anthropic_service, mock_anthropic_client):
        """Test successful document summarization"""
        # Mock response structure
        mock_content = Mock()
        mock_content.text = json.dumps({
            "summary": "John Doe is an experienced software engineer with strong technical skills."
        })
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        # Test with minimal text
        test_text = "John Doe, Software Engineer, 5 years experience"
        result = await anthropic_service.generate_document_summary(test_text)
        
        # Verify the result
        assert isinstance(result, dict)
        assert "summary" in result
        assert "John Doe is an experienced software engineer" in result["summary"]
        
        # Verify API call was made with correct parameters
        mock_anthropic_client.messages.create.assert_called_once()
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args[1]["model"] == "claude-3-haiku-20240307"
        assert call_args[1]["max_tokens"] == 1000
        assert call_args[1]["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_generate_document_summary_invalid_json(self, anthropic_service, mock_anthropic_client):
        """Test handling of invalid JSON in summary response"""
        # Mock response with invalid JSON
        mock_content = Mock()
        mock_content.text = "This is a plain text summary, not JSON"
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        test_text = "John Doe, Software Engineer"
        result = await anthropic_service.generate_document_summary(test_text)
        
        # Should return raw content as summary when JSON parsing fails
        assert result["summary"] == "This is a plain text summary, not JSON"

    @pytest.mark.asyncio
    async def test_generate_document_summary_api_error(self, anthropic_service, mock_anthropic_client):
        """Test handling of API errors in summarization"""
        # Mock API exception
        mock_anthropic_client.messages.create.side_effect = Exception("API Error")
        
        test_text = "John Doe, Software Engineer"
        result = await anthropic_service.generate_document_summary(test_text)
        
        # Should return error message
        assert result["summary"] == "Error generating summary"

    def test_extraction_prompt_structure(self, anthropic_service):
        """Test that extraction prompt includes all required fields"""
        test_text = "Test document"
        prompt = anthropic_service._build_extraction_prompt(test_text)
        
        # Check for all required fields in the prompt
        required_fields = [
            "name", "cpf", "position", "salary", "contract_type",
            "main_skills", "hard_skills", "work_experience"
        ]
        
        for field in required_fields:
            assert field in prompt
        
        # Check for work experience structure
        work_exp_fields = [
            "company", "position", "start_date", "end_date",
            "current_job", "description", "achievements", "technologies_used"
        ]
        
        for field in work_exp_fields:
            assert field in prompt
        
        # Check that it asks for JSON only
        assert "Return ONLY a valid JSON object" in prompt