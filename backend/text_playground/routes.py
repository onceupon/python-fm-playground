from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import models
from . import claude
from . import jurassic2
import logging
import traceback


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/foundation-models/model/text/{modelId}/invoke")
def invoke(body: models.TextRequest, modelId: str):
    try:
        logger.info(f"Text invoke called with model_id: {modelId}")
        logger.debug(
            f"Text invoke request - model_id: {modelId}, "
            f"prompt: {body.prompt[:100]}..., "
            f"temperature: {body.temperature}, "
            f"max_tokens: {body.maxTokens}"
        )
        
        if modelId == "us.anthropic.claude-3-5-sonnet-20241022-v2:0":
            completion = claude.invoke(body.prompt, body.temperature, body.maxTokens)
        elif modelId == "ai21.j2-mid-v1":
            completion = jurassic2.invoke(body.prompt, body.temperature, body.maxTokens)
        else:
            logger.warning(f"Unsupported model requested: {modelId}")
            raise HTTPException(status_code=400, detail=f"Unsupported model: {modelId}")

        logger.info(f"Text invoke completed successfully for model_id: {modelId}")
        return models.TextResponse(
            completion=completion
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"ClientError in text invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {modelId}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
            f"  Temperature: {body.temperature}\n"
            f"  Max Tokens: {body.maxTokens}\n"
            f"  Full Response: {e.response}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        if error_code == "AccessDeniedException":
            raise HTTPException(status_code=403, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"{error_code}: {error_message}")
    except HTTPException:
        # Re-raise HTTPExceptions without modification
        raise
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Unexpected exception in text invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {modelId}\n"
            f"  Prompt: {body.prompt[:200]}...\n"
            f"  Temperature: {body.temperature}\n"
            f"  Max Tokens: {body.maxTokens}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        
        raise HTTPException(status_code=500, detail=f"{error_type}: {error_message}")