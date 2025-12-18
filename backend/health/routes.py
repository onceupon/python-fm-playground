from fastapi import APIRouter, HTTPException, Query
from . import service
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/health")
def health_check(region: str = Query(None, description="AWS region to check (defaults to us-east-1)")):
    """
    Health check endpoint to verify backend API status and AWS Bedrock connectivity.
    
    This endpoint tests:
    - boto3 client initialization
    - AWS Bedrock connectivity
    - Lists available foundation models
    
    Returns structured response with:
    - status: "healthy" or "unhealthy"
    - region: AWS region being used
    - bedrock_client_initialized: whether boto3 client was successfully created
    - available_models: list of accessible foundation models
    - model_count: number of available models
    - errors: any connectivity or configuration issues
    """
    # Use provided region or default to us-east-1
    target_region = region if region else "us-east-1"
    
    logger.info(f"Health check requested for region: {target_region}")
    
    try:
        result = service.check_bedrock_health(region_name=target_region)
        
        # Return appropriate HTTP status code based on health status
        if result["status"] == "unhealthy":
            logger.warning(f"Health check failed: {result.get('errors', [])}")
            # Still return 200 but with unhealthy status in response body
            # This is common practice for health checks to distinguish from endpoint errors
            return result
        
        logger.info(f"Health check passed: {result['model_count']} models available")
        return result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error in health_check endpoint: {error_message}")
        # For unexpected errors, return 500
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed with unexpected error: {error_message}"
        )


@router.get("/api/health/model/{model_id}")
def validate_model(model_id: str, region: str = Query(None, description="AWS region to check (defaults to us-east-1)")):
    """
    Model validation endpoint that accepts a model ID and verifies if it's accessible.
    
    This endpoint:
    - Checks if the specified model ID exists
    - Verifies accessibility in the specified region
    - Returns detailed model information if accessible
    
    Args:
        model_id: The model identifier to validate (e.g., "amazon.titan-text-express-v1")
        region: AWS region to check (defaults to us-east-1)
    
    Returns:
        - model_id: The requested model ID
        - accessible: Boolean indicating if model is accessible
        - region: AWS region checked
        - model_details: Detailed model information if accessible
        - errors: Any validation errors or issues
    """
    # Use provided region or default to us-east-1
    target_region = region if region else "us-east-1"
    
    logger.info(f"Model validation requested for model_id: {model_id} in region: {target_region}")
    
    try:
        result = service.validate_model(model_id=model_id, region_name=target_region)
        
        if not result["accessible"]:
            logger.warning(f"Model validation failed for {model_id}: {result.get('errors', [])}")
            # Return 404 if model is not found/accessible
            if any(error.get("code") == "ResourceNotFoundException" for error in result.get("errors", [])):
                raise HTTPException(
                    status_code=404,
                    detail=f"Model '{model_id}' not found or not accessible in region '{target_region}'"
                )
            # Return 403 for access denied
            elif any(error.get("code") == "AccessDeniedException" for error in result.get("errors", [])):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied to model '{model_id}'"
                )
            # For other errors, return the result with error details
            return result
        
        logger.info(f"Model validation passed for {model_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_message = str(e)
        logger.error(f"Unexpected error in validate_model endpoint for {model_id}: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"Model validation failed with unexpected error: {error_message}"
        )
