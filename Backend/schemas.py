from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import datetime

# Dataset Schemas
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    file_path: str
    upload_date: datetime.datetime
    owner_id: int

    class Config:
        from_attributes = True

# TrainedModel Schemas
class TrainedModelBase(BaseModel):
    name: str
    # Parameters the model was (or will be) trained with.
    # Can be set at creation or updated after training.
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TrainedModelCreate(TrainedModelBase):
    dataset_id: int
    # Accuracy will be null until the model is trained and evaluated.
    # Model_path will be set after training and saving.


class TrainedModelUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    accuracy: Optional[float] = None
    model_path: Optional[str] = None


class TrainedModel(TrainedModelBase):
    id: int
    dataset_id: int
    model_path: Optional[str] = None # Path to the serialized trained model
    creation_date: datetime.datetime
    accuracy: Optional[float] = None # Populated after training and evaluation
    owner_id: int

    class Config:
        from_attributes = True

Dataset.model_rebuild()
TrainedModel.model_rebuild()

# ScanHistory Schemas
class ScanHistoryBase(BaseModel):
    file_name: str
    results: Optional[Dict[str, Any]] = None
    is_threat_detected: Optional[bool] = False

class ScanHistoryCreate(ScanHistoryBase):
    model_id: int

class ScanHistory(ScanHistoryBase):
    id: int
    user_id: int
    model_id: int
    scan_date: datetime.datetime

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    email: str
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class UserWithDetails(User):
    datasets: List[Dataset] = []
    trained_models: List[TrainedModel] = []
    scan_history: List[ScanHistory] = []

    class Config:
        from_attributes = True
        


class ActivityLogBase(BaseModel):
    action_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    username: Optional[str] = None # For display

class ActivityLogCreate(ActivityLogBase):
    user_id: Optional[int] = None

class ActivityLog(ActivityLogBase):
    id: int
    timestamp: datetime.datetime
    user_id: Optional[int] = None
    is_read: bool

class Config:
    from_attributes = True # Updated from orm_mode    

class MarkReadPayload(BaseModel):
    log_ids: List[int]

class ActivityLogMarkReadPayload(BaseModel):
    log_ids: List[int]

ScanHistory.model_rebuild()