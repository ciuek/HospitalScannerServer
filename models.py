from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    age = Column(Integer, index=True)
    pesel = Column(String, index=True)
    medical_history = relationship("PatientHistory", backref="patient")


class PatientHistory(Base):
    __tablename__ = "patient_history"

    id = Column(Integer, primary_key=True)
    event_date = Column(DateTime, index=True)
    event_description = Column(String, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", name="fk_patient_history_patients"))
    doctor_id = Column(Integer, ForeignKey("users.id", name="fk_patient_history_users"))