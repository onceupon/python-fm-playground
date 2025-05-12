from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import models
from . import services

router = APIRouter()

@router.post("/story-playground/generate")
def generate_story(request: models.StoryRequest):
    try:
        title, story = services.generate_story(
            theme=request.theme,
            genre=request.genre,
            characters=request.characters,
            length=request.length,
            temperature=request.temperature,
            max_tokens=request.maxTokens
        )
        
        return models.StoryResponse(
            title=title,
            story=story
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            raise HTTPException(status_code=403, detail="Access denied to AWS Bedrock")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))