from typing import Dict, List
import logging


class TemplateService:
    def __init__(self):
        logging.info("Template service initialized")

    def get_default_template(self) -> Dict:
        """
        Get the default HR data template for initial form values.
        
        Returns:
            Dictionary containing default template data
        """
        return {
            "name": "John Doe",
            "cpf": "123.456.789-00",
            "date": "2024-03-20T00:00:00",
            "position": "Software Engineer",
            "department": "Engineering",
            "salary": 5000.00,
            "contract_type": "CLT",
            "start_date": "2024-03-20T00:00:00",
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

    def get_empty_template(self) -> Dict:
        """
        Get an empty HR data template structure.
        
        Returns:
            Dictionary containing empty template structure
        """
        return {
            "name": "",
            "cpf": "",
            "date": "",
            "position": "",
            "department": "",
            "salary": None,
            "contract_type": "",
            "start_date": "",
            "main_skills": [],
            "hard_skills": [],
            "work_experience": []
        }

    def get_work_experience_template(self) -> Dict:
        """
        Get a template for a single work experience entry.
        
        Returns:
            Dictionary containing work experience template
        """
        return {
            "company": "",
            "position": "",
            "start_date": "",
            "end_date": "",
            "current_job": False,
            "description": "",
            "achievements": [],
            "technologies_used": []
        }

    def get_template_by_role(self, role: str) -> Dict:
        """
        Get a role-specific template with common skills and information.
        
        Args:
            role: The role/position for which to generate template
            
        Returns:
            Dictionary containing role-specific template
        """
        templates = {
            "software_engineer": {
                "position": "Software Engineer",
                "department": "Engineering",
                "main_skills": ["Problem Solving", "Communication", "Teamwork", "Analytical Thinking"],
                "hard_skills": ["Python", "JavaScript", "React", "Node.js", "Git", "SQL"],
                "contract_type": "CLT"
            },
            "data_scientist": {
                "position": "Data Scientist",
                "department": "Data Science",
                "main_skills": ["Analytical Thinking", "Communication", "Problem Solving", "Attention to Detail"],
                "hard_skills": ["Python", "R", "SQL", "Machine Learning", "Pandas", "NumPy", "Scikit-learn"],
                "contract_type": "CLT"
            },
            "product_manager": {
                "position": "Product Manager",
                "department": "Product",
                "main_skills": ["Leadership", "Communication", "Strategic Thinking", "Project Management"],
                "hard_skills": ["Jira", "Figma", "Analytics", "SQL", "Agile", "Scrum"],
                "contract_type": "CLT"
            },
            "designer": {
                "position": "UX/UI Designer",
                "department": "Design",
                "main_skills": ["Creativity", "Communication", "Empathy", "Attention to Detail"],
                "hard_skills": ["Figma", "Adobe XD", "Photoshop", "Illustrator", "Sketch", "Prototyping"],
                "contract_type": "CLT"
            }
        }

        # Get base template
        base_template = self.get_empty_template()
        
        # Apply role-specific data if available
        role_data = templates.get(role.lower(), {})
        base_template.update(role_data)
        
        return base_template

    def get_available_roles(self) -> List[str]:
        """
        Get list of available role templates.
        
        Returns:
            List of available role names
        """
        return [
            "software_engineer",
            "data_scientist", 
            "product_manager",
            "designer"
        ]

    def merge_templates(self, base_template: Dict, user_data: Dict) -> Dict:
        """
        Merge user data with a base template, preserving user values.
        
        Args:
            base_template: Base template dictionary
            user_data: User-provided data dictionary
            
        Returns:
            Merged template with user data taking precedence
        """
        merged = base_template.copy()
        
        for key, value in user_data.items():
            if value is not None and value != "":
                if isinstance(value, list) and len(value) > 0:
                    merged[key] = value
                elif not isinstance(value, list):
                    merged[key] = value
        
        return merged 