from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    bank_code: str
    branch_code: str

class FaceVerifyRequest(BaseModel):
    appraiser_id: str
    image_id: str
