from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any 
import models, schemas


# User CRUD operations (no changes from previous simplified version)
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, password=user.password, role=user.role, is_admin=False)
    if user.role and user.role.lower() == "admin":
        db_user.is_admin = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"] is not None:
        db_user.password = update_data["password"]
        del update_data["password"]
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# Dataset CRUD operations (no changes)
def create_dataset(db: Session, dataset: schemas.DatasetCreate, file_path: str, owner_id: int):
    db_dataset = models.Dataset(**dataset.model_dump(), file_path=file_path, owner_id=owner_id)
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def get_dataset(db: Session, dataset_id: int):
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()

def get_datasets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Dataset).offset(skip).limit(limit).all()

def get_datasets_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Dataset).filter(models.Dataset.owner_id == owner_id).offset(skip).limit(limit).all()

def delete_dataset(db: Session, dataset_id: int):
    db_dataset = get_dataset(db, dataset_id)
    if not db_dataset:
        return None
    db.delete(db_dataset)
    db.commit()
    return db_dataset

# TrainedModel CRUD operations
def create_trained_model_entry(db: Session, model_to_create: schemas.TrainedModelCreate, owner_id: int):
    """
    Creates an initial database entry for a model that is about to be trained.
    model_path and accuracy will be null initially.
    """
    db_model = models.TrainedModel(
        name=model_to_create.name,
        dataset_id=model_to_create.dataset_id,
        parameters=model_to_create.parameters, # Store intended parameters
        owner_id=owner_id,
        model_path=None, # Will be updated after training
        accuracy=None    # Will be updated after training
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def update_trained_model_details(db: Session, model_id: int, model_update: schemas.TrainedModelUpdate):
    """
    Updates a trained model's details after training, typically path, actual parameters, and accuracy.
    """
    db_model = get_trained_model(db, model_id)
    if not db_model:
        return None
    
    update_data = model_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model

def get_trained_model(db: Session, model_id: int):
    return db.query(models.TrainedModel).filter(models.TrainedModel.id == model_id).first()

def get_trained_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TrainedModel).offset(skip).limit(limit).all()

def get_trained_models_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.TrainedModel).filter(models.TrainedModel.owner_id == owner_id).offset(skip).limit(limit).all()

def delete_trained_model(db: Session, model_id: int):
    db_model = get_trained_model(db, model_id)
    if not db_model:
        return None
    # Actual file deletion should be handled in the route or service layer
    db.delete(db_model)
    db.commit()
    return db_model

# ScanHistory CRUD operations (no changes)
def create_scan_history(db: Session, scan: schemas.ScanHistoryCreate, user_id: int):
    db_scan = models.ScanHistory(**scan.model_dump(), user_id=user_id)
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

def get_scan_history(db: Session, scan_id: int):
    return db.query(models.ScanHistory).filter(models.ScanHistory.id == scan_id).first()

def get_scan_histories_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ScanHistory).filter(models.ScanHistory.user_id == user_id).offset(skip).limit(limit).all()

def get_all_scan_histories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ScanHistory).offset(skip).limit(limit).all()
    
    
    
def create_activity_log(db: Session, activity: schemas.ActivityLogCreate):
    db_log = models.ActivityLog(
        user_id=activity.user_id,
        username=activity.username, # Fetch username if user_id is present or pass directly
        action_type=activity.action_type,
        message=activity.message,
        details=activity.details
    )
    # If user_id is provided and username isn't, try to fetch username
    if activity.user_id and not activity.username:
        user = get_user(db, activity.user_id)
        if user:
            db_log.username = user.email # Or a display name if you add one to User model

    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_activity_logs(db: Session, skip: int = 0, limit: int = 20, user_id: Optional[int] = None):
    query = db.query(models.ActivityLog)
    if user_id:
        query = query.filter(models.ActivityLog.user_id == user_id)
    return query.order_by(models.ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_unread_activity_logs_count(db: Session, user_id: Optional[int] = None):
    query = db.query(models.ActivityLog).filter(models.ActivityLog.is_read == False)
    if user_id:
        query = query.filter(models.ActivityLog.user_id == user_id)
    return query.count()

def mark_activity_logs_as_read(db: Session, log_ids: List[int], user_id: Optional[int] = None):
    query = db.query(models.ActivityLog).filter(models.ActivityLog.id.in_(log_ids))
    if user_id: # Ensure user can only mark their own logs as read, or admin can mark any
        # Add logic here if non-admin users should only mark their own.
        # For admin, user_id might be None to mark any.
        pass
    query.update({models.ActivityLog.is_read: True}, synchronize_session=False)
    db.commit()
    return query.count()

def mark_all_activity_logs_as_read_for_user(db: Session, user_id: Optional[int] = None):
    query = db.query(models.ActivityLog).filter(models.ActivityLog.is_read == False)
    if user_id:
         query = query.filter(models.ActivityLog.user_id == user_id)
    # For a general "mark all as read" by anyone viewing, remove user_id filter or handle permissions
    updated_count = query.update({models.ActivityLog.is_read: True}, synchronize_session=False)
    db.commit()
    return updated_count