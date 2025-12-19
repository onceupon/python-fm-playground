import base64
import boto3
import json
import logging
import traceback

logger = logging.getLogger(__name__)

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

STYLES = [
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "digital-art",
    "enhance",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "modeling-compound",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
    "tile-texture"
]

def invoke(prompt, style_preset, model_id):
    try:
        logger.info(f"Invoking Bedrock for image with model_id: {model_id}")
        
        prompt_config = {
            "text_prompts": [ { "text": prompt } ],
            "cfg_scale": 20,
            "steps": 100
        }

        if style_preset in STYLES:
            prompt_config["style_preset"] = style_preset
            logger.debug(f"Using style_preset: {style_preset}")
        else:
            logger.debug(f"No style_preset applied (requested: {style_preset})")

        logger.debug(f"Bedrock invoke_model request payload - model_id: {model_id}, config: {json.dumps(prompt_config, indent=2)}")

        response = bedrock_runtime.invoke_model(
            body=json.dumps(prompt_config),
            modelId=model_id
        )

        logger.debug(f"Bedrock invoke_model raw response metadata: {response.get('ResponseMetadata')}")

        response_body = json.loads(response["body"].read())
        logger.debug(f"Bedrock invoke_model response - artifacts count: {len(response_body.get('artifacts', []))}")

        base64_str = response_body["artifacts"][0]["base64"]
        
        logger.info(f"Successfully completed Bedrock image invocation for model_id: {model_id}, image size: {len(base64_str)} chars")

        return base64_str
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Error in image service invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {prompt[:200]}...\n"
            f"  Style Preset: {style_preset}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        raise