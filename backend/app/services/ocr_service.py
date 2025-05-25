import pytesseract
from pdf2image.pdf2image import convert_from_bytes
import re
from datetime import datetime
from typing import Dict, Any
from ..models.hr_data import HRData

class OCRService:
    @staticmethod
    def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
        # Convert PDF to images
        images = convert_from_bytes(pdf_file_bytes)
        
        # Extract text from each page
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang='por')
        
        return text

    @staticmethod
    def extract_hr_data(text: str) -> Dict[str, Any]:
        """
        Extract HR data from text and return as a dictionary.
        
        Args:
            text: Text to extract data from
            
        Returns:
            Dictionary containing extracted HR data
        """
        # Extract name (assuming it follows 'Nome:' or similar pattern)
        name_match = re.search(r'Nome:?\s*([^\n]+)', text, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else ""

        # Extract CPF (format: XXX.XXX.XXX-XX)
        cpf_match = re.search(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
        cpf = cpf_match.group(0) if cpf_match else ""

        # Extract date (assuming format DD/MM/YYYY)
        date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        date = datetime.strptime(date_match.group(0), '%d/%m/%Y') if date_match else datetime.now()

        # Extract position
        position_match = re.search(r'Cargo:?\s*([^\n]+)', text, re.IGNORECASE)
        position = position_match.group(1).strip() if position_match else None

        # Extract department
        department_match = re.search(r'Departamento:?\s*([^\n]+)', text, re.IGNORECASE)
        department = department_match.group(1).strip() if department_match else None

        # Extract salary
        salary_match = re.search(r'Salário:?\s*R?\$?\s*(\d+[.,]\d+)', text, re.IGNORECASE)
        salary = float(salary_match.group(1).replace(',', '.')) if salary_match else None

        # Extract contract type
        contract_match = re.search(r'Contrato:?\s*([^\n]+)', text, re.IGNORECASE)
        contract_type = contract_match.group(1).strip() if contract_match else None

        # Return dictionary instead of HRData object
        return {
            "name": name,
            "cpf": cpf,
            "date": date.isoformat(),
            "position": position,
            "department": department,
            "salary": salary,
            "contract_type": contract_type,
            "start_date": date.isoformat(),
            "main_skills": [],
            "hard_skills": [],
            "work_experience": []
        } 