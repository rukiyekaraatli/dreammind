import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, DreamAnalysis, MoodRecord, CharacterTherapy
from typing import List

# Veritabanı dosya yolu
DB_PATH = os.getenv("DREAMMIND_DB_PATH", "dreammind.db")
DB_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy engine ve session
engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabloyu oluştur (ilk çalıştırmada)
Base.metadata.create_all(bind=engine)

def add_dream_analysis(dream_text: str, analysis_result: str) -> None:
    """
    Yeni bir rüya analizi kaydı ekler.
    """
    session = SessionLocal()
    try:
        record = DreamAnalysis(dream_text=dream_text, analysis_result=analysis_result)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_dream_analyses(limit: int = 10) -> List[DreamAnalysis]:
    """
    Son yapılan rüya analizlerini (varsayılan 10) döner.
    """
    session = SessionLocal()
    try:
        return session.query(DreamAnalysis).order_by(DreamAnalysis.created_at.desc()).limit(limit).all()
    finally:
        session.close()

def delete_dream_analysis(record_id: int) -> None:
    """
    Belirli bir rüya analizi kaydını siler.
    """
    session = SessionLocal()
    try:
        record = session.query(DreamAnalysis).filter(DreamAnalysis.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    finally:
        session.close()

# MoodRecord işlemleri
def add_mood_record(mood: str, note: str = None) -> None:
    session = SessionLocal()
    try:
        record = MoodRecord(mood=mood, note=note)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_mood_records(limit: int = 30) -> list:
    session = SessionLocal()
    try:
        return session.query(MoodRecord).order_by(MoodRecord.created_at.desc()).limit(limit).all()
    finally:
        session.close()

def delete_mood_record(record_id: int) -> None:
    session = SessionLocal()
    try:
        record = session.query(MoodRecord).filter(MoodRecord.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    finally:
        session.close()

# CharacterTherapy işlemleri
def add_character_therapy(character: str, user_input: str, ai_response: str) -> None:
    session = SessionLocal()
    try:
        record = CharacterTherapy(character=character, user_input=user_input, ai_response=ai_response)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_character_therapies(limit: int = 30) -> list:
    session = SessionLocal()
    try:
        return session.query(CharacterTherapy).order_by(CharacterTherapy.created_at.desc()).limit(limit).all()
    finally:
        session.close()

def delete_character_therapy(record_id: int) -> None:
    session = SessionLocal()
    try:
        record = session.query(CharacterTherapy).filter(CharacterTherapy.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    finally:
        session.close() 