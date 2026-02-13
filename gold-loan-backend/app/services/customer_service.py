from app.repositories.customer_repo import CustomerRepository

class CustomerService:
    def __init__(self):
        self.repo = CustomerRepository()

    def create(self, db, tenant_id, payload):
        return self.repo.create(db, tenant_id, payload)
