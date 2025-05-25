from typing import Dict, Union, Any
from datetime import datetime
from pydantic import ValidationError
import logging

from ..models.hr_data import HRData


class ValidationService:
    def __init__(self):
        logging.info("Validation service initialized")

    def validate_hr_data(self, data: Dict) -> Dict[str, Any]:
        """
        Validate HR data against the model and return both data and validation errors.
        
        Args:
            data: Dictionary containing HR data to validate
            
        Returns:
            Dictionary containing:
            - 'data': HRData object (if validation partially succeeded)
            - 'errors': Dictionary of validation errors (if any)
        """
        result = {"data": None, "errors": {}}
        
        try:
            # Convert string dates to datetime objects for validation
            processed_data = self._process_date_fields(data.copy())
            
            # Create HRData instance even if there are validation errors
            result["data"] = HRData(**processed_data)
            
        except ValidationError as e:
            # Format validation errors but don't raise
            result["errors"] = self._format_validation_errors(e)
            
        except Exception as e:
            logging.error(f"Unexpected validation error: {str(e)}")
            result["errors"]["general"] = [str(e)]
            
        return result

    def _process_date_fields(self, data: Dict) -> Dict:
        """
        Process and convert date fields from strings to datetime objects.
        
        Args:
            data: Dictionary containing HR data
            
        Returns:
            Dictionary with processed date fields
        """
        # Convert main date fields
        if isinstance(data.get('date'), str):
            data['date'] = self._parse_datetime(data['date'])
        if isinstance(data.get('start_date'), str):
            data['start_date'] = self._parse_datetime(data['start_date'])
            
        # Handle work experience dates
        if 'work_experience' in data and isinstance(data['work_experience'], list):
            for exp in data['work_experience']:
                if isinstance(exp.get('start_date'), str):
                    exp['start_date'] = self._parse_datetime(exp['start_date'])
                if isinstance(exp.get('end_date'), str):
                    exp['end_date'] = self._parse_datetime(exp['end_date'])
        
        return data

    def _parse_datetime(self, date_string: str) -> datetime:
        """
        Parse datetime string, handling different formats.
        
        Args:
            date_string: String representation of datetime
            
        Returns:
            Parsed datetime object
        """
        try:
            # Handle ISO format with 'Z' timezone indicator
            if date_string.endswith('Z'):
                date_string = date_string.replace('Z', '+00:00')
            
            return datetime.fromisoformat(date_string)
        except ValueError as e:
            logging.error(f"Failed to parse datetime string '{date_string}': {str(e)}")
            raise ValueError(f"Invalid date format: {date_string}")

    def _format_validation_errors(self, validation_error: ValidationError) -> Dict[str, list]:
        """
        Format Pydantic validation errors into a more user-friendly structure.
        
        Args:
            validation_error: Pydantic ValidationError object
            
        Returns:
            Dictionary with field names as keys and error messages as values
        """
        errors = {}
        for error in validation_error.errors():
            field = error["loc"][0] if error["loc"] else "general"
            if field not in errors:
                errors[field] = []
            errors[field].append(error["msg"])
        return errors

    def validate_data_without_storing(self, data: Dict) -> Dict:
        """
        Validate HR data without storing it and return validation status.
        
        Args:
            data: Dictionary containing HR data to validate
            
        Returns:
            Dictionary with validation status, data and errors if any
        """
        result = self.validate_hr_data(data)
        
        return {
            "valid": len(result["errors"]) == 0,
            "data": result["data"],
            "errors": result["errors"]
        }

    def is_valid_cpf(self, cpf: str) -> bool:
        """
        Check if a CPF is valid without raising exceptions.
        
        Args:
            cpf: CPF string to validate
            
        Returns:
            Boolean indicating if CPF is valid
        """
        try:
            # Remove any non-digit characters for validation
            cpf_digits = ''.join(filter(str.isdigit, cpf))
            
            # Must have exactly 11 digits
            if len(cpf_digits) != 11:
                return False
            
            # Check if all digits are the same
            if len(set(cpf_digits)) == 1:
                return False
                
            # Validate first digit
            sum_products = sum(int(a) * b for a, b in zip(cpf_digits[0:9], range(10, 1, -1)))
            expected_digit = (sum_products * 10 % 11) % 10
            if int(cpf_digits[9]) != expected_digit:
                return False
                
            # Validate second digit
            sum_products = sum(int(a) * b for a, b in zip(cpf_digits[0:10], range(11, 1, -1)))
            expected_digit = (sum_products * 10 % 11) % 10
            if int(cpf_digits[10]) != expected_digit:
                return False
                
            return True
        except Exception:
            return False 