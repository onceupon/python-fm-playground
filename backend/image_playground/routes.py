from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from . import models
from . import services

router = APIRouter()


@router.post("/foundation-models/model/image/{model_id}/invoke")
def invoke(body: models.ImageRequest, model_id: str):
    try:
        response = services.invoke(body.prompt, body.stylePreset, model_id)
        return {
            "imageByteArray": response
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "AccessDeniedException":
            raise HTTPException(status_code=403)
        else:
            raise HTTPException(status_code=500, detail=str(e.response["Error"]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
