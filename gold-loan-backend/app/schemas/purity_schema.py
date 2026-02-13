from pydantic import BaseModel

class PurityTriggerResponse(BaseModel):
    job_id: str
    status: str
