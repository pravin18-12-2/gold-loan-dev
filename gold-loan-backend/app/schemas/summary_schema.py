from pydantic import BaseModel

class SummaryResponse(BaseModel):
    summary_id: str
