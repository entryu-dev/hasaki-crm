
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Models
class Prospect(Base):
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
