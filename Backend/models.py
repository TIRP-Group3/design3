from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String) # Changed from hashed_password
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")

    datasets = relationship("Dataset", back_populates="owner")
    trained_models = relationship("TrainedModel", back_populates="owner")
    scan_history = relationship("ScanHistory", back_populates="user")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    file_path = Column(String)
    description = Column(String, nullable=True)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="datasets")
    trained_models = relationship("TrainedModel", back_populates="dataset")

class TrainedModel(Base):
    __tablename__ = "trained_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    model_path = Column(String)
    parameters = Column(JSON, nullable=True)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    accuracy = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="trained_models")
    dataset = relationship("Dataset", back_populates="trained_models")
    scan_history = relationship("ScanHistory", back_populates="model")

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    model_id = Column(Integer, ForeignKey("trained_models.id"))
    scan_date = Column(DateTime, default=datetime.datetime.utcnow)
    results = Column(JSON)
    is_threat_detected = Column(Boolean, default=False)

    user = relationship("User", back_populates="scan_history")
    model = relationship("TrainedModel", back_populates="scan_history")
    
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for system events
    username = Column(String, nullable=True) # Store username for quick display
    action_type = Column(String, index=True) # e.g., "dataset_uploaded", "model_training_started", "scan_completed"
    message = Column(String) # "Admin uploaded dataset 'XYZ'", "User ABC scanned file 'report.docx'"
    details = Column(JSON, nullable=True) # For extra context, e.g., {"dataset_id": 1, "model_id": 5}
    is_read = Column(Boolean, default=False)
