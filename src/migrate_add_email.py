#!/usr/bin/env python3
"""
Database migration script to add email column to prospects table.
Run this script to update the database schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def add_email_column():
    """Add email column to prospects table if it doesn't exist."""

    # Database configuration
    DATABASE_URL = "mysql+pymysql://entryu:entryu@hasaki-mysql:3306/hasaki"

    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            # Check if email column already exists
            result = connection.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'hasaki'
                AND TABLE_NAME = 'prospects'
                AND COLUMN_NAME = 'email'
            """))

            column_exists = result.fetchone()[0] > 0

            if column_exists:
                print("✅ Email column already exists in prospects table.")
                return True

            # Add email column
            print("📧 Adding email column to prospects table...")
            connection.execute(text("""
                ALTER TABLE prospects
                ADD COLUMN email VARCHAR(100) AFTER last_name
            """))

            connection.commit()
            print("✅ Successfully added email column to prospects table.")
            return True

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Running database migration: Add email column to prospects table")
    success = add_email_column()

    if success:
        print("✨ Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)
