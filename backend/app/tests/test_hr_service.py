from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from ..models.hr_data import HRData, WorkExperience
from ..services.hr_service import HRService


@pytest.fixture
def sample_hr_data():
    return HRData(
        name="John Doe",
        cpf="123.456.789-00",
        position="Software Engineer",
        salary=5000.00,
        contract_type="CLT",
        main_skills=["Leadership", "Communication"],
        hard_skills=["Python", "React"],
        work_experience=[]
    )

@pytest.fixture
def sample_work_experience():
    return WorkExperience(
        company="Tech Corp",
        position="Senior Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Desenvolvimento de aplicações web",
        achievements=["Liderou equipe de 5 desenvolvedores"],
        technologies_used=["React", "Node.js"]
    )

@pytest.fixture
def valid_cpf_hr_data():
    return HRData(
        name="John Doe",
        cpf="529.982.247-25",  # Valid CPF
        position="Software Engineer",
        salary=5000.00,
        contract_type="CLT",
        main_skills=["Leadership", "Communication"],
        hard_skills=["Python", "React"],
        work_experience=[]
    )

@pytest.fixture
def invalid_cpf_hr_data():
    return HRData(
        name="John Doe",
        cpf="123.456.789-00",  # Invalid CPF (all same digits)
        position="Software Engineer",
        salary=5000.00,
        contract_type="CLT",
        main_skills=["Leadership", "Communication"],
        hard_skills=["Python", "React"],
        work_experience=[]
    )

def test_add_work_experience(sample_hr_data, sample_work_experience):
    service = HRService(sample_hr_data)
    service.add_work_experience(sample_work_experience)
    assert len(sample_hr_data.work_experience) == 1
    assert sample_hr_data.work_experience[0] == sample_work_experience

def test_add_overlapping_work_experience(sample_hr_data, sample_work_experience):
    service = HRService(sample_hr_data)
    service.add_work_experience(sample_work_experience)
    
    overlapping_exp = WorkExperience(
        company="Another Corp",
        position="Developer",
        start_date=datetime(2023, 6, 1),
        end_date=datetime(2024, 1, 1),
        current_job=False,
        description="Desenvolvimento backend",
        achievements=[],
        technologies_used=["Python"]
    )
    
    with pytest.raises(HTTPException) as exc_info:
        service.add_work_experience(overlapping_exp)
    assert exc_info.value.status_code == 400
    assert "datas sobrepostas" in exc_info.value.detail

def test_update_work_experience(sample_hr_data, sample_work_experience):
    service = HRService(sample_hr_data)
    service.add_work_experience(sample_work_experience)
    
    updated_exp = WorkExperience(
        company="Tech Corp Updated",
        position="Lead Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Liderança técnica",
        achievements=["Liderou equipe de 10 desenvolvedores"],
        technologies_used=["React", "Node.js", "AWS"]
    )
    
    service.update_work_experience(0, updated_exp)
    assert sample_hr_data.work_experience[0] == updated_exp

def test_update_nonexistent_work_experience(sample_hr_data, sample_work_experience):
    service = HRService(sample_hr_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_work_experience(0, sample_work_experience)
    assert exc_info.value.status_code == 404

def test_remove_work_experience(sample_hr_data, sample_work_experience):
    service = HRService(sample_hr_data)
    service.add_work_experience(sample_work_experience)
    service.remove_work_experience(0)
    assert len(sample_hr_data.work_experience) == 0

def test_remove_nonexistent_work_experience(sample_hr_data):
    service = HRService(sample_hr_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.remove_work_experience(0)
    assert exc_info.value.status_code == 404

def test_add_skill(sample_hr_data):
    service = HRService(sample_hr_data)
    
    # Test adding hard skill
    service.add_skill("Docker", "hard")
    assert "Docker" in sample_hr_data.hard_skills
    
    # Test adding main skill
    service.add_skill("Problem Solving", "main")
    assert "Problem Solving" in sample_hr_data.main_skills

def test_add_duplicate_skill(sample_hr_data):
    service = HRService(sample_hr_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.add_skill("Python", "hard")
    assert exc_info.value.status_code == 400
    assert "já existe na lista" in exc_info.value.detail

def test_add_invalid_skill_type(sample_hr_data):
    service = HRService(sample_hr_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.add_skill("Skill", "invalid")
    assert exc_info.value.status_code == 400
    assert "Tipo de habilidade deve ser 'hard' ou 'main'" in exc_info.value.detail

def test_remove_skill(sample_hr_data):
    service = HRService(sample_hr_data)
    
    # Test removing hard skill
    service.remove_skill("Python", "hard")
    assert "Python" not in sample_hr_data.hard_skills
    
    # Test removing main skill
    service.remove_skill("Leadership", "main")
    assert "Leadership" not in sample_hr_data.main_skills

def test_remove_nonexistent_skill(sample_hr_data):
    service = HRService(sample_hr_data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.remove_skill("NonexistentSkill", "hard")
    assert exc_info.value.status_code == 404

def test_calculate_total_experience(sample_hr_data):
    service = HRService(sample_hr_data)
    
    # Add two non-overlapping experiences
    exp1 = WorkExperience(
        company="Company A",
        position="Developer",
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2021, 12, 31),
        current_job=False,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    exp2 = WorkExperience(
        company="Company B",
        position="Senior Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    service.add_work_experience(exp1)
    service.add_work_experience(exp2)
    
    total_time = service.calculate_total_experience()
    expected_days = (datetime(2021, 12, 31) - datetime(2020, 1, 1)).days + \
                   (datetime(2023, 12, 31) - datetime(2022, 1, 1)).days + 2  # +2 for inclusive dates
    assert total_time.days == expected_days

def test_calculate_total_experience_with_current_job(sample_hr_data):
    service = HRService(sample_hr_data)
    
    # Add an experience with current_job=True
    current_exp = WorkExperience(
        company="Current Company",
        position="Developer",
        start_date=datetime(2023, 1, 1),
        end_date=None,
        current_job=True,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    service.add_work_experience(current_exp)
    
    # The total experience should be from start_date until now
    total_time = service.calculate_total_experience()
    expected_min_days = (datetime.now() - datetime(2023, 1, 1)).days
    assert total_time.days >= expected_min_days

def test_init_with_invalid_cpf(invalid_cpf_hr_data):
    with pytest.raises(HTTPException) as exc_info:
        HRService(invalid_cpf_hr_data)
    assert exc_info.value.status_code == 400
    assert "CPF inválido" in exc_info.value.detail

def test_init_with_valid_cpf(valid_cpf_hr_data):
    service = HRService(valid_cpf_hr_data)
    assert service.hr_data == valid_cpf_hr_data

def test_work_experience_operations(valid_cpf_hr_data, sample_work_experience):
    service = HRService(valid_cpf_hr_data)
    
    # Test adding work experience
    service.add_work_experience(sample_work_experience)
    assert len(valid_cpf_hr_data.work_experience) == 1
    assert valid_cpf_hr_data.work_experience[0] == sample_work_experience
    
    # Test adding overlapping experience
    overlapping_exp = WorkExperience(
        company="Another Corp",
        position="Developer",
        start_date=datetime(2023, 6, 1),
        end_date=datetime(2024, 1, 1),
        current_job=False,
        description="Desenvolvimento backend",
        achievements=[],
        technologies_used=["Python"]
    )
    
    with pytest.raises(HTTPException) as exc_info:
        service.add_work_experience(overlapping_exp)
    assert exc_info.value.status_code == 400
    assert "datas sobrepostas" in exc_info.value.detail
    
    # Test updating work experience
    updated_exp = WorkExperience(
        company="Tech Corp Updated",
        position="Lead Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Liderança técnica",
        achievements=["Liderou equipe de 10 desenvolvedores"],
        technologies_used=["React", "Node.js", "AWS"]
    )
    
    service.update_work_experience(0, updated_exp)
    assert valid_cpf_hr_data.work_experience[0] == updated_exp
    
    # Test updating nonexistent experience
    with pytest.raises(HTTPException) as exc_info:
        service.update_work_experience(1, sample_work_experience)
    assert exc_info.value.status_code == 404
    
    # Test removing work experience
    service.remove_work_experience(0)
    assert len(valid_cpf_hr_data.work_experience) == 0
    
    # Test removing nonexistent experience
    with pytest.raises(HTTPException) as exc_info:
        service.remove_work_experience(0)
    assert exc_info.value.status_code == 404

def test_skill_operations(valid_cpf_hr_data):
    service = HRService(valid_cpf_hr_data)
    
    # Test adding skills
    service.add_skill("Docker", "hard")
    assert "Docker" in valid_cpf_hr_data.hard_skills
    
    service.add_skill("Problem Solving", "main")
    assert "Problem Solving" in valid_cpf_hr_data.main_skills
    
    # Test adding duplicate skill
    with pytest.raises(HTTPException) as exc_info:
        service.add_skill("Python", "hard")
    assert exc_info.value.status_code == 400
    assert "já existe na lista" in exc_info.value.detail
    
    # Test adding invalid skill type
    with pytest.raises(HTTPException) as exc_info:
        service.add_skill("Skill", "invalid")
    assert exc_info.value.status_code == 400
    assert "Tipo de habilidade deve ser 'hard' ou 'main'" in exc_info.value.detail
    
    # Test removing skills
    service.remove_skill("Python", "hard")
    assert "Python" not in valid_cpf_hr_data.hard_skills
    
    service.remove_skill("Leadership", "main")
    assert "Leadership" not in valid_cpf_hr_data.main_skills
    
    # Test removing nonexistent skill
    with pytest.raises(HTTPException) as exc_info:
        service.remove_skill("NonexistentSkill", "hard")
    assert exc_info.value.status_code == 404

def test_experience_calculation(valid_cpf_hr_data):
    service = HRService(valid_cpf_hr_data)
    
    # Add two non-overlapping experiences
    exp1 = WorkExperience(
        company="Company A",
        position="Developer",
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2021, 12, 31),
        current_job=False,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    exp2 = WorkExperience(
        company="Company B",
        position="Senior Developer",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2023, 12, 31),
        current_job=False,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    service.add_work_experience(exp1)
    service.add_work_experience(exp2)
    
    total_time = service.calculate_total_experience()
    expected_days = (datetime(2021, 12, 31) - datetime(2020, 1, 1)).days + \
                   (datetime(2023, 12, 31) - datetime(2022, 1, 1)).days + 2  # +2 for inclusive dates
    assert total_time.days == expected_days
    
    # Test with current job
    current_exp = WorkExperience(
        company="Current Company",
        position="Developer",
        start_date=datetime(2023, 1, 1),
        end_date=None,
        current_job=True,
        description="Development",
        achievements=[],
        technologies_used=[]
    )
    
    service.add_work_experience(current_exp)
    total_time = service.calculate_total_experience()
    expected_min_days = (datetime.now() - datetime(2023, 1, 1)).days
    assert total_time.days >= expected_min_days

def test_cpf_validation_cases():
    # Test various CPF validation cases
    test_cases = [
        ("529.982.247-25", True),  # Valid CPF
        ("123.456.789-00", False),  # Invalid CPF (all same digits)
        ("111.111.111-11", False),  # Invalid CPF (all ones)
        ("123.456.789-09", False),  # Invalid CPF (wrong check digits)
        ("52998224725", True),      # Valid CPF without formatting
        ("529.982.247-2", False),   # Invalid CPF (incomplete)
        ("529.982.247-256", False), # Invalid CPF (too long)
    ]
    
    for cpf, should_be_valid in test_cases:
        hr_data = HRData(
            name="Test User",
            cpf=cpf,
            position="Developer",
            salary=5000.00,
            contract_type="CLT",
            main_skills=[],
            hard_skills=[],
            work_experience=[]
        )
        
        if should_be_valid:
            service = HRService(hr_data)
            assert service.hr_data.cpf == cpf
        else:
            with pytest.raises(HTTPException) as exc_info:
                HRService(hr_data)
            assert exc_info.value.status_code == 400
            assert "CPF inválido" in exc_info.value.detail 