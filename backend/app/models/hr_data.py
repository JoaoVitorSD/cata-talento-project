from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
import re

class WorkExperience(BaseModel):
    company: str = Field(..., min_length=1, description="Nome da empresa")
    position: str = Field(..., min_length=1, description="Cargo ocupado")
    start_date: datetime = Field(..., description="Data de início")
    end_date: Optional[datetime] = Field(None, description="Data de término")
    current_job: bool = Field(False, description="Emprego atual")
    description: str = Field(..., min_length=10, description="Descrição das atividades")
    achievements: List[str] = Field(default=[], description="Lista de conquistas")
    technologies_used: List[str] = Field(default=[], description="Tecnologias utilizadas")

    @validator('end_date')
    def validate_end_date(cls, end_date, values):
        if end_date and 'start_date' in values:
            if end_date < values['start_date']:
                raise ValueError('A data de término não pode ser anterior à data de início')
            
            if end_date > datetime.now():
                raise ValueError('A data de término não pode ser no futuro')
        
        if 'current_job' in values and values['current_job'] and end_date:
            raise ValueError('Não é possível definir data de término para emprego atual')
            
        return end_date

    @validator('start_date')
    def validate_start_date(cls, start_date):
        if start_date > datetime.now():
            raise ValueError('A data de início não pode ser no futuro')
        return start_date

    @validator('achievements')
    def validate_achievements(cls, achievements):
        if achievements:
            for achievement in achievements:
                if len(achievement.strip()) < 5:
                    raise ValueError('Cada conquista deve ter pelo menos 5 caracteres')
        return achievements

    @validator('technologies_used')
    def validate_technologies(cls, technologies):
        if technologies:
            for tech in technologies:
                if len(tech.strip()) < 2:
                    raise ValueError('Cada tecnologia deve ter pelo menos 2 caracteres')
        return technologies

class HRData(BaseModel):
    name: str = Field(..., min_length=3, description="Nome completo")
    cpf: str = Field(..., description="CPF no formato XXX.XXX.XXX-XX")
    position: Optional[str] = Field(None, min_length=2, description="Cargo pretendido")
    salary: Optional[float] = Field(None, gt=0, description="Salário pretendido")
    contract_type: Optional[str] = Field(None, description="Tipo de contrato")
    main_skills: Optional[List[str]] = Field(default=None, description="Habilidades principais")
    hard_skills: Optional[List[str]] = Field(default=None, description="Habilidades técnicas")
    work_experience: List[WorkExperience] = Field(default=[], description="Experiências profissionais")

    @validator('cpf')
    def validate_cpf(cls, cpf):
        # Remove any non-digit characters for validation
        cpf_digits = ''.join(filter(str.isdigit, cpf))
        
        # Check if it's a partial CPF (allow partial input)
        if len(cpf_digits) < 11:
            # If it's a partial CPF, just format what we have
            if len(cpf_digits) <= 3:
                return cpf_digits
            elif len(cpf_digits) <= 6:
                return f'{cpf_digits[:3]}.{cpf_digits[3:]}'
            elif len(cpf_digits) <= 9:
                return f'{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:]}'
            else:
                return f'{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}'
        
        # For complete CPF (11 digits), perform full validation
        if len(cpf_digits) > 11:
            raise ValueError('CPF não pode ter mais que 11 dígitos')
            
        # Check if all digits are the same
        if len(set(cpf_digits)) == 1:
            raise ValueError('CPF inválido')
            
        # Validate first digit
        sum_products = sum(int(a) * b for a, b in zip(cpf_digits[0:9], range(10, 1, -1)))
        expected_digit = (sum_products * 10 % 11) % 10
        if int(cpf_digits[9]) != expected_digit:
            raise ValueError('CPF inválido')
            
        # Validate second digit
        sum_products = sum(int(a) * b for a, b in zip(cpf_digits[0:10], range(11, 1, -1)))
        expected_digit = (sum_products * 10 % 11) % 10
        if int(cpf_digits[10]) != expected_digit:
            raise ValueError('CPF inválido')
            
        # Format CPF to standard format
        return f'{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}'

    @validator('salary')
    def validate_salary(cls, salary):
        if salary is not None and salary <= 0:
            raise ValueError('O salário deve ser maior que zero')
        return salary

    @validator('main_skills')
    def validate_main_skills(cls, skills):
        if skills:
            for skill in skills:
                if len(skill.strip()) < 2:
                    raise ValueError('Cada habilidade principal deve ter pelo menos 2 caracteres')
        return skills

    @validator('hard_skills')
    def validate_hard_skills(cls, skills):
        if skills:
            for skill in skills:
                if len(skill.strip()) < 2:
                    raise ValueError('Cada habilidade técnica deve ter pelo menos 2 caracteres')
        return skills

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "cpf": "123.456.789-00",
                "position": "Software Engineer",
                "salary": 5000.00,
                "contract_type": "CLT",
                "main_skills": ["Leadership", "Communication", "Problem Solving"],
                "hard_skills": ["Python", "React", "MongoDB", "Docker"],
                "work_experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Developer",
                        "start_date": "2022-01-01T00:00:00",
                        "end_date": "2023-12-31T00:00:00",
                        "current_job": False,
                        "description": "Desenvolvimento de aplicações web",
                        "achievements": [
                            "Liderou equipe de 5 desenvolvedores",
                            "Reduziu tempo de deploy em 50%"
                        ],
                        "technologies_used": ["React", "Node.js", "AWS"]
                    }
                ]
            }
        } 