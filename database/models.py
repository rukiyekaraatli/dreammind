from sqlalchemy import Column, Integer, Text, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """
    Kullanıcı bilgilerini tutan tablo.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dream_analyses = relationship("DreamAnalysis", back_populates="user")
    mood_records = relationship("MoodRecord", back_populates="user")
    therapy_sessions = relationship("CharacterTherapy", back_populates="user")


class DreamAnalysis(Base):
    """
    Kullanıcının rüya analizi kayıtlarını tutan tablo.
    """
    __tablename__ = "dream_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    dream_text = Column(Text, nullable=False)
    analysis_result = Column(Text, nullable=False)

    # Relationship
    user = relationship("User", back_populates="dream_analyses")


class MoodRecord(Base):
    """
    Kullanıcının günlük ruh hali kayıtlarını tutan tablo.
    """
    __tablename__ = "mood_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    mood = Column(String(32), nullable=False)
    note = Column(Text, nullable=True)

    # Relationship
    user = relationship("User", back_populates="mood_records")


class CharacterTherapy(Base):
    """
    Karakter terapisi sohbet kayıtlarını tutan tablo.
    """
    __tablename__ = "character_therapy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    character = Column(String(64), nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    # Relationship
    user = relationship("User", back_populates="therapy_sessions")