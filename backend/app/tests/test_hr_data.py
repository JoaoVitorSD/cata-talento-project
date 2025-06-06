from datetime import datetime

import pytest

from ..models.hr_data import HRData, WorkExperience


@pytest.fixture
def valid_work_experience():
    return WorkExperience(
        company="Tech Corp",
        position="Senior Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Desenvolvimento de aplicações web com foco em escalabilidade",
        achievements=["Liderou equipe de 5 desenvolvedores"],
        technologies_used=["React", "Node.js"]
    )

@pytest.fixture
def valid_hr_data():
    return HRData(
        name="John Doe",
        cpf="529.982.247-25",
        position="Software Engineer",
        salary=5000.00,
        contract_type="CLT",
        main_skills=["Leadership", "Communication"],
        hard_skills=["Python", "React"],
        work_experience=[]
    )

def test_work_experience_current_job_validation():
    # Test current job validation - should not allow end_date when current_job is True
    with pytest.raises(ValueError, match="Não é possível definir data de término para emprego atual"):
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2023, 12, 31),  # This should trigger the error
            current_job=True,  # Because this is True
            description="Desenvolvimento de aplicações web com foco em escalabilidade e performance",
            achievements=[],
            technologies_used=[]
        )

    # Test current job validation - should allow None end_date when current_job is True
    exp = WorkExperience(
        company="Tech Corp",
        position="Developer",
        start_date=datetime(2022, 1, 1),
        end_date=None,  # This is allowed
        current_job=True,
        description="Desenvolvimento de aplicações web com foco em escalabilidade e performance",
        achievements=[],
        technologies_used=[]
    )
    assert exp.current_job is True
    assert exp.end_date is None

def test_work_experience_date_validation():
    # Test future start date validation
    future_date = datetime.now().replace(year=datetime.now().year + 1)
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=future_date,
            end_date=None,
            current_job=False,
            description="Desenvolvimento de aplicações web",
            achievements=[],
            technologies_used=[]
        )
    assert "A data de início não pode ser no futuro" in str(exc_info.value)

    # Test end date before start date validation
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2022, 12, 31),
            current_job=False,
            description="Desenvolvimento de aplicações web",
            achievements=[],
            technologies_used=[]
        )
    assert "A data de término não pode ser anterior à data de início" in str(exc_info.value)

    # Test future end date validation
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2022, 1, 1),
            end_date=datetime.now().replace(year=datetime.now().year + 1),
            current_job=False,
            description="Desenvolvimento de aplicações web",
            achievements=[],
            technologies_used=[]
        )
    assert "A data de término não pode ser no futuro" in str(exc_info.value)

def test_work_experience_achievements_validation():
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2023, 12, 31),
            current_job=False,
            description="Desenvolvimento de aplicações web",
            achievements=["long"],  # Too short achievement
            technologies_used=[]
        )
    assert "Cada conquista deve ter pelo menos 5 caracteres" in str(exc_info.value)

def test_work_experience_technologies_validation():
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2023, 12, 31),
            current_job=False,
            description="Desenvolvimento de aplicações web",
            achievements=[],
            technologies_used=["A"]  # Too short technology
        )
    assert "Cada tecnologia deve ter pelo menos 2 caracteres" in str(exc_info.value)

def test_work_experience_description_validation():
    with pytest.raises(ValueError) as exc_info:
        WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2023, 12, 31),
            current_job=False,
            description="Short",  # Too short description
            achievements=[],
            technologies_used=[]
        )
    assert "String should have at least 10 characters" in str(exc_info.value)

def test_hr_data_name_validation():
    with pytest.raises(ValueError) as exc_info:
        HRData(
            name="Jo",  # Too short name
            cpf="529.982.247-25",
            position="Software Engineer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=[],
            hard_skills=[],
            work_experience=[]
        )
    assert "String should have at least 3 characters" in str(exc_info.value)

def test_hr_data_position_validation():
    with pytest.raises(ValueError) as exc_info:
        HRData(
            name="John Doe",
            cpf="529.982.247-25",
            position="A",  # Too short position
            salary=5000.00,
            contract_type="CLT",
            main_skills=[],
            hard_skills=[],
            work_experience=[]
        )
    assert "String should have at least 2 characters" in str(exc_info.value)

def test_hr_data_salary_validation():
    with pytest.raises(ValueError) as exc_info:
        HRData(
            name="John Doe",
            cpf="529.982.247-25",
            position="Software Engineer",
            salary=-1000.00,  # Negative salary
            contract_type="CLT",
            main_skills=[],
            hard_skills=[],
            work_experience=[]
        )
    assert "Input should be greater than 0" in str(exc_info)

def test_hr_data_main_skills_validation():
    with pytest.raises(ValueError) as exc_info:
        HRData(
            name="John Doe",
            cpf="529.982.247-25",
            position="Software Engineer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=["A"],  # Too short skill
            hard_skills=[],
            work_experience=[]
        )
    assert "Cada habilidade principal deve ter pelo menos 2 caracteres" in str(exc_info.value)

def test_hr_data_hard_skills_validation():
    with pytest.raises(ValueError) as exc_info:
        HRData(
            name="John Doe",
            cpf="529.982.247-25",
            position="Software Engineer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=[],
            hard_skills=["A"],  # Too short skill
            work_experience=[]
        )
    assert "Cada habilidade técnica deve ter pelo menos 2 caracteres" in str(exc_info.value)

def test_work_experience_validation():
    # Test valid work experience
    exp = WorkExperience(
        company="Tech Corp",
        position="Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Desenvolvimento de aplicações web com foco em escalabilidade",
        achievements=["Liderou equipe de 5 desenvolvedores"],
        technologies_used=["React", "Node.js"]
    )
    assert exp.company == "Tech Corp"
    assert exp.position == "Developer"
    assert exp.current_job is False
    assert exp.description == "Desenvolvimento de aplicações web com foco em escalabilidade"
    assert len(exp.achievements) == 1
    assert len(exp.technologies_used) == 2

def test_hr_data_validation():
    # Test valid HR data
    hr_data = HRData(
        name="John Doe",
        cpf="529.982.247-25",
        position="Software Engineer",
        salary=5000.00,
        contract_type="CLT",
        main_skills=["Leadership", "Communication"],
        hard_skills=["Python", "React"],
        work_experience=[]
    )
    assert hr_data.name == "John Doe"
    assert hr_data.cpf == "529.982.247-25"
    assert hr_data.position == "Software Engineer"
    assert hr_data.salary == 5000.00
    assert hr_data.contract_type == "CLT"
    assert hr_data.main_skills is not None and len(hr_data.main_skills) == 2
    assert hr_data.hard_skills is not None and len(hr_data.hard_skills) == 2
    assert len(hr_data.work_experience) == 0

def test_cpf_validation():
    # Test valid CPF cases
    valid_cpfs = [
        "529.982.247-25",
        "52998224725",  # Without formatting
        "529.982.247-25",  # With formatting
    ]
    
    for cpf in valid_cpfs:
        hr_data = HRData(
            name="John Doe",
            cpf=cpf,
            position="Software Engineer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=[],
            hard_skills=[],
            work_experience=[]
        )
        # CPF should be formatted to standard format
        assert hr_data.cpf == "529.982.247-25"

    # Test invalid CPF cases
    invalid_cpfs = [
        "123.456.789-00",  # All same digits
        "111.111.111-11",  # All ones
        "123.456.789-00",  # Wrong check digits
        "529.982.247-2",   # Incomplete
        "529.982.247-256", # Too long
    ]
    
    for cpf in invalid_cpfs:
        with pytest.raises(ValueError) as exc_info:
            HRData(
                name="John Doe",
                cpf=cpf,
                position="Software Engineer",
                salary=5000.00,
                contract_type="CLT",
                main_skills=[],
                hard_skills=[],
                work_experience=[]
            )
        assert "CPF inválido" in str(exc_info.value)

def test_work_experience_in_hr_data(valid_hr_data, valid_work_experience):
    # Test adding valid work experience to HR data
    valid_hr_data.work_experience.append(valid_work_experience)
    assert len(valid_hr_data.work_experience) == 1
    assert valid_hr_data.work_experience[0] == valid_work_experience

    # Test adding invalid work experience (future start date)
    future_date = datetime.now().replace(year=datetime.now().year + 1)
    with pytest.raises(ValueError) as exc_info:
        invalid_exp = WorkExperience(
            company="Tech Corp",
            position="Developer",
            start_date=future_date,
            end_date=None,
            current_job=True,
            description="Desenvolvimento de aplicações web com foco em escalabilidade e performance",
            achievements=[],
            technologies_used=[]
        )
    assert "A data de início não pode ser no futuro" in str(exc_info.value)

def test_optional_fields():
    # Test HR data with optional fields
    hr_data = HRData(
        name="John Doe",
        cpf="529.982.247-25",
        position=None,  # Optional
        salary=None,    # Optional
        contract_type=None,  # Optional
        main_skills=None,    # Optional
        hard_skills=None,    # Optional
        work_experience=[]   # Optional but defaults to empty list
    )
    assert hr_data.position is None
    assert hr_data.salary is None
    assert hr_data.contract_type is None
    assert hr_data.main_skills is None
    assert hr_data.hard_skills is None
    assert hr_data.work_experience == []

    # Test work experience with optional fields
    exp = WorkExperience(
        company="Tech Corp",
        position="Developer",
        start_date=datetime(2022, 1, 1),
        end_date=None,  # Optional
        current_job=False,
        description="Desenvolvimento de aplicações web com foco em escalabilidade",
        achievements=[],  # Optional but defaults to empty list
        technologies_used=[]  # Optional but defaults to empty list
    )
    assert exp.end_date is None
    assert exp.achievements == []
    assert exp.technologies_used == [] 