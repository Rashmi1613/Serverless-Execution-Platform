from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create Database Engine
engine = create_engine("sqlite:///functions.db")

# Define Base
Base = declarative_base()

# Create Session
Session = sessionmaker(bind=engine)
session = Session()

