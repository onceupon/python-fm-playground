import boto3
import json
import logging
import traceback

logger = logging.getLogger(__name__)

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

def invoke(prompt, temperature, max_tokens):
    try:
        model_id = "ai21.j2-mid-v1"
        logger.info(f"Invoking Jurassic-2 model: {model_id}")
        
        prompt_config = {
            "prompt": prompt,
            "maxTokens": max_tokens,
            "temperature": temperature
        }

        logger.debug(
            f"Bedrock invoke_model request payload - model_id: {model_id}, "
            f"config: {json.dumps(prompt_config, indent=2)}"
        )

        response = bedrock_runtime.invoke_model(
            body=json.dumps(prompt_config),
            modelId=model_id
        )

        logger.debug(f"Bedrock invoke_model raw response metadata: {response.get('ResponseMetadata')}")

        response_body = json.loads(response.get("body").read())
        logger.debug(f"Bedrock invoke_model response body: {json.dumps(response_body, indent=2)}")

        completion = response_body["completions"][0]["data"]["text"]
        if completion.startswith("\n"):
            completion = completion[1:]
            logger.debug("Stripped leading newline from completion")

        logger.info(f"Successfully completed Jurassic-2 invocation, response length: {len(completion)} chars")
        
        return completion
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Error in Jurassic-2 invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Prompt: {prompt[:200]}...\n"
            f"  Temperature: {temperature}\n"
            f"  Max Tokens: {max_tokens}\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        raise
