from sqlalchemy import create_engine, Column, Integer, Text, DateTime, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config.settings import DATABASE_URL

# Create the SQLAlchemy engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CRRbiNotification(Base):
    __tablename__ = "cr_rbi_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    paragraph = Column(Text, nullable=True)
    pub_date = Column(DateTime, nullable=True)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
