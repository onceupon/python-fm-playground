import boto3
import logging
import traceback
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

logger = logging.getLogger(__name__)


def check_bedrock_health(region_name="us-east-1"):
    """
    Check AWS Bedrock connectivity and list available models.
    
    Returns:
        dict: Health check response with status, region, models, and any errors
    """
    health_status = {
        "status": "healthy",
        "region": region_name,
        "bedrock_client_initialized": False,
        "available_models": [],
        "model_count": 0,
        "errors": []
    }
    
    try:
        # Test boto3 client initialization
        logger.info(f"Initializing bedrock client for health check in region: {region_name}")
        bedrock_client = boto3.client(
            service_name="bedrock",
            region_name=region_name
        )
        health_status["bedrock_client_initialized"] = True
        logger.info("Bedrock client initialized successfully")
        
        # Test listing foundation models
        logger.info("Attempting to list foundation models")
        response = bedrock_client.list_foundation_models()
        
        model_summaries = response.get('modelSummaries', [])
        health_status["model_count"] = len(model_summaries)
        
        # Extract basic model information
        for model in model_summaries:
            health_status["available_models"].append({
                "modelId": model.get("modelId"),
                "modelName": model.get("modelName"),
                "providerName": model.get("providerName"),
                "inputModalities": model.get("inputModalities", []),
                "outputModalities": model.get("outputModalities", [])
            })
        
        logger.info(f"Successfully retrieved {len(model_summaries)} foundation models")
        
    except NoCredentialsError as e:
        error_msg = "No AWS credentials found"
        logger.error(f"NoCredentialsError in check_bedrock_health: {error_msg}")
        health_status["status"] = "unhealthy"
        health_status["errors"].append({
            "type": "NoCredentialsError",
            "message": error_msg,
            "details": "AWS credentials not configured. Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables or ~/.aws/credentials file."
        })
        
    except PartialCredentialsError as e:
        error_msg = f"Incomplete AWS credentials: {str(e)}"
        logger.error(f"PartialCredentialsError in check_bedrock_health: {error_msg}")
        health_status["status"] = "unhealthy"
        health_status["errors"].append({
            "type": "PartialCredentialsError",
            "message": error_msg,
            "details": str(e)
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        logger.error(
            f"ClientError in check_bedrock_health:\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Full Response: {e.response}"
        )
        health_status["status"] = "unhealthy"
        health_status["errors"].append({
            "type": "ClientError",
            "code": error_code,
            "message": error_message
        })
        
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(
            f"Unexpected exception in check_bedrock_health:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        health_status["status"] = "unhealthy"
        health_status["errors"].append({
            "type": error_type,
            "message": error_message
        })
    
    return health_status


def validate_model(model_id, region_name="us-east-1"):
    """
    Validate if a specific model ID is accessible.
    
    Args:
        model_id: The model identifier to validate
        region_name: AWS region name
        
    Returns:
        dict: Validation response with accessibility status and model details
    """
    validation_result = {
        "model_id": model_id,
        "accessible": False,
        "region": region_name,
        "model_details": None,
        "errors": []
    }
    
    try:
        logger.info(f"Validating model access for model_id: {model_id} in region: {region_name}")
        
        bedrock_client = boto3.client(
            service_name="bedrock",
            region_name=region_name
        )
        
        # Try to get the foundation model details
        response = bedrock_client.get_foundation_model(
            modelIdentifier=model_id
        )
        
        model_details = response.get('modelDetails', {})
        validation_result["accessible"] = True
        validation_result["model_details"] = {
            "modelId": model_details.get("modelId"),
            "modelArn": model_details.get("modelArn"),
            "modelName": model_details.get("modelName"),
            "providerName": model_details.get("providerName"),
            "inputModalities": model_details.get("inputModalities", []),
            "outputModalities": model_details.get("outputModalities", []),
            "responseStreamingSupported": model_details.get("responseStreamingSupported"),
            "customizationsSupported": model_details.get("customizationsSupported", []),
            "inferenceTypesSupported": model_details.get("inferenceTypesSupported", [])
        }
        
        logger.info(f"Model {model_id} is accessible")
        
    except NoCredentialsError as e:
        error_msg = "No AWS credentials found"
        logger.error(f"NoCredentialsError in validate_model: {error_msg}")
        validation_result["errors"].append({
            "type": "NoCredentialsError",
            "message": error_msg,
            "details": "AWS credentials not configured"
        })
        
    except PartialCredentialsError as e:
        error_msg = f"Incomplete AWS credentials: {str(e)}"
        logger.error(f"PartialCredentialsError in validate_model: {error_msg}")
        validation_result["errors"].append({
            "type": "PartialCredentialsError",
            "message": error_msg,
            "details": str(e)
        })
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"].get("Message", "Unknown error")
        logger.error(
            f"ClientError in validate_model:\n"
            f"  Error Code: {error_code}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}"
        )
        validation_result["errors"].append({
            "type": "ClientError",
            "code": error_code,
            "message": error_message
        })
        
        # Add specific guidance for common error codes
        if error_code == "ResourceNotFoundException":
            validation_result["errors"].append({
                "type": "Guidance",
                "message": f"Model '{model_id}' not found. It may not exist, not be available in region '{region_name}', or model access may not be enabled in AWS Bedrock."
            })
        elif error_code == "AccessDeniedException":
            validation_result["errors"].append({
                "type": "Guidance",
                "message": f"Access denied to model '{model_id}'. Check IAM permissions for bedrock:GetFoundationModel action."
            })
        
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(
            f"Unexpected exception in validate_model:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        validation_result["errors"].append({
            "type": error_type,
            "message": error_message
        })
    
    return validation_result
