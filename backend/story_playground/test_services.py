import unittest
from unittest.mock import patch, MagicMock
from . import services

class TestStoryServices(unittest.TestCase):
    
    def test_generate_random_prompt(self):
        # Test with default parameters
        prompt = services.generate_random_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("medium-length story", prompt)
        self.assertIn("1 main character", prompt)
        
        # Test with custom parameters
        prompt = services.generate_random_prompt(
            theme="mystery", 
            genre="thriller", 
            characters=3, 
            length="short"
        )
        self.assertIsInstance(prompt, str)
        self.assertIn("mystery", prompt)
        self.assertIn("thriller", prompt)
        self.assertIn("3 main characters", prompt)
        self.assertIn("short story", prompt)
    
    @patch('boto3.client')
    def test_generate_story(self, mock_boto3_client):
        # Mock the bedrock_runtime client
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Mock the response from the API
        mock_response = {
            "body": MagicMock()
        }
        mock_response["body"].read.return_value = '{"content": [{"text": "Title: Test Story\\n\\nThis is a test story."}]}'
        mock_client.invoke_model.return_value = mock_response
        
        # Call the function with the mocked client
        title, story = services.generate_story()
        
        # Verify the results
        self.assertEqual(title, "Test Story")
        self.assertEqual(story, "This is a test story.")
        
        # Verify the API was called with the correct parameters
        mock_client.invoke_model.assert_called_once()
        args, kwargs = mock_client.invoke_model.call_args
        self.assertEqual(kwargs["modelId"], "anthropic.claude-3-5-sonnet-20240620-v1:0")
        
        # Verify the request body contains the expected fields
        import json
        body = json.loads(kwargs["body"])
        self.assertIn("anthropic_version", body)
        self.assertIn("max_tokens", body)
        self.assertIn("temperature", body)
        self.assertIn("messages", body)

if __name__ == '__main__':
    unittest.main()