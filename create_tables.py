import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine
from app.core.database import Base
from app.models.user import User, Student, Teacher, Admin

# Import the models to ensure they're registered with Base

# Get database URL from environment or use default
DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://root:password@localhost/newedu")

# Create engine
engine = create_engine(DATABASE_URL)

def create_tables():
    print(f"Creating tables using {DATABASE_URL}...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
