from typing import Optional
from fastapi import HTTPException, status

class ThumbnailFactoryException(Exception):
    """Base exception class for Thumbnail Factory application."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ModelGenerationException(ThumbnailFactoryException):
    """Exception raised when model generation fails."""
    def __init__(self, message: str, model_name: str):
        self.model_name = model_name
        super().__init__(message, "MODEL_GENERATION_ERROR")

class InsufficientCreditsException(ThumbnailFactoryException):
    """Exception raised when user has insufficient credits."""
    def __init__(self, message: str = "Insufficient credits for this operation"):
        super().__init__(message, "INSUFFICIENT_CREDITS")

class AssetNotFoundException(ThumbnailFactoryException):
    """Exception raised when an asset is not found."""
    def __init__(self, asset_id: str):
        super().__init__(f"Asset with ID {asset_id} not found", "ASSET_NOT_FOUND")

class ProjectNotFoundException(ThumbnailFactoryException):
    """Exception raised when a project is not found."""
    def __init__(self, project_id: str):
        super().__init__(f"Project with ID {project_id} not found", "PROJECT_NOT_FOUND")

class JobNotFoundException(ThumbnailFactoryException):
    """Exception raised when a job is not found."""
    def __init__(self, job_id: str):
        super().__init__(f"Job with ID {job_id} not found", "JOB_NOT_FOUND")

def handle_exception(exc: Exception) -> HTTPException:
    """Convert application exceptions to HTTP exceptions."""
    if isinstance(exc, ThumbnailFactoryException):
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, InsufficientCreditsException):
            status_code = status.HTTP_402_PAYMENT_REQUIRED
        elif isinstance(exc, (AssetNotFoundException, ProjectNotFoundException, JobNotFoundException)):
            status_code = status.HTTP_404_NOT_FOUND
            
        return HTTPException(
            status_code=status_code,
            detail={
                "message": exc.message,
                "error_code": exc.error_code
            }
        )
    
    # For unexpected errors, return 500
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred"
    )