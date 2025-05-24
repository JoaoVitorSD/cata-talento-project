from fastapi import APIRouter, UploadFile, HTTPException
from ..services.ocr_service import OCRService
from ..services.mongodb_service import MongoDBService
from ..models.hr_data import HRData, WorkExperience
from anthropic import Anthropic
from typing import Dict, Optional, Union
from datetime import datetime
from pydantic import ValidationError
import json
import os
import logging

router = APIRouter()

# Template data for initial form values
TEMPLATE_DATA = {
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

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logging.error("ANTHROPIC_API_KEY not found in environment variables")
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is required")

# Configure Anthropic Client
anthropic = Anthropic(api_key=api_key)

# Initialize MongoDB service
mongodb_service = MongoDBService()

async def analyze_text_with_claude(text: str) -> Dict:
    try:
        # Create message synchronously since Anthropic's Python client doesn't support async
        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=3000,
            temperature=0.3,
            system="You are a helpful assistant that extracts HR document information. You must return only a JSON object.",
            messages=[{
                "role": "user",
                "content": f"""Extract the following fields from this HR document text if present: 
                - name
                - cpf
                - date
                - position
                - department
                - salary
                - contract_type
                - start_date
                - main_skills (list of soft/interpersonal skills)
                - hard_skills (list of technical skills, tools, technologies)
                - work_experience (list of work experiences with the following structure for each):
                  * company
                  * position
                  * start_date
                  * end_date (if not current job)
                  * current_job (boolean)
                  * description
                  * achievements (list of key achievements)
                  * technologies_used (list of technologies used)
                
                For skills and work experience, analyze the text carefully and extract:
                - Any mentioned skills, technologies, or competencies
                - All work experiences with their details
                - Key achievements and responsibilities from each role
                - Technologies and tools used in each position
                
                Return ONLY a valid JSON object with these fields, nothing else.
                
                Document text:
                {text}"""
            }]
        )
        
        # Extract the JSON response
        if response and hasattr(response, 'content') and response.content:
            content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse Claude response as JSON: {content}")
                return {}
        return {}
            
    except Exception as e:
        logging.error(f"Error calling Claude API: {str(e)}")
        return {}

@router.post("/process-pdf", response_model=HRData)
async def process_pdf(file: UploadFile):
    if not file or not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Extract text from PDF
        ocr_service = OCRService()
        try:
            extracted_text = ocr_service.extract_text_from_pdf(contents)
        except Exception as e:
            logging.error(f"OCR Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error extracting text from PDF")

        # First get AI-enhanced extraction with Claude
        ai_extracted_data = await analyze_text_with_claude(extracted_text)
        
        # Then use traditional extraction as fallback
        hr_data = ocr_service.extract_hr_data(extracted_text)
        
        # Merge AI and traditional extraction, preferring AI results when available
        for field in ai_extracted_data:
            if ai_extracted_data[field]:
                setattr(hr_data, field, ai_extracted_data[field])
        
        return hr_data
        
    except Exception as e:
        logging.error(f"Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def validate_hr_data(data: Dict) -> Union[HRData, Dict[str, list]]:
    """
    Validate HR data against the model.
    Returns either a valid HRData object or a dictionary of validation errors.
    """
    try:
        # Convert string dates to datetime objects for validation
        if isinstance(data.get('date'), str):
            data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        if isinstance(data.get('start_date'), str):
            data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            
        # Handle work experience dates
        if 'work_experience' in data:
            for exp in data['work_experience']:
                if isinstance(exp.get('start_date'), str):
                    exp['start_date'] = datetime.fromisoformat(exp['start_date'].replace('Z', '+00:00'))
                if isinstance(exp.get('end_date'), str):
                    exp['end_date'] = datetime.fromisoformat(exp['end_date'].replace('Z', '+00:00'))

        return HRData(**data)
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "general"
            if field not in errors:
                errors[field] = []
            errors[field].append(error["msg"])
        return {"errors": errors}
    except Exception as e:
        return {"errors": {"general": [str(e)]}}

@router.post("/store-document", response_model=Dict)
async def store_document(data: Dict):
    try:
        # Validate the data
        validated_data = validate_hr_data(data)
        
        # If validation returned errors, return them
        if isinstance(validated_data, dict) and "errors" in validated_data:
            raise HTTPException(
                status_code=422,
                detail=validated_data["errors"]
            )
        
        # Convert Pydantic model to dict
        document_data = validated_data.model_dump()
        
        # Store in MongoDB
        document_id = mongodb_service.store_document(document_data)
        
        return {"status": "success", "document_id": document_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error storing document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store document")

@router.get("/template", response_model=Dict)
async def get_template():
    """Return template data for initial form values"""
    return TEMPLATE_DATA

@router.post("/validate", response_model=Dict)
async def validate_data(data: Dict):
    """
    Validate HR data without storing it.
    Returns validation errors if any, or success message if valid.
    """
    validated_data = validate_hr_data(data)
    
    if isinstance(validated_data, dict) and "errors" in validated_data:
        return {"valid": False, "errors": validated_data["errors"]}
    
    return {"valid": True}