from anthropic import Anthropic
from typing import Dict
import json
import os
import logging


class AnthropicService:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logging.error("ANTHROPIC_API_KEY not found in environment variables")
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is required")
        
        # Configure Anthropic Client
        self.client = Anthropic(api_key=api_key)
        logging.info("Anthropic service initialized successfully")

    async def analyze_hr_document(self, text: str) -> Dict:
        """
        Analyze HR document text using Claude AI to extract structured data.
        
        Args:
            text: The extracted text from the document
            
        Returns:
            Dict containing extracted HR data fields
        """
        try:
            # Create message synchronously since Anthropic's Python client doesn't support async
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=3000,
                temperature=0.3,
                system="You are a helpful assistant that extracts resumes document information. You must return only a JSON object.",
                messages=[{
                    "role": "user",
                    "content": self._build_extraction_prompt(text)
                }]
            )
            
            # Extract the JSON response
            if response and hasattr(response, 'content') and response.content:
                # Access the content properly based on Anthropic API structure
                content_block = response.content[0]
                if hasattr(content_block, 'text'):
                    content = content_block.text
                else:
                    content = str(content_block)
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse Claude response as JSON: {content}")
                    return {}
            return {}
                
        except Exception as e:
            logging.error(f"Error calling Claude API: {str(e)}")
            return {}

    def _build_extraction_prompt(self, text: str) -> str:
        """
        Build the prompt for HR document extraction.
        
        Args:
            text: The document text to analyze
            
        Returns:
            Formatted prompt string
        """
        return f"""Extract the following fields from this HR document text if present: 
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

    async def generate_document_summary(self, text: str) -> Dict:
        """
        Generate a summary of the HR document.
        
        Args:
            text: The document text to summarize
            
        Returns:
            Dict containing document summary
        """
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.3,
                system="You are a helpful assistant that creates professional summaries of HR documents.",
                messages=[{
                    "role": "user",
                    "content": f"""Create a professional summary of this HR document. Include:
                    - Key candidate information
                    - Main qualifications and skills
                    - Notable experience highlights
                    - Overall assessment
                    
                    Return the summary as a JSON object with 'summary' field.
                    
                    Document text:
                    {text}"""
                }]
            )
            
            if response and hasattr(response, 'content') and response.content:
                # Access the content properly based on Anthropic API structure
                content_block = response.content[0]
                if hasattr(content_block, 'text'):
                    content = content_block.text
                else:
                    content = str(content_block)
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse Claude summary response as JSON: {content}")
                    return {"summary": content}  # Return raw content if JSON parsing fails
            return {"summary": "Unable to generate summary"}
                
        except Exception as e:
            logging.error(f"Error generating summary with Claude API: {str(e)}")
            return {"summary": "Error generating summary"} 