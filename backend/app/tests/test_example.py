from dotenv import load_dotenv

from ..core.dependencies import ServiceContainer

# Load environment variables from .env file
load_dotenv()

def test_valid_cpf(service_container):
    valid = service_container.get_validation_service()
    assert valid.is_valid_cpf("11822113725") == True

def test_unvalid_cpf(service_container):
    valid = service_container.get_validation_service()
    assert valid.is_valid_cpf("11822113720") == False

print(test_valid_cpf())