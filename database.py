from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()
engine = create_engine("sqlite:///shadow_password.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    _tablename_ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    gesture_embedding = Column(Text, nullable=False) # Encrypted
    voice_embedding = Column(Text, nullable=False)   # Encrypted
    trust_threshold = Column(Float, default=70.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SecurityLog(Base):
    _tablename_ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    trust_score = Column(Float, nullable=False)
    status = Column(String(20), nullable=False) # SUCCESS, FAILURE, INTRUSION
    gesture_score = Column(Float)
    voice_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    