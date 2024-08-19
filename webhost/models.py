from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()


class Request(Base):
    __tablename__ = "requests"

    id = Column(String, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="processing")
    result = Column(Text, nullable=True)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
