from pydantic import BaseModel

class JewelImage(BaseModel):
    index: int
    image_id: str

class ComplianceRequest(BaseModel):
    total_jewel_count: int
    overall_image_id: str
    jewel_images: list[JewelImage]
