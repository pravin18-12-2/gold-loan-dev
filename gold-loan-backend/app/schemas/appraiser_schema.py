from pydantic import BaseModel, EmailStr

class CreateAppraiserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    branch_id: str
    appraiser_code: str
    face_image_id: str
