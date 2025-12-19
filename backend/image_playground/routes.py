from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import models
from . import services
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/foundation-models/model/image/{model_id}/invoke")
def invoke(body: models.ImageRequest, model_id: str):
    try:
        logger.info(f"Image invoke called with model_id: {model_id}")
        logger.debug(
            f"Image invoke request - model_id: {model_id}, "
            f"prompt: {body.prompt[:100]}..., "
            f"style_preset: {body.stylePreset}"
        )
        
        response = services.invoke(body.prompt, body.stylePreset, model_id)
        
        logger.info(f"Image invoke completed successfully for model_id: {model_id}")
        return {
            "imageByteArray": response
        }
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"ClientError in image invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
            f"  Style Preset: {body.stylePreset}\n"
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
            f"Unexpected exception in image invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
            f"  Style Preset: {body.stylePreset}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        raise HTTPException(status_code=500, detail=f"{error_type}: {error_message}")
