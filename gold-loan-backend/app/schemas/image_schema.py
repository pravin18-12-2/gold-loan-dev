from pydantic import BaseModel

class UploadUrlRequest(BaseModel):
    image_type: str
    loan_id: str
