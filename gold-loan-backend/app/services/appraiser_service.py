from app.repositories.appraiser_repo import AppraiserRepository

class AppraiserService:
    def __init__(self):
        self.repo = AppraiserRepository()

    def create(self, db, tenant_id, payload):
        return self.repo.create(db, tenant_id, payload)

    def list(self, db, tenant_id):
        return self.repo.list(db, tenant_id)
