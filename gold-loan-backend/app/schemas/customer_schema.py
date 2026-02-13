from pydantic import BaseModel

class CreateCustomerRequest(BaseModel):
    customer_code: str
    name: str
    face_image_id: str
