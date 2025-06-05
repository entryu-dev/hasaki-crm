
from datetime import datetime
import uuid
import csv
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

from ..schemas import BulkProspectResponse, BulkProspectCreate
from ..models.prospects import Prospect

router = APIRouter()

DATABASE_URL = "mysql+pymysql://entryu:entryu@hasaki-mysql:3306/hasaki"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pspects  database model
router = APIRouter()

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
            prospect = Prospect(
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

@router.post("/prospects/bulk-csv", response_model=BulkProspectResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_prospects_csv(
    file: UploadFile = File(...),
    created_by: Optional[str] = None,
    modified_user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create multiple prospects in bulk from CSV file.

    Expected CSV columns:
    - first_name
    - last_name
    - email (optional)
    - phone_mobile (optional)
    - phone_work (optional)
    - company/account_name (optional)
    - title (optional)
    - department (optional)
    - primary_address_street (optional)
    - primary_address_city (optional)
    - primary_address_state (optional)
    - primary_address_postalcode (optional)
    - primary_address_country (optional)

    And other prospect fields as defined in the database schema.
    """

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    created_ids = []
    errors = []

    try:
        # Read CSV content
        content = await file.read()
        decoded_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_content))

        # Validate required columns
        required_columns = ['first_name', 'last_name']
        if not all(col in csv_reader.fieldnames for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain required columns: {required_columns}"
            )

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
            try:
                # Clean and validate row data
                prospect_data = {}

                # Map CSV columns to database fields
                column_mapping = {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'email': 'email',
                    'phone_mobile': 'phone_mobile',
                    'phone_work': 'phone_work',
                    'phone_home': 'phone_home',
                    'phone_other': 'phone_other',
                    'phone_fax': 'phone_fax',
                    'company': 'account_name',
                    'account_name': 'account_name',
                    'title': 'title',
                    'department': 'department',
                    'salutation': 'salutation',
                    'description': 'description',
                    'primary_address_street': 'primary_address_street',
                    'primary_address_city': 'primary_address_city',
                    'primary_address_state': 'primary_address_state',
                    'primary_address_postalcode': 'primary_address_postalcode',
                    'primary_address_country': 'primary_address_country',
                    'alt_address_street': 'alt_address_street',
                    'alt_address_city': 'alt_address_city',
                    'alt_address_state': 'alt_address_state',
                    'alt_address_postalcode': 'alt_address_postalcode',
                    'alt_address_country': 'alt_address_country',
                    'assistant': 'assistant',
                    'assistant_phone': 'assistant_phone',
                    'lead_id': 'lead_id',
                    'campaign_id': 'campaign_id'
                }

                # Extract and clean data from CSV row
                for csv_col, db_col in column_mapping.items():
                    if csv_col in row and row[csv_col]:
                        value = row[csv_col].strip()
                        if value:  # Only add non-empty values
                            prospect_data[db_col] = value

                # Validate required fields
                if not prospect_data.get('first_name') or not prospect_data.get('last_name'):
                    errors.append({
                        "row": row_num,
                        "message": "Missing required fields: first_name and last_name"
                    })
                    continue

                # Create prospect
                prospect = Prospect(
                    id=str(uuid.uuid4()),
                    date_entered=datetime.utcnow(),
                    date_modified=datetime.utcnow(),
                    created_by=created_by,
                    modified_user_id=modified_user_id,
                    **prospect_data
                )

                db.add(prospect)
                created_ids.append(prospect.id)

            except Exception as row_error:
                errors.append({
                    "row": row_num,
                    "message": f"Error processing row: {str(row_error)}"
                })
                continue

        # Commit all successful entries
        if created_ids:
            db.commit()

        return {
            "success": len(created_ids) > 0,
            "count": len(created_ids),
            "created_ids": created_ids,
            "errors": errors
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

    finally:
        await file.close()
