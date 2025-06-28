import logging
from typing import Dict, Union, cast

from fastapi import APIRouter, HTTPException, UploadFile

from ..core.dependencies import (get_anthropic_service, get_mongodb_service,
                                 get_ocr_service, get_template_service,
                                 get_validation_service)
from ..models.hr_data import HRData

router = APIRouter()


@router.post("/process-pdf", response_model=Dict)
async def process_pdf(file: UploadFile):
    """
    Process a PDF document to extract HR data using OCR and AI enhancement.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Dictionary containing:
        - hr_data: Extracted and structured HR data
        - errors: List of validation errors if any
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    if not file or not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Get services
        ocr_service = get_ocr_service()
        anthropic_service = get_anthropic_service()
        
        # Read the uploaded file
        contents = await file.read()
        
        # Extract text from PDF
        try:
            extracted_text = ocr_service.extract_text_from_pdf(contents)
        except Exception as e:
            logging.error(f"OCR Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error extracting text from PDF")

        # Get AI-enhanced extraction with Claude
        ai_extracted_data = await anthropic_service.analyze_hr_document(extracted_text)
        
        # Create HR data directly from AI extraction instead of using OCR fallback
        if ai_extracted_data:
            # Use validation service to convert JSON to HRData model
            validation_service = get_validation_service()
            validated_hr_data = validation_service.validate_hr_data(ai_extracted_data)
            
            # If validation successful, return the validated data with empty errors
            if not isinstance(validated_hr_data, dict) or "errors" not in validated_hr_data:
                return {
                    "hr_data": validated_hr_data,
                    "errors": {}
                }
            else:
                logging.warning(f"AI extracted data validation failed: {validated_hr_data}")
                return {
                    "hr_data": ai_extracted_data,
                    "errors": validated_hr_data["errors"]
                }
        
        # Fallback: create empty template if AI extraction fails
        template_service = get_template_service()
        fallback_data = template_service.get_empty_template()
        fallback_data['name'] = 'Extracted from PDF'  # Add minimal indication
        
        validation_service = get_validation_service()
        validated_hr_data = validation_service.validate_hr_data(fallback_data)
        
        # Return both HR data and any validation errors
        if isinstance(validated_hr_data, dict) and "errors" in validated_hr_data:
            return {
                "hr_data": ai_extracted_data,
                "errors": validated_hr_data["errors"]
            }
        else:
            return {
                "hr_data": validated_hr_data,
                "errors": {}
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Processing Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/store-document", response_model=Dict)
async def store_document(data: Dict):
    """
    Validate and store HR data in the database.
    
    Args:
        data: HR data dictionary to validate and store
        
    Returns:
        Success status and document ID
        
    Raises:
        HTTPException: If validation fails or storage fails
    """
    try:
        # Get services
        validation_service = get_validation_service()
        mongodb_service = get_mongodb_service()
        
        # Validate the data
        validated_data = validation_service.validate_hr_data(data)
        
        # If validation returned errors, return them
        if isinstance(validated_data, dict) and "errors" in validated_data:
            raise HTTPException(
                status_code=422,
                detail=validated_data["errors"]
            )
        
        # At this point, validated_data is an HRData object
        # Convert Pydantic model to dict
        hr_data_obj = cast(HRData, validated_data)
        document_data = hr_data_obj.model_dump()
        
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
    """
    Get the default HR data template for initial form values.
    
    Returns:
        Default template data dictionary
    """
    template_service = get_template_service()
    return template_service.get_default_template()


@router.get("/template/roles", response_model=Dict)
async def get_available_roles():
    """
    Get list of available role templates.
    
    Returns:
        Dictionary containing list of available roles
    """
    template_service = get_template_service()
    return {"roles": template_service.get_available_roles()}


@router.get("/template/{role}", response_model=Dict)
async def get_template_by_role(role: str):
    """
    Get a role-specific HR data template.
    
    Args:
        role: Role name for which to get template
        
    Returns:
        Role-specific template data dictionary
    """
    template_service = get_template_service()
    return template_service.get_template_by_role(role)


@router.post("/validate", response_model=Dict)
async def validate_data(data: Dict):
    """
    Validate HR data without storing it.
    
    Args:
        data: HR data dictionary to validate
        
    Returns:
        Validation status and errors if any
    """
    validation_service = get_validation_service()
    return validation_service.validate_data_without_storing(data)


@router.post("/summarize-pdf", response_model=Dict)
async def summarize_pdf(file: UploadFile):
    """
    Generate a summary of the PDF document content.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Document summary
        
    Raises:
        HTTPException: If file is invalid or processing fails
    """
    if not file or not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Get services
        ocr_service = get_ocr_service()
        anthropic_service = get_anthropic_service()
        
        # Read the uploaded file
        contents = await file.read()
        
        # Extract text from PDF
        try:
            extracted_text = ocr_service.extract_text_from_pdf(contents)
        except Exception as e:
            logging.error(f"OCR Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error extracting text from PDF")

        # Generate summary using Claude
        summary = await anthropic_service.generate_document_summary(extracted_text)
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Summary Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))