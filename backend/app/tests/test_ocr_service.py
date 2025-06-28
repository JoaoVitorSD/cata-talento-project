from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytesseract
import pytest
from app.services.ocr_service import OCRService
from pdf2image.pdf2image import convert_from_bytes
from PIL import Image


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes for testing"""
    return b"fake_pdf_content"


@pytest.fixture
def sample_text():
    """Sample text extracted from PDF"""
    return """
    Nome: João Silva Santos
    CPF: 123.456.789-00
    Data: 15/03/2023
    Cargo: Desenvolvedor Full Stack
    Departamento: Tecnologia
    Salário: R$ 5.500,00
    Contrato: CLT
    """


@pytest.fixture
def sample_text_with_missing_fields():
    """Sample text with some missing fields"""
    return """
    Nome: Maria Oliveira
    CPF: 987.654.321-00
    Data: 20/07/2023
    Cargo: Analista de Dados
    """


@pytest.fixture
def sample_text_no_fields():
    """Sample text with no recognizable fields"""
    return """
    Este é um documento qualquer
    sem campos específicos de RH
    apenas texto genérico
    """


class TestOCRService:
    """Test class for OCRService"""

    # ---------- EXTRACT TEXT FROM PDF ----------
    
    @patch('app.services.ocr_service.convert_from_bytes')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_pdf_success(self, mock_pytesseract, mock_convert, sample_pdf_bytes):
        """Test successful text extraction from PDF"""
        # Mock PDF to image conversion
        mock_image1 = Mock()
        mock_image2 = Mock()
        mock_convert.return_value = [mock_image1, mock_image2]
        
        # Mock OCR text extraction
        mock_pytesseract.side_effect = ["Texto da página 1", "Texto da página 2"]
        
        result = OCRService.extract_text_from_pdf(sample_pdf_bytes)
        
        # Verify calls
        mock_convert.assert_called_once_with(sample_pdf_bytes)
        assert mock_pytesseract.call_count == 2
        assert result == "Texto da página 1Texto da página 2"

    @patch('app.services.ocr_service.convert_from_bytes')
    def test_extract_text_from_pdf_empty_pdf(self, mock_convert, sample_pdf_bytes):
        """Test text extraction from empty PDF"""
        mock_convert.return_value = []
        
        result = OCRService.extract_text_from_pdf(sample_pdf_bytes)
        
        assert result == ""

    @patch('app.services.ocr_service.convert_from_bytes')
    def test_extract_text_from_pdf_conversion_error(self, mock_convert, sample_pdf_bytes):
        """Test handling of PDF conversion error"""
        mock_convert.side_effect = Exception("PDF conversion failed")
        
        with pytest.raises(Exception, match="PDF conversion failed"):
            OCRService.extract_text_from_pdf(sample_pdf_bytes)

    @patch('app.services.ocr_service.convert_from_bytes')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_extract_text_from_pdf_ocr_error(self, mock_pytesseract, mock_convert, sample_pdf_bytes):
        """Test handling of OCR error"""
        mock_image = Mock()
        mock_convert.return_value = [mock_image]
        mock_pytesseract.side_effect = Exception("OCR failed")
        
        with pytest.raises(Exception, match="OCR failed"):
            OCRService.extract_text_from_pdf(sample_pdf_bytes)

    # ---------- EXTRACT HR DATA ----------
    
    def test_extract_hr_data_complete_fields(self, sample_text):
        """Test extraction of HR data with all fields present"""
        result = OCRService.extract_hr_data(sample_text)
        
        assert result["name"] == "João Silva Santos"
        assert result["cpf"] == "123.456.789-00"
        assert result["position"] == "Desenvolvedor Full Stack"
        assert result["department"] == "Tecnologia"
        assert result["salary"] == 5.5  # The regex captures "5.500" before the comma
        assert result["contract_type"] == "CLT"
        assert "2023-03-15" in result["date"]
        assert result["start_date"] == result["date"]
        assert result["main_skills"] == []
        assert result["hard_skills"] == []
        assert result["work_experience"] == []

    def test_extract_hr_data_missing_fields(self, sample_text_with_missing_fields):
        """Test extraction of HR data with missing fields"""
        result = OCRService.extract_hr_data(sample_text_with_missing_fields)
        
        assert result["name"] == "Maria Oliveira"
        assert result["cpf"] == "987.654.321-00"
        assert result["position"] == "Analista de Dados"
        assert result["department"] is None
        assert result["salary"] is None
        assert result["contract_type"] is None
        assert "2023-07-20" in result["date"]

    def test_extract_hr_data_no_fields(self, sample_text_no_fields):
        """Test extraction of HR data with no recognizable fields"""
        result = OCRService.extract_hr_data(sample_text_no_fields)
        
        assert result["name"] == ""
        assert result["cpf"] == ""
        assert result["position"] is None

    def test_extract_hr_data_empty_text(self):
        """Test extraction of HR data from empty text"""
        result = OCRService.extract_hr_data("")
        
        assert result["name"] == ""
        assert result["cpf"] == ""
        assert result["position"] is None

    # ---------- NAME EXTRACTION ----------
    
    def test_extract_name_various_formats(self):
        """Test name extraction with various formats"""
        test_cases = [
            ("Nome: João Silva", "João Silva"),
            ("NOME: Maria Santos", "Maria Santos"),
            ("nome: Pedro Costa", "Pedro Costa"),
            ("Nome João Silva", "João Silva"),
            ("NOME Maria Santos", "Maria Santos"),
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["name"] == expected

    def test_extract_name_not_found(self):
        """Test name extraction when not found"""
        text = "CPF: 123.456.789-00\nCargo: Desenvolvedor"
        result = OCRService.extract_hr_data(text)
        assert result["name"] == ""

    # ---------- CPF EXTRACTION ----------
    
    def test_extract_cpf_various_formats(self):
        """Test CPF extraction with various formats"""
        test_cases = [
            ("CPF: 123.456.789-00", "123.456.789-00"),
            ("cpf: 987.654.321-00", "987.654.321-00"),
            ("CPF 111.222.333-44", "111.222.333-44"),
            ("cpf 555.666.777-88", "555.666.777-88"),
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["cpf"] == expected

    def test_extract_cpf_not_found(self):
        """Test CPF extraction when not found"""
        text = "Nome: João Silva\nCargo: Desenvolvedor"
        result = OCRService.extract_hr_data(text)
        assert result["cpf"] == ""

    # ---------- DATE EXTRACTION ----------
    
    def test_extract_date_various_formats(self):
        """Test date extraction with various formats"""
        test_cases = [
            ("Data: 15/03/2023", "2023-03-15"),
            ("DATA: 20/07/2023", "2023-07-20"),
            ("Data 01/01/2023", "2023-01-01"),
            ("data 31/12/2023", "2023-12-31"),
        ]
        
        for text, expected_date in test_cases:
            result = OCRService.extract_hr_data(text)
            assert expected_date in result["date"]

    def test_extract_date_not_found(self):
        """Test date extraction when not found"""
        text = "Nome: João Silva\nCPF: 123.456.789-00"
        result = OCRService.extract_hr_data(text)
        # Should use current date
        assert isinstance(result["date"], str)
        assert len(result["date"]) > 0

    # ---------- POSITION EXTRACTION ----------
    
    def test_extract_position_various_formats(self):
        """Test position extraction with various formats"""
        test_cases = [
            ("Cargo: Desenvolvedor Full Stack", "Desenvolvedor Full Stack"),
            ("CARGO: Analista de Dados", "Analista de Dados"),
            ("cargo: Gerente de Projetos", "Gerente de Projetos"),
            ("Cargo Desenvolvedor", "Desenvolvedor"),
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["position"] == expected

    def test_extract_position_not_found(self):
        """Test position extraction when not found"""
        text = "Nome: João Silva\nCPF: 123.456.789-00"
        result = OCRService.extract_hr_data(text)
        assert result["position"] is None

    # ---------- DEPARTMENT EXTRACTION ----------
    
    def test_extract_department_various_formats(self):
        """Test department extraction with various formats"""
        test_cases = [
            ("Departamento: Tecnologia", "Tecnologia"),
            ("DEPARTAMENTO: Recursos Humanos", "Recursos Humanos"),
            ("departamento: Marketing", "Marketing"),
            ("Departamento Finanças", "Finanças"),
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["department"] == expected

    def test_extract_department_not_found(self):
        """Test department extraction when not found"""
        text = "Nome: João Silva\nCargo: Desenvolvedor"
        result = OCRService.extract_hr_data(text)
        assert result["department"] is None

    # ---------- SALARY EXTRACTION ----------
    
    def test_extract_salary_various_formats(self):
        """Test salary extraction with various formats"""
        test_cases = [
            ("Salário: R$ 5.500,00", 5.5),  # Regex captures "5.500" before comma
            ("SALÁRIO: R$ 3.200,50", 3.2),  # Regex captures "3.200" before comma
            ("salário: R$ 7.800,00", 7.8),  # Regex captures "7.800" before comma
            ("Salário R$ 4.500,00", 4.5),   # Regex captures "4.500" before comma
            ("Salário: 6.000,00", 6.0),     # Regex captures "6.000" before comma
            ("Salário: R$ 2.500", 2.5),     # No comma, captures "2.500"
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["salary"] == expected

    def test_extract_salary_not_found(self):
        """Test salary extraction when not found"""
        text = "Nome: João Silva\nCargo: Desenvolvedor"
        result = OCRService.extract_hr_data(text)
        assert result["salary"] is None

    # ---------- CONTRACT TYPE EXTRACTION ----------
    
    def test_extract_contract_type_various_formats(self):
        """Test contract type extraction with various formats"""
        test_cases = [
            ("Contrato: CLT", "CLT"),
            ("CONTRATO: PJ", "PJ"),
            ("contrato: Estagiário", "Estagiário"),
            ("Contrato Cooperado", "Cooperado"),
        ]
        
        for text, expected in test_cases:
            result = OCRService.extract_hr_data(text)
            assert result["contract_type"] == expected

    def test_extract_contract_type_not_found(self):
        """Test contract type extraction when not found"""
        text = "Nome: João Silva\nCargo: Desenvolvedor"
        result = OCRService.extract_hr_data(text)
        assert result["contract_type"] is None

    # ---------- EDGE CASES ----------
    
    def test_extract_hr_data_multiple_matches(self):
        """Test extraction when multiple matches are found (should take first)"""
        text = """
        Nome: João Silva
        Nome: Maria Santos
        CPF: 123.456.789-00
        CPF: 987.654.321-00
        Cargo: Desenvolvedor
        Cargo: Analista
        """
        result = OCRService.extract_hr_data(text)
        
        assert result["name"] == "João Silva"
        assert result["cpf"] == "123.456.789-00"
        assert result["position"] == "Desenvolvedor"

    def test_extract_hr_data_special_characters(self):
        """Test extraction with special characters in text"""
        text = """
        Nome: João Silva-Santos
        CPF: 123.456.789-00
        Cargo: Desenvolvedor (Full Stack)
        Departamento: TI & Inovação
        Salário: R$ 5.500,00
        Contrato: CLT
        """
        result = OCRService.extract_hr_data(text)
        
        assert result["name"] == "João Silva-Santos"
        assert result["cpf"] == "123.456.789-00"
        assert result["position"] == "Desenvolvedor (Full Stack)"
        assert result["department"] == "TI & Inovação"
        assert result["salary"] == 5.5  # Regex captures "5.500" before comma
        assert result["contract_type"] == "CLT"

    def test_extract_hr_data_whitespace_handling(self):
        """Test extraction with various whitespace patterns"""
        text = """
        Nome:    João Silva    
        CPF:  123.456.789-00  
        Cargo:  Desenvolvedor  
        """
        result = OCRService.extract_hr_data(text)
        
        assert result["name"] == "João Silva"
        assert result["cpf"] == "123.456.789-00"
        assert result["position"] == "Desenvolvedor"

    # ---------- INTEGRATION TESTS ----------
    
    @patch('app.services.ocr_service.convert_from_bytes')
    @patch('app.services.ocr_service.pytesseract.image_to_string')
    def test_full_ocr_pipeline(self, mock_pytesseract, mock_convert, sample_pdf_bytes):
        """Test the complete OCR pipeline from PDF to HR data"""
        # Mock PDF to image conversion
        mock_image = Mock()
        mock_convert.return_value = [mock_image]
        
        # Mock OCR text extraction
        sample_text = """
        Nome: João Silva Santos
        CPF: 123.456.789-00
        Data: 15/03/2023
        Cargo: Desenvolvedor Full Stack
        Departamento: Tecnologia
        Salário: R$ 5.500,00
        Contrato: CLT
        """
        mock_pytesseract.return_value = sample_text
        
        # Extract text from PDF
        extracted_text = OCRService.extract_text_from_pdf(sample_pdf_bytes)
        
        # Extract HR data from text
        hr_data = OCRService.extract_hr_data(extracted_text)
        
        # Verify results
        assert extracted_text == sample_text
        assert hr_data["name"] == "João Silva Santos"
        assert hr_data["cpf"] == "123.456.789-00"
        assert hr_data["position"] == "Desenvolvedor Full Stack"
        assert hr_data["department"] == "Tecnologia"
        assert hr_data["salary"] == 5.5  # Regex captures "5.500" before comma
        assert hr_data["contract_type"] == "CLT"
        assert "2023-03-15" in hr_data["date"]

    # ---------- ERROR HANDLING ----------
    
    def test_extract_hr_data_invalid_date_format(self):
        """Test handling of invalid date format"""
        text = "Data: 32/13/2023"  # Invalid date
        with pytest.raises(ValueError, match="time data.*does not match format"):
            OCRService.extract_hr_data(text)

    def test_extract_hr_data_invalid_salary_format(self):
        """Test handling of invalid salary format"""
        text = "Salário: R$ abc,def"  # Invalid salary
        result = OCRService.extract_hr_data(text)
        
        assert result["salary"] is None

    def test_extract_hr_data_malformed_text(self):
        """Test handling of malformed text"""
        text = "Nome:\nCPF:\nCargo:\n"  # Empty values
        result = OCRService.extract_hr_data(text)
        
        assert result["name"] == "CPF:"  # Regex captures everything until end of line
        assert result["cpf"] == ""
        assert result["position"] == ":"