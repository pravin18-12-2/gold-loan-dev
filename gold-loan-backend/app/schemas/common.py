from datetime import datetime
from pydantic import BaseModel

class Meta(BaseModel):
    request_id: str
    timestamp: datetime
    version: str = 'v1'
