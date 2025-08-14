import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, DreamAnalysis, MoodRecord, CharacterTherapy, User
from typing import List, Optional

# Veritabanı dosya yolu
DB_PATH = os.getenv("DREAMMIND_DB_PATH", "dreammind.db")
DB_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy engine ve session
engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Veritabanını ve tabloları oluştur
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# User işlemleri
def get_user_by_username(username: str) -> Optional[User]:
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()

def add_user(username: str, hashed_password: str) -> User:
    session = SessionLocal()
    try:
        new_user = User(username=username, hashed_password=hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    finally:
        session.close()

# DreamAnalysis işlemleri
def add_dream_analysis(user_id: int, dream_text: str, analysis_result: str) -> None:
    session = SessionLocal()
    try:
        record = DreamAnalysis(user_id=user_id, dream_text=dream_text, analysis_result=analysis_result)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_dream_analyses(user_id: int, limit: int = 10) -> List[DreamAnalysis]:
    session = SessionLocal()
    try:
        return session.query(DreamAnalysis).filter(DreamAnalysis.user_id == user_id).order_by(DreamAnalysis.created_at.desc()).limit(limit).all()
    finally:
        session.close()

def delete_dream_analysis(record_id: int) -> None:
    session = SessionLocal()
    try:
        record = session.query(DreamAnalysis).filter(DreamAnalysis.id == record_id).first()
        if record:
            session.delete(record)
            session.commit()
    finally:
        session.close()

# MoodRecord işlemleri
def add_mood_record(user_id: int, mood: str, note: str = None) -> None:
    session = SessionLocal()
    try:
        record = MoodRecord(user_id=user_id, mood=mood, note=note)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_mood_records(user_id: int, limit: int = 30) -> list:
    session = SessionLocal()
    try:
        return session.query(MoodRecord).filter(MoodRecord.user_id == user_id).order_by(MoodRecord.created_at.desc()).limit(limit).all()
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
def add_character_therapy(user_id: int, character: str, user_input: str, ai_response: str) -> None:
    session = SessionLocal()
    try:
        record = CharacterTherapy(user_id=user_id, character=character, user_input=user_input, ai_response=ai_response)
        session.add(record)
        session.commit()
    finally:
        session.close()

def list_character_therapies(user_id: int, limit: int = 30) -> list:
    session = SessionLocal()
    try:
        return session.query(CharacterTherapy).filter(CharacterTherapy.user_id == user_id).order_by(CharacterTherapy.created_at.desc()).limit(limit).all()
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