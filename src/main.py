from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, date
import uvicorn
import uuid
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database connection - using the container name as the host
# Replace "db" with your actual database container name
DATABASE_URL = "mysql+pymysql://vsuser:vspass@db:3306/hasaki"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class ProspectDB(Base):
    __tablename__ = "prospects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date_entered = Column(DateTime, default=datetime.utcnow)
    date_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_user_id = Column(String(36))
    created_by = Column(String(36))
    description = Column(Text)
    deleted = Column(Boolean, default=False)
    assigned_user_id = Column(String(36), index=True)
    salutation = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100), index=True)
    title = Column(String(100))
    photo = Column(String(255))
    department = Column(String(255))
    do_not_call = Column(Boolean, default=False)
    phone_home = Column(String(100))
    phone_mobile = Column(String(100))
    phone_work = Column(String(100))
    phone_other = Column(String(100))
    phone_fax = Column(String(100))
    lawful_basis = Column(Text)
    date_reviewed = Column(Date)
    lawful_basis_source = Column(String(100))
    primary_address_street = Column(String(150))
    primary_address_city = Column(String(100))
    primary_address_state = Column(String(100))
    primary_address_postalcode = Column(String(20))
    primary_address_country = Column(String(255))
    alt_address_street = Column(String(150))
    alt_address_city = Column(String(100))
    alt_address_state = Column(String(100))
    alt_address_postalcode = Column(String(20))
    alt_address_country = Column(String(255))
    assistant = Column(String(75))
    assistant_phone = Column(String(100))
    tracker_key = Column(Integer, autoincrement=True, nullable=False, index=True)
    birthdate = Column(Date)
    lead_id = Column(String(36))
    account_name = Column(String(150))
    campaign_id = Column(String(36))

# Pydantic models
class ProspectBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_user_id: Optional[str] = None
    salutation: Optional[str] = None
    photo: Optional[str] = None
    department: Optional[str] = None
    do_not_call: Optional[bool] = False
    phone_home: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_work: Optional[str] = None
    phone_other: Optional[str] = None
    phone_fax: Optional[str] = None
    lawful_basis: Optional[str] = None
    date_reviewed: Optional[date] = None
    lawful_basis_source: Optional[str] = None
    primary_address_street: Optional[str] = None
    primary_address_city: Optional[str] = None
    primary_address_state: Optional[str] = None
    primary_address_postalcode: Optional[str] = None
    primary_address_country: Optional[str] = None
    alt_address_street: Optional[str] = None
    alt_address_city: Optional[str] = None
    alt_address_state: Optional[str] = None
    alt_address_postalcode: Optional[str] = None
    alt_address_country: Optional[str] = None
    assistant: Optional[str] = None
    assistant_phone: Optional[str] = None
    birthdate: Optional[date] = None
    lead_id: Optional[str] = None
    account_name: Optional[str] = None
    campaign_id: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class ProspectResponse(ProspectBase):
    id: str
    date_entered: datetime
    date_modified: datetime
    tracker_key: int

    class Config:
        orm_mode = True

class BulkProspectCreate(BaseModel):
    prospects: List[ProspectCreate]
    created_by: Optional[str] = None
    modified_user_id: Optional[str] = None

class BulkProspectResponse(BaseModel):
    success: bool
    count: int
    created_ids: List[str]
    errors: Optional[List[Dict[str, Any]]] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Hasaki CRM API",
    description="API for Hasaki CRM system",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Hasaki CRM API"}

@app.post("/prospects/bulk", response_model=BulkProspectResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_prospects(data: BulkProspectCreate, db: Session = Depends(get_db)):
    """
    Create multiple prospects in bulk.

    This endpoint accepts a list of prospect data and inserts them into the database.
    """
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

@app.get("/health")
async def health_check():
    """Health check endpoint that also tests database connectivity"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8082, reload=True)
