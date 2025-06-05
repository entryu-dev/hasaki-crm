from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
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
