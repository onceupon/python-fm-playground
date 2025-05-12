import boto3
import json
import random

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

# List of story themes
THEMES = [
    "adventure", "mystery", "fantasy", "science fiction", "romance", 
    "horror", "historical", "comedy", "drama", "fairy tale"
]

# List of story genres
GENRES = [
    "action", "thriller", "dystopian", "utopian", "western", 
    "cyberpunk", "steampunk", "magical realism", "urban fantasy", "space opera"
]

def generate_random_prompt(theme=None, genre=None, characters=1, length="medium"):
    """Generate a random story prompt based on parameters"""
    
    # Use provided theme or select random one
    selected_theme = theme if theme else random.choice(THEMES)
    
    # Use provided genre or select random one
    selected_genre = genre if genre else random.choice(GENRES)
    
    # Determine story length based on parameter
    if length == "short":
        length_desc = "a short story (about 500 words)"
    elif length == "long":
        length_desc = "a longer story (about 2000 words)"
    else:  # medium
        length_desc = "a medium-length story (about 1000 words)"
    
    # Character count description
    char_desc = f"featuring {characters} main character{'s' if characters > 1 else ''}"
    
    # Construct the prompt
    prompt = f"Write {length_desc} in the {selected_genre} genre with a {selected_theme} theme, {char_desc}. Include a creative title at the beginning of your response in the format 'Title: [Your Title]'."
    
    return prompt

def generate_story(theme=None, genre=None, characters=1, length="medium", temperature=0.7, max_tokens=1000):
    """Generate a story using Claude 3.5 Sonnet"""
    
    # Generate the prompt
    prompt = generate_random_prompt(theme, genre, characters, length)
    
    # Prepare the request payload
    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Call the Bedrock API
    response = bedrock_runtime.invoke_model(
        body=json.dumps(prompt_config),
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0"
    )
    
    # Parse the response
    response_body = json.loads(response.get("body").read())
    story_text = response_body.get("content")[0]["text"]
    
    # Extract title from the story
    title_line = story_text.split('\n')[0]
    if title_line.startswith('Title:'):
        title = title_line.replace('Title:', '').strip()
        story = '\n'.join(story_text.split('\n')[1:]).strip()
    else:
        # If no title format is found, use a generic title
        title = "Untitled Story"
        story = story_text
    
    return title, story