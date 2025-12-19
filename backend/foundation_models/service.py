import boto3
import logging
import traceback

logger = logging.getLogger(__name__)

bedrock_client = boto3.client(
    service_name="bedrock",
    region_name="us-east-1"
)


def list_foundation_models():
    try:
        logger.info("Calling bedrock.list_foundation_models()")
        logger.debug("Bedrock list_foundation_models request - no parameters")
        
        response = bedrock_client.list_foundation_models()
        
        logger.debug(f"Bedrock list_foundation_models response metadata: {response.get('ResponseMetadata')}")
        logger.debug(f"Bedrock list_foundation_models - model count: {len(response.get('modelSummaries', []))}")
        
        model_summaries = response['modelSummaries']
        logger.info(f"Successfully retrieved {len(model_summaries)} foundation models")
        
        return model_summaries
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Error in list_foundation_models:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        raise


def get_foundation_model(model_id):
    try:
        logger.info(f"Calling bedrock.get_foundation_model() with model_id: {model_id}")
        logger.debug(f"Bedrock get_foundation_model request - modelIdentifier: {model_id}")
        
        response = bedrock_client.get_foundation_model(
            modelIdentifier=model_id
        )
        
        logger.debug(f"Bedrock get_foundation_model response metadata: {response.get('ResponseMetadata')}")
        logger.debug(f"Bedrock get_foundation_model response - modelDetails: {response.get('modelDetails')}")
        
        model_details = response['modelDetails']
        logger.info(f"Successfully retrieved foundation model details for model_id: {model_id}")
        
        return model_details
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Error in get_foundation_model:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        raise