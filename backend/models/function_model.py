from sqlalchemy import Column, Integer, String
from .database import Base  # Ensure the correct import

class FunctionMetadata(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    route = Column(String)
    language = Column(String)
    timeout = Column(Integer)

