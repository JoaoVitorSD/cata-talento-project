from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException

from ..models.hr_data import HRData, WorkExperience


class HRService:
    def __init__(self, hr_data: HRData):
        self.hr_data = hr_data
        if not self._is_valid_cpf(hr_data.cpf):
            raise HTTPException(
                status_code=400,
                detail="CPF inválido. Todas as operações requerem um CPF válido."
            )

    def _is_valid_cpf(self, cpf: str) -> bool:
        """Validate if the CPF is valid according to Brazilian rules."""
        # Remove any non-digit characters
        cpf_digits = ''.join(filter(str.isdigit, cpf))
        
        # Check if it's a complete CPF (11 digits)
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

    def _validate_cpf(self) -> None:
        """Validate CPF before any operation."""
        if not self._is_valid_cpf(self.hr_data.cpf):
            raise HTTPException(
                status_code=400,
                detail="CPF inválido. Todas as operações requerem um CPF válido."
            )

    def add_work_experience(self, experience: WorkExperience) -> None:
        """Add a new work experience to the HR data."""
        self._validate_cpf()
        # Validate if dates overlap with existing experiences
        for existing_exp in self.hr_data.work_experience:
            if self._dates_overlap(existing_exp, experience):
                raise HTTPException(
                    status_code=400,
                    detail="Experiência profissional com datas sobrepostas a uma experiência existente"
                )
        
        self.hr_data.work_experience.append(experience)

    def update_work_experience(self, index: int, experience: WorkExperience) -> None:
        """Update an existing work experience at the specified index."""
        self._validate_cpf()
        if not 0 <= index < len(self.hr_data.work_experience):
            raise HTTPException(
                status_code=404,
                detail="Índice de experiência profissional não encontrado"
            )

        # Validate if dates overlap with other experiences
        for i, existing_exp in enumerate(self.hr_data.work_experience):
            if i != index and self._dates_overlap(existing_exp, experience):
                raise HTTPException(
                    status_code=400,
                    detail="Experiência profissional com datas sobrepostas a uma experiência existente"
                )

        self.hr_data.work_experience[index] = experience

    def remove_work_experience(self, index: int) -> None:
        """Remove a work experience at the specified index."""
        self._validate_cpf()
        if not 0 <= index < len(self.hr_data.work_experience):
            raise HTTPException(
                status_code=404,
                detail="Índice de experiência profissional não encontrado"
            )
        
        self.hr_data.work_experience.pop(index)

    def add_skill(self, skill: str, skill_type: str = "hard") -> None:
        """Add a new skill to either hard_skills or main_skills."""
        self._validate_cpf()
        if skill_type not in ["hard", "main"]:
            raise HTTPException(
                status_code=400,
                detail="Tipo de habilidade deve ser 'hard' ou 'main'"
            )

        skill = skill.strip()
        if len(skill) < 2:
            raise HTTPException(
                status_code=400,
                detail="Habilidade deve ter pelo menos 2 caracteres"
            )

        target_list = self.hr_data.hard_skills if skill_type == "hard" else self.hr_data.main_skills
        if target_list is None:
            target_list = []
            if skill_type == "hard":
                self.hr_data.hard_skills = target_list
            else:
                self.hr_data.main_skills = target_list

        if skill in target_list:
            raise HTTPException(
                status_code=400,
                detail=f"Habilidade '{skill}' já existe na lista"
            )

        target_list.append(skill)

    def remove_skill(self, skill: str, skill_type: str = "hard") -> None:
        """Remove a skill from either hard_skills or main_skills."""
        self._validate_cpf()
        if skill_type not in ["hard", "main"]:
            raise HTTPException(
                status_code=400,
                detail="Tipo de habilidade deve ser 'hard' ou 'main'"
            )

        target_list = self.hr_data.hard_skills if skill_type == "hard" else self.hr_data.main_skills
        if not target_list or skill not in target_list:
            raise HTTPException(
                status_code=404,
                detail=f"Habilidade '{skill}' não encontrada na lista"
            )

        target_list.remove(skill)

    def calculate_total_experience(self) -> timedelta:
        """Calculate total work experience time."""
        self._validate_cpf()
        total_time = timedelta()
        
        for exp in self.hr_data.work_experience:
            end_date = exp.end_date if not exp.current_job else datetime.now()
            if end_date and exp.start_date:
                total_time += end_date - exp.start_date

        return total_time

    def _dates_overlap(self, exp1: WorkExperience, exp2: WorkExperience) -> bool:
        """Check if two work experiences have overlapping dates."""
        def get_end_date(exp: WorkExperience) -> datetime:
            if exp.current_job:
                return datetime.now()
            if exp.end_date is None:
                return exp.start_date  # If no end_date and not current_job, use start_date as end_date
            return exp.end_date

        start1, end1 = exp1.start_date, get_end_date(exp1)
        start2, end2 = exp2.start_date, get_end_date(exp2)

        return (start1 <= end2 and start2 <= end1) 