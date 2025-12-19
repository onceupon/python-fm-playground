from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import service
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/foundation-models")
def list_foundation_models():
    try:
        logger.info("Listing foundation models")
        result = service.list_foundation_models()
        logger.info(f"Successfully retrieved {len(result)} foundation models")
        logger.debug(f"Foundation models list: {result}")
        return result
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"ClientError in list_foundation_models:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Full Response: {e.response}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        if error_code == "AccessDeniedException":
            raise HTTPException(status_code=403, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"{error_code}: {error_message}")
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Unexpected exception in list_foundation_models:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        raise HTTPException(status_code=500, detail=f"{error_type}: {error_message}")

@router.get("/foundation-models/model/{model_id}")
def get_foundation_model_details(model_id: str):
    try:
        logger.info(f"Getting foundation model details for model_id: {model_id}")
        result = service.get_foundation_model(model_id)
        logger.info(f"Successfully retrieved details for model_id: {model_id}")
        logger.debug(f"Model details: {result}")
        return result
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"ClientError in get_foundation_model_details:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Full Response: {e.response}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        if error_code == "AccessDeniedException":
            raise HTTPException(status_code=403, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"{error_code}: {error_message}")
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Unexpected exception in get_foundation_model_details:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        raise HTTPException(status_code=500, detail=f"{error_type}: {error_message}")

