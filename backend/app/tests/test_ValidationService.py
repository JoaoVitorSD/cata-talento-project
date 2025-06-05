import pytest
from datetime import datetime
from pydantic import ValidationError, BaseModel, Field

from app.services.validation_service import ValidationService
from app.models.hr_data import HRData
from app.core.dependencies import ServiceContainer

from dotenv import load_dotenv
load_dotenv()


@pytest.fixture
def service():
    return ValidationService()


# ---------- CPF VALIDATION ----------
@pytest.mark.parametrize("cpf", [
    '52998224725',  # válido
])
def test_valid_cpf(service, cpf):
    assert service.is_valid_cpf(cpf) is True


@pytest.mark.parametrize("cpf", [
    '11111111111',
    '12345678900',
    '00000000000',
    '5299822472'  # curto
])
def test_invalid_cpf(service, cpf):
    assert service.is_valid_cpf(cpf) is False


# ---------- DATE PARSING ----------
@pytest.mark.parametrize("date_str, expected", [
    ("2023-05-01", datetime(2023, 5, 1)),
    ("2023", datetime(2023, 1, 1)),
    ("2023-05-01T00:00:00Z", datetime.fromisoformat('2023-05-01T00:00:00+00:00'))
])
def test_parse_valid_dates(service, date_str, expected):
    assert service._parse_datetime(date_str) == expected


@pytest.mark.parametrize("date_str", [
    "invalid-date",
    "32/13/2023",
    "abc",
])
def test_parse_invalid_date(service, date_str):
    with pytest.raises(ValueError):
        service._parse_datetime(date_str)




def test_validate_data_with_missing_fields(service):
    data = {
        "name": "John Doe"
        # cpf ausente
    }
    result = service.validate_data_without_storing(data)
    assert result['valid'] is False
    assert 'cpf' in result['errors']


# ---------- FORMATTING ERRORS ----------
def test_format_validation_errors(service):
    class DummyModel(BaseModel):
        name: str = Field(...)

    with pytest.raises(ValidationError) as e:
        DummyModel()

    errors = service._format_validation_errors(e.value)
    assert 'name' in errors
    assert isinstance(errors['name'], list)
