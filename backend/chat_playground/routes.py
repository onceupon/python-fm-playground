from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import models
from . import services
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/foundation-models/model/chat/{model_id}/invoke")
def invoke(body: models.ChatRequest, model_id: str):
    try:
        logger.info(f"Chat invoke called with model_id: {model_id}")
        logger.debug(f"Chat invoke request - model_id: {model_id}, prompt: {body.prompt[:100]}...")
        
        completion = services.invoke(body.prompt, model_id)
        
        logger.info(f"Chat invoke completed successfully for model_id: {model_id}")
        return models.ChatResponse(
            completion=completion
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"ClientError in chat invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
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
            f"Unexpected exception in chat invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        raise HTTPException(status_code=500, detail=f"{error_type}: {error_message}")
