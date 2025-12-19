import boto3
import json
import logging
import traceback

logger = logging.getLogger(__name__)

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

def invoke(prompt, model_id):
    try:
        logger.info(f"Invoking Bedrock with model_id: {model_id}")

        systemPrompt = """
                        Take the role of a friendly chat bot. Your responses are brief.
                        You sometimes use emojis where appropriate, but you don't overdo it.
                        You engage human in a dialog by regularly asking questions,
                        except when Human indicates that the conversation is over.
                       """;

        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.8,
            "system": systemPrompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        logger.debug(f"Bedrock invoke_model request payload - model_id: {model_id}, config: {json.dumps(prompt_config, indent=2)}")

        response = bedrock_runtime.invoke_model(
            body=json.dumps(prompt_config),
            modelId=model_id
        )

        logger.debug(f"Bedrock invoke_model raw response metadata: {response.get('ResponseMetadata')}")
        
        response_body = json.loads(response.get("body").read())
        logger.debug(f"Bedrock invoke_model response body: {json.dumps(response_body, indent=2)}")

        completion = response_body['content'][0]['text']
        logger.info(f"Successfully completed Bedrock invocation for model_id: {model_id}")
        
        return completion
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        logger.error(
            f"Error in chat service invoke:\n"
            f"  Error Type: {error_type}\n"
            f"  Error Message: {error_message}\n"
            f"  Model ID: {model_id}\n"
            f"  Prompt: {prompt[:200]}...\n"
            f"  Stack Trace:\n{stack_trace}"
        )
        raise
