from pydantic import BaseModel

class CreateLoanRequest(BaseModel):
    customer_id: str
    appraiser_id: str
    bank_id: str
    branch_id: str
