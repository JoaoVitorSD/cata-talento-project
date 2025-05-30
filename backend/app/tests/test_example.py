from ..core.dependencies import ServiceContainer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_valid_cpf():
    services = ServiceContainer()
    services.initialize_services()
    valid = services.get_validation_service()
    return valid.is_valid_cpf("11822113725")

def test_unvalid_cpf():
    services = ServiceContainer()
    services.initialize_services()
    valid = services.get_validation_service()
    assert valid.is_valid_cpf("11822113720") == False

print(test_valid_cpf())