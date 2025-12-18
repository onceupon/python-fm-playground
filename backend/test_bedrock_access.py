#!/usr/bin/env python3
"""
Standalone test script to verify AWS Bedrock connectivity and model access.

This script performs comprehensive testing of:
1. AWS credentials availability
2. Access to anthropic.claude-3-5-sonnet-20241022-v2:0 model
3. Access to stability.stable-diffusion-xl model
4. Detailed error handling and diagnostics

Usage:
    python test_bedrock_access.py
"""

import boto3
import json
import sys
import traceback
from datetime import datetime
from botocore.exceptions import (
    ClientError, 
    NoCredentialsError, 
    PartialCredentialsError,
    BotoCoreError
)


class BedrockAccessTester:
    """Test AWS Bedrock connectivity and model access."""
    
    def __init__(self, region_name="us-east-1"):
        """
        Initialize the tester with AWS region.
        
        Args:
            region_name: AWS region to use (default: us-east-1)
        """
        self.region_name = region_name
        self.bedrock_runtime = None
        self.bedrock_client = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "region": region_name,
            "tests": []
        }
        
    def print_header(self, title):
        """Print a formatted section header."""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
        
    def print_subheader(self, title):
        """Print a formatted subsection header."""
        print(f"\n--- {title} ---")
        
    def record_test(self, test_name, passed, details):
        """Record test result."""
        self.test_results["tests"].append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        
    def test_aws_credentials(self):
        """Test AWS credentials availability and validity."""
        self.print_header("TEST 1: AWS Credentials Availability")
        
        try:
            # Try to get credentials from the default credential provider chain
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials is None:
                print("❌ FAILED: No AWS credentials found")
                print("\nCredentials can be configured via:")
                print("  - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
                print("  - ~/.aws/credentials file")
                print("  - IAM role (for EC2/ECS/Lambda)")
                print("  - AWS SSO")
                self.record_test("AWS Credentials", False, "No credentials found")
                return False
                
            # Check if credentials are frozen (which means they're available)
            frozen_creds = credentials.get_frozen_credentials()
            
            print("✅ PASSED: AWS credentials found")
            print(f"\nCredential Details:")
            print(f"  Access Key ID: {frozen_creds.access_key[:8]}..." if frozen_creds.access_key else "  Access Key ID: None")
            print(f"  Secret Access Key: {'*' * 20} (hidden)")
            print(f"  Session Token: {'Present' if frozen_creds.token else 'Not Present'}")
            
            # Get identity using STS
            try:
                sts = boto3.client('sts', region_name=self.region_name)
                identity = sts.get_caller_identity()
                print(f"\nAWS Identity:")
                print(f"  Account: {identity['Account']}")
                print(f"  User/Role ARN: {identity['Arn']}")
                print(f"  User ID: {identity['UserId']}")
                
                self.record_test("AWS Credentials", True, {
                    "account": identity['Account'],
                    "arn": identity['Arn'],
                    "has_session_token": frozen_creds.token is not None
                })
            except Exception as e:
                print(f"\n⚠️  WARNING: Could not retrieve AWS identity: {str(e)}")
                self.record_test("AWS Credentials", True, {
                    "warning": "Credentials found but could not verify identity",
                    "error": str(e)
                })
            
            return True
            
        except NoCredentialsError:
            print("❌ FAILED: No credentials found in any location")
            self.record_test("AWS Credentials", False, "NoCredentialsError")
            return False
        except PartialCredentialsError as e:
            print(f"❌ FAILED: Incomplete credentials - {str(e)}")
            self.record_test("AWS Credentials", False, f"PartialCredentialsError: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ FAILED: Unexpected error - {str(e)}")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            self.record_test("AWS Credentials", False, f"Exception: {str(e)}")
            return False
    
    def initialize_bedrock_clients(self):
        """Initialize Bedrock clients."""
        self.print_header("Initializing AWS Bedrock Clients")
        
        try:
            # Initialize bedrock-runtime client for model invocation
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.region_name
            )
            print(f"✅ Bedrock Runtime client initialized (region: {self.region_name})")
            
            # Initialize bedrock client for metadata operations
            self.bedrock_client = boto3.client(
                service_name="bedrock",
                region_name=self.region_name
            )
            print(f"✅ Bedrock client initialized (region: {self.region_name})")
            
            return True
        except Exception as e:
            print(f"❌ FAILED to initialize Bedrock clients: {str(e)}")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            return False
    
    def test_claude_model_access(self):
        """Test access to Claude 3.5 Sonnet model."""
        self.print_header("TEST 2: Claude 3.5 Sonnet Model Access")
        
        # Use the cross-region inference profile model ID
        model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        print(f"Testing model: {model_id}")
        
        try:
            # Prepare a simple test prompt
            prompt_config = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": "Say 'Hello from AWS Bedrock!' to confirm you are working."
                    }
                ]
            }
            
            print(f"\nSending test request...")
            print(f"Request payload:")
            print(json.dumps(prompt_config, indent=2))
            
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                body=json.dumps(prompt_config),
                modelId=model_id
            )
            
            # Parse response
            response_body = json.loads(response.get("body").read())
            
            print(f"\n✅ PASSED: Successfully invoked Claude model")
            print(f"\nResponse metadata:")
            print(f"  HTTP Status: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            print(f"  Request ID: {response.get('ResponseMetadata', {}).get('RequestId')}")
            
            print(f"\nResponse body structure:")
            print(f"  Role: {response_body.get('role')}")
            print(f"  Model: {response_body.get('model')}")
            print(f"  Stop Reason: {response_body.get('stop_reason')}")
            
            # Extract and display the completion
            if 'content' in response_body and len(response_body['content']) > 0:
                completion = response_body['content'][0]['text']
                print(f"\nModel response:")
                print(f"  {completion}")
                
                self.record_test("Claude Model Access", True, {
                    "model_id": model_id,
                    "response_length": len(completion),
                    "stop_reason": response_body.get('stop_reason'),
                    "usage": response_body.get('usage', {})
                })
            else:
                print(f"\n⚠️  WARNING: Response received but no content found")
                self.record_test("Claude Model Access", True, {
                    "model_id": model_id,
                    "warning": "No content in response"
                })
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            print(f"\n❌ FAILED: AWS ClientError")
            print(f"\nError Details:")
            print(f"  Error Code: {error_code}")
            print(f"  Error Message: {error_message}")
            print(f"  HTTP Status: {e.response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            
            # Provide specific guidance based on error code
            if error_code == 'AccessDeniedException':
                print(f"\n🔍 Diagnosis: Insufficient IAM permissions")
                print(f"  Required permission: bedrock:InvokeModel")
                print(f"  Resource ARN: arn:aws:bedrock:{self.region_name}::foundation-model/{model_id}")
            elif error_code == 'ResourceNotFoundException':
                print(f"\n🔍 Diagnosis: Model not found or not enabled")
                print(f"  - Verify model ID is correct: {model_id}")
                print(f"  - Check if model is available in region: {self.region_name}")
                print(f"  - Ensure model access is enabled in AWS Console > Bedrock > Model access")
            elif error_code == 'ValidationException':
                print(f"\n🔍 Diagnosis: Invalid request format")
                print(f"  - Check API payload format matches model requirements")
            elif error_code == 'ThrottlingException':
                print(f"\n🔍 Diagnosis: Rate limit exceeded")
                print(f"  - Too many requests to the model")
            
            self.record_test("Claude Model Access", False, {
                "model_id": model_id,
                "error_code": error_code,
                "error_message": error_message
            })
            return False
            
        except BotoCoreError as e:
            print(f"\n❌ FAILED: BotoCoreError - {str(e)}")
            print(f"\n🔍 Diagnosis: AWS SDK/connectivity issue")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            self.record_test("Claude Model Access", False, f"BotoCoreError: {str(e)}")
            return False
            
        except Exception as e:
            print(f"\n❌ FAILED: Unexpected error - {str(e)}")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            self.record_test("Claude Model Access", False, f"Exception: {str(e)}")
            return False
    
    def test_stable_diffusion_model_access(self):
        """Test access to Stable Diffusion XL model."""
        self.print_header("TEST 3: Stable Diffusion XL Model Access")
        
        model_id = "stability.stable-diffusion-xl-v1"
        
        print(f"Testing model: {model_id}")
        
        try:
            # Prepare a simple test prompt for image generation
            prompt_config = {
                "text_prompts": [
                    {
                        "text": "A simple red circle on white background"
                    }
                ],
                "cfg_scale": 7,
                "steps": 30,
                "seed": 42
            }
            
            print(f"\nSending test request...")
            print(f"Request payload:")
            print(json.dumps(prompt_config, indent=2))
            
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                body=json.dumps(prompt_config),
                modelId=model_id
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            
            print(f"\n✅ PASSED: Successfully invoked Stable Diffusion model")
            print(f"\nResponse metadata:")
            print(f"  HTTP Status: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            print(f"  Request ID: {response.get('ResponseMetadata', {}).get('RequestId')}")
            
            # Check artifacts in response
            if 'artifacts' in response_body and len(response_body['artifacts']) > 0:
                artifact = response_body['artifacts'][0]
                base64_image = artifact.get('base64', '')
                finish_reason = artifact.get('finishReason', 'N/A')
                
                print(f"\nResponse details:")
                print(f"  Artifacts count: {len(response_body['artifacts'])}")
                print(f"  Finish reason: {finish_reason}")
                print(f"  Image data length: {len(base64_image)} characters")
                print(f"  Estimated image size: ~{len(base64_image) * 3 // 4 // 1024} KB")
                
                self.record_test("Stable Diffusion Model Access", True, {
                    "model_id": model_id,
                    "artifacts_count": len(response_body['artifacts']),
                    "finish_reason": finish_reason,
                    "image_data_length": len(base64_image)
                })
            else:
                print(f"\n⚠️  WARNING: Response received but no artifacts found")
                self.record_test("Stable Diffusion Model Access", True, {
                    "model_id": model_id,
                    "warning": "No artifacts in response"
                })
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            print(f"\n❌ FAILED: AWS ClientError")
            print(f"\nError Details:")
            print(f"  Error Code: {error_code}")
            print(f"  Error Message: {error_message}")
            print(f"  HTTP Status: {e.response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            
            # Provide specific guidance based on error code
            if error_code == 'AccessDeniedException':
                print(f"\n🔍 Diagnosis: Insufficient IAM permissions")
                print(f"  Required permission: bedrock:InvokeModel")
                print(f"  Resource ARN: arn:aws:bedrock:{self.region_name}::foundation-model/{model_id}")
            elif error_code == 'ResourceNotFoundException':
                print(f"\n🔍 Diagnosis: Model not found or not enabled")
                print(f"  - Verify model ID is correct: {model_id}")
                print(f"  - Check if model is available in region: {self.region_name}")
                print(f"  - Ensure model access is enabled in AWS Console > Bedrock > Model access")
            elif error_code == 'ValidationException':
                print(f"\n🔍 Diagnosis: Invalid request format")
                print(f"  - Check API payload format matches model requirements")
            elif error_code == 'ThrottlingException':
                print(f"\n🔍 Diagnosis: Rate limit exceeded")
                print(f"  - Too many requests to the model")
            
            self.record_test("Stable Diffusion Model Access", False, {
                "model_id": model_id,
                "error_code": error_code,
                "error_message": error_message
            })
            return False
            
        except BotoCoreError as e:
            print(f"\n❌ FAILED: BotoCoreError - {str(e)}")
            print(f"\n🔍 Diagnosis: AWS SDK/connectivity issue")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            self.record_test("Stable Diffusion Model Access", False, f"BotoCoreError: {str(e)}")
            return False
            
        except Exception as e:
            print(f"\n❌ FAILED: Unexpected error - {str(e)}")
            print(f"\nStack trace:")
            print(traceback.format_exc())
            self.record_test("Stable Diffusion Model Access", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        self.print_header("TEST SUMMARY")
        
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(1 for test in self.test_results["tests"] if test["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTest Run Timestamp: {self.test_results['timestamp']}")
        print(f"AWS Region: {self.test_results['region']}")
        print(f"\nResults: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests PASSED! AWS Bedrock is properly configured.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) FAILED. Review the errors above.")
        
        print("\nDetailed Results:")
        for i, test in enumerate(self.test_results["tests"], 1):
            status = "✅ PASS" if test["passed"] else "❌ FAIL"
            print(f"  {i}. {test['name']}: {status}")
        
        # Save results to JSON file
        output_file = "bedrock_test_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all tests and return overall success status."""
        print("\n" + "=" * 80)
        print(" AWS BEDROCK ACCESS TEST SUITE")
        print("=" * 80)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Region: {self.region_name}")
        
        # Test 1: AWS Credentials
        creds_ok = self.test_aws_credentials()
        
        if not creds_ok:
            print("\n⚠️  Skipping remaining tests due to credential failure")
            self.print_summary()
            return False
        
        # Initialize clients
        if not self.initialize_bedrock_clients():
            print("\n⚠️  Skipping remaining tests due to client initialization failure")
            self.print_summary()
            return False
        
        # Test 2: Claude Model
        self.test_claude_model_access()
        
        # Test 3: Stable Diffusion Model
        self.test_stable_diffusion_model_access()
        
        # Print summary
        all_passed = self.print_summary()
        
        return all_passed


def main():
    """Main entry point."""
    # Allow region to be passed as command-line argument
    region = "us-east-1"
    if len(sys.argv) > 1:
        region = sys.argv[1]
        print(f"Using region from command line: {region}")
    
    tester = BedrockAccessTester(region_name=region)
    
    try:
        all_passed = tester.run_all_tests()
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error in test suite: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
