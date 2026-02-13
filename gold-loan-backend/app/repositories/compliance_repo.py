from sqlalchemy.orm import Session
from app.models.compliance import RbiCompliance, RbiComplianceItem

class ComplianceRepository:
    def create(self, db: Session, tenant_id: str, loan_id: str, payload: dict):
        rec = RbiCompliance(
            tenant_id=tenant_id,
            loan_id=loan_id,
            total_jewel_count=payload['total_jewel_count'],
            overall_image_id=payload['overall_image_id'],
        )
        db.add(rec)
        db.flush()
        for item in payload['jewel_images']:
            db.add(RbiComplianceItem(
                tenant_id=tenant_id,
                compliance_id=rec.id,
                jewel_index=item['index'],
                jewel_image_id=item['image_id'],
            ))
        db.commit()
        return rec
