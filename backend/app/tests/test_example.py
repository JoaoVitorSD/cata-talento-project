from app.services.validation_service import ValidationService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_valid_cpf():
    valid =  ValidationService()
    assert valid.is_valid_cpf("11822113725") == True

def test_unvalid_cpf():
    valid = ValidationService()
    assert valid.is_valid_cpf("11822113720") == False