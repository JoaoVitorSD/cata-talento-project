from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import traceback
from datetime import datetime
from .api.endpoints import router
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HR Document OCR API",
    description="API for processing HR documents using OCR",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Get the full stack trace
        stack_trace = traceback.format_exc()
        
        # Log the error with stack trace
        logger.error("Exception occurred:")
        logger.error(f"Path: {request.url.path}")
        logger.error(f"Method: {request.method}")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Stack Trace:\n{stack_trace}")
        
        # Return error response to client
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(e),
                "path": request.url.path,
                "timestamp": datetime.now().isoformat()
            }
        )

# Include the router
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()} 