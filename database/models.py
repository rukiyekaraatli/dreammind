from sqlalchemy import Column, Integer, Text, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DreamAnalysis(Base):
    """
    Kullanıcının rüya analizi kayıtlarını tutan tablo.
    """
    __tablename__ = "dream_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    dream_text = Column(Text, nullable=False)
    analysis_result = Column(Text, nullable=False)

class MoodRecord(Base):
    """
    Kullanıcının günlük ruh hali kayıtlarını tutan tablo.
    """
    __tablename__ = "mood_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mood = Column(String(32), nullable=False)
    note = Column(Text, nullable=True)

class CharacterTherapy(Base):
    """
    Karakter terapisi sohbet kayıtlarını tutan tablo.
    """
    __tablename__ = "character_therapy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    character = Column(String(64), nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False) 