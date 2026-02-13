from datetime import datetime
from pydantic import BaseModel, EmailStr


class Meta(BaseModel):
    request_id: str
    timestamp: datetime
    version: str = "v1"


class ErrorInfo(BaseModel):
    code: str
    message: str


class EnvelopeSuccess(BaseModel):
    success: bool = True
    data: dict | list
    meta: Meta


class EnvelopeError(BaseModel):
    success: bool = False
    error: ErrorInfo
    meta: Meta


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    bank_code: str
    branch_code: str


class FaceVerifyRequest(BaseModel):
    appraiser_id: str
    image_id: str


class CreateAppraiserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    branch_id: str
    appraiser_code: str
    face_image_id: str


class CreateCustomerRequest(BaseModel):
    customer_code: str
    name: str
    face_image_id: str


class CreateLoanRequest(BaseModel):
    customer_id: str
    appraiser_id: str
    bank_id: str
    branch_id: str


class JewelImage(BaseModel):
    index: int
    image_id: str


class ComplianceRequest(BaseModel):
    total_jewel_count: int
    overall_image_id: str
    jewel_images: list[JewelImage]


class UploadUrlRequest(BaseModel):
    image_type: str
    loan_id: str
