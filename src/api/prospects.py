
from fastapi import APIRouter, Body, Depends, Path, Query, status
from ..schemas.prospects import BulkProspectResponse, BulkProspectCreate
router = APIRouter()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "mysql+pymysql://entryu:entryu@hasaki-mysql:3306/hasaki"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/prospects/bulk", response_model=BulkProspectResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_prospects(data: BulkProspectCreate, db: Session = Depends(get_db)):
    """
    Create multiple prospects in bulk.

    This endpoint accepts a list of prospect data and inserts them into the database.
    """
    print("database", DATABASE_URL)
    created_ids = []
    errors = []

    try:
        for prospect_data in data.prospects:
            # Create a DB model instance with the prospect data
            prospect = ProspectDB(
                id=str(uuid.uuid4()),
                date_entered=datetime.utcnow(),
                date_modified=datetime.utcnow(),
                created_by=data.created_by,
                modified_user_id=data.modified_user_id,
                **prospect_data.dict()
            )

            # Add to session
            db.add(prospect)
            created_ids.append(prospect.id)

        # Commit all changes at once
        db.commit()

        return {
            "success": True,
            "count": len(created_ids),
            "created_ids": created_ids,
            "errors": errors
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "count": 0,
            "created_ids": [],
            "errors": [{"message": str(e)}]
        }
