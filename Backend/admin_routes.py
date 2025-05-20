from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated, Dict, Any
import json
import os
import shutil
import datetime # Make sure datetime is imported if not already via other modules

from . import crud, models, schemas, ml_utils
from .database import SessionLocal

DEFAULT_ADMIN_OWNER_ID = 1 # Assuming User ID 1 is the designated admin

# --- Helper to get admin username (simplistic) ---
# This DEFINITION is fine at the module level
def get_admin_username(db: Session) -> str:
    admin_user = crud.get_user(db, DEFAULT_ADMIN_OWNER_ID)
    # Fallback to a generic name if user not found or doesn't have an email.
    # Ideally, ensure the admin user (ID 1) exists and has an email.
    return admin_user.email if admin_user and admin_user.email else "Admin"

DATASETS_DIR = "backend_app/data/datasets"
MODELS_DIR = "backend_app/data/trained_models"
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User Management Endpoints ---
@router.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)): # Renamed to avoid conflict with crud.create_user
    db_user_check = crud.get_user_by_email(db, email=user.email)
    if db_user_check:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = crud.create_user(db=db, user=user)
    
    # Log this admin action
    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID, # Action performed by admin
        username=admin_username_val,
        action_type="admin_created_user",
        message=f"Admin '{admin_username_val}' created user '{created_user.email}'.",
        details={"created_user_id": created_user.id, "created_user_role": created_user.role}
    ))
    return created_user

@router.get("/users/", response_model=List[schemas.User])
def read_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserWithDetails)
def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user_endpoint(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="admin_updated_user",
        message=f"Admin '{admin_username_val}' updated user ID {db_user.id} ('{db_user.email}').",
        details={"updated_user_id": db_user.id, "update_data": user_update.model_dump(exclude_unset=True)}
    ))
    return db_user

@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    # Ensure admin is not deleting themselves if ID 1 is protected, or handle appropriately
    # if user_id == DEFAULT_ADMIN_OWNER_ID:
    #     raise HTTPException(status_code=403, detail="Admin user cannot be deleted through this endpoint.")
        
    user_to_delete = crud.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
        
    deleted_user_email = user_to_delete.email # Get email before deleting

    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None: # Should not happen if get_user found it, but good check
        raise HTTPException(status_code=404, detail="User not found during deletion process.")

    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="admin_deleted_user",
        message=f"Admin '{admin_username_val}' deleted user ID {user_id} (formerly '{deleted_user_email}').",
        details={"deleted_user_id": user_id, "deleted_user_email": deleted_user_email}
    ))
    return db_user

# --- Dataset Management Endpoints ---
@router.post("/datasets/", response_model=schemas.Dataset)
async def upload_dataset_endpoint( # Corrected signature order from previous fix
    name: Annotated[str, Form()],
    description: Annotated[Optional[str], Form()] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Using DEFAULT_ADMIN_OWNER_ID defined at the module level
    owner = crud.get_user(db, user_id=DEFAULT_ADMIN_OWNER_ID)
    if not owner:
        # For simplicity, we'll raise an error if the default admin user isn't found.
        # A robust system would have a proper way to ensure this user exists or handle it.
        print(f"CRITICAL: Default admin user (ID: {DEFAULT_ADMIN_OWNER_ID}) not found. This user is required for operations.")
        raise HTTPException(status_code=500, detail=f"System misconfiguration: Default admin owner (ID: {DEFAULT_ADMIN_OWNER_ID}) not found.")

    safe_filename = "".join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in file.filename)
    file_path = os.path.join(DATASETS_DIR, safe_filename)
    counter = 1
    base, ext = os.path.splitext(file_path)
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
        
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save dataset file: {e}")
    finally:
        file.file.close()

    dataset_create_schema = schemas.DatasetCreate(name=name, description=description)
    db_dataset = crud.create_dataset(db=db, dataset=dataset_create_schema, file_path=file_path, owner_id=DEFAULT_ADMIN_OWNER_ID)

    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="dataset_uploaded",
        message=f"Admin '{admin_username_val}' uploaded dataset '{db_dataset.name}'.",
        details={"dataset_id": db_dataset.id, "file_path": db_dataset.file_path}
    ))
    return db_dataset

@router.get("/datasets/", response_model=List[schemas.Dataset])
def list_datasets_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    datasets = crud.get_datasets(db, skip=skip, limit=limit)
    return datasets

@router.get("/datasets/{dataset_id}", response_model=schemas.Dataset)
def read_dataset_endpoint(dataset_id: int, db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset

@router.delete("/datasets/{dataset_id}", response_model=schemas.Dataset)
def delete_dataset_endpoint(dataset_id: int, db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset_name_for_log = db_dataset.name
    dataset_path_for_log = db_dataset.file_path

    try:
        if db_dataset.file_path and os.path.exists(db_dataset.file_path):
            os.remove(db_dataset.file_path)
    except Exception as e:
        print(f"Error deleting dataset file {db_dataset.file_path}: {e}")
        # Log this file deletion error but proceed to delete DB record if desired
        # For now, we just print. An activity log for "file_delete_failed" could be added.

    deleted_dataset_from_db = crud.delete_dataset(db, dataset_id=dataset_id) # This returns the deleted object

    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="dataset_deleted",
        message=f"Admin '{admin_username_val}' deleted dataset '{dataset_name_for_log}' (ID: {dataset_id}).",
        details={"dataset_id": dataset_id, "deleted_file_path": dataset_path_for_log}
    ))
    return deleted_dataset_from_db # Return the object that was deleted


# --- Model Training and Management Endpoints ---
@router.post("/models/train/", response_model=schemas.TrainedModel)
async def train_hybrid_model_endpoint(
    name: Annotated[str, Form()],
    dataset_id: Annotated[int, Form()],
    target_column_name: Annotated[Optional[str], Form()] = None,
    kmeans_params_str: Annotated[str, Form(description='JSON string for K-Means: {"n_clusters": 3, "n_init": 10}')] = '{}',
    svm_params_str: Annotated[str, Form(description='JSON string for SVM: {"C": 1.0, "kernel": "rbf"}')] = '{}',
    test_size: Annotated[float, Form(ge=0.1, le=0.5)] = 0.2,
    random_state: Annotated[Optional[int], Form()] = 42,
    db: Session = Depends(get_db)
):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not db_dataset.file_path or not os.path.exists(db_dataset.file_path):
        raise HTTPException(status_code=400, detail="Dataset file path is missing or file does not exist.")

    owner = crud.get_user(db, user_id=DEFAULT_ADMIN_OWNER_ID) # Check if admin user exists
    if not owner:
        raise HTTPException(status_code=500, detail=f"System misconfiguration: Default admin owner (ID: {DEFAULT_ADMIN_OWNER_ID}) not found.")

    try:
        kmeans_params = json.loads(kmeans_params_str)
        svm_params = json.loads(svm_params_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON string for K-Means or SVM parameters.")

    # Apply defaults and ensure random_state/probability
    if not kmeans_params: kmeans_params = {"n_clusters": 3, "n_init": 10, "max_iter": 300}
    if "random_state" not in kmeans_params and random_state is not None: kmeans_params["random_state"] = random_state
    # Ensure n_init is an int if 'auto' might cause issues with specific sklearn version, default to 10
    if 'n_init' in kmeans_params and kmeans_params['n_init'] == 'auto': kmeans_params['n_init'] = 10


    if not svm_params: svm_params = {"C": 1.0, "kernel": "rbf", "gamma": "scale"}
    if "random_state" not in svm_params and random_state is not None: svm_params["random_state"] = random_state
    if "probability" not in svm_params: svm_params["probability"] = True

    model_create_schema = schemas.TrainedModelCreate(
        name=name,
        dataset_id=dataset_id,
        parameters={ 
            "kmeans_intended_params": kmeans_params.copy(), # Store a copy of intended params
            "svm_intended_params": svm_params.copy(),
            "target_column_name": target_column_name,
            "test_size": test_size,
            "random_state_for_split": random_state # The overall random state for split
        }
    )
    db_model_entry = crud.create_trained_model_entry(db=db, model_to_create=model_create_schema, owner_id=DEFAULT_ADMIN_OWNER_ID)

    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="model_training_started",
        message=f"Admin '{admin_username_val}' started training for model '{db_model_entry.name}'.",
        details={"model_id": db_model_entry.id, "dataset_id": db_dataset.id}
    ))

    try:
        model_name_prefix = f"model_{db_model_entry.id}_{name.replace(' ', '_')}"
        
        actual_model_path, achieved_accuracy, final_model_params = ml_utils.full_hybrid_model_training_pipeline(
            dataset_file_path=db_dataset.file_path,
            model_name_prefix=model_name_prefix,
            kmeans_hyperparams=kmeans_params, # These now include random_state
            svm_hyperparams=svm_params,       # These now include random_state and probability
            target_column=target_column_name,
            test_size=test_size,
            random_state=random_state # This is for train_test_split inside the pipeline
        )

        model_update_schema = schemas.TrainedModelUpdate(
            model_path=actual_model_path,
            accuracy=achieved_accuracy,
            parameters=final_model_params # These are the actual params from fitted model + pipeline info
        )
        updated_model = crud.update_trained_model_details(
            db=db, model_id=db_model_entry.id, model_update=model_update_schema
        )
        if not updated_model:
             raise HTTPException(status_code=500, detail="Failed to update model details after training.")

        crud.create_activity_log(db, schemas.ActivityLogCreate(
            user_id=DEFAULT_ADMIN_OWNER_ID,
            username=admin_username_val,
            action_type="model_training_succeeded",
            message=f"Model '{updated_model.name}' trained successfully. Accuracy: {updated_model.accuracy:.2f}",
            details={"model_id": updated_model.id, "accuracy": updated_model.accuracy, "model_path": actual_model_path}
        ))
        return updated_model

    except FileNotFoundError as e:
        err_msg = f"Dataset file not found during training: {e}"
    except ValueError as e:
        err_msg = f"Data processing or parameter error: {e}"
    except Exception as e:
        err_msg = f"Model training failed: {e}"
    
    # Common error handling for training pipeline exceptions
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="model_training_failed",
        message=f"Training failed for model intended as '{name}'. Reason: {err_msg[:150]}...",
        details={"dataset_id": dataset_id, "error_full": str(err_msg)}
    ))
    if db_model_entry: # If initial entry was made, try to delete it on failure
        crud.delete_trained_model(db, model_id=db_model_entry.id)
    print(f"Error during model training for '{name}': {err_msg}") # Log full error server-side
    raise HTTPException(status_code=500, detail=err_msg)


@router.get("/models/", response_model=List[schemas.TrainedModel])
def list_trained_models_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    models = crud.get_trained_models(db, skip=skip, limit=limit)
    return models

@router.get("/models/{model_id}", response_model=schemas.TrainedModel)
def read_trained_model_endpoint(model_id: int, db: Session = Depends(get_db)):
    db_model = crud.get_trained_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="Trained model not found")
    return db_model

@router.delete("/models/{model_id}", response_model=schemas.TrainedModel)
def delete_trained_model_endpoint(model_id: int, db: Session = Depends(get_db)):
    db_model = crud.get_trained_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=404, detail="Trained model not found")

    model_name_for_log = db_model.name
    model_path_for_log = db_model.model_path

    try:
        if db_model.model_path and os.path.exists(db_model.model_path):
            os.remove(db_model.model_path)
    except Exception as e:
        print(f"Error deleting model file {db_model.model_path}: {e}")

    deleted_model_from_db = crud.delete_trained_model(db, model_id=model_id)

    admin_username_val = get_admin_username(db)
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=DEFAULT_ADMIN_OWNER_ID,
        username=admin_username_val,
        action_type="model_deleted",
        message=f"Admin '{admin_username_val}' deleted model '{model_name_for_log}' (ID: {model_id}).",
        details={"model_id": model_id, "deleted_model_path": model_path_for_log}
    ))
    return deleted_model_from_db

# --- Notification / ActivityLog Endpoints ---
@router.get("/notifications/", response_model=List[schemas.ActivityLog])
def get_notifications_endpoint(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    logs = crud.get_activity_logs(db, skip=skip, limit=limit)
    return logs

@router.get("/notifications/unread_count/", response_model=int)
def get_unread_notifications_count_endpoint(db: Session = Depends(get_db)):
    return crud.get_unread_activity_logs_count(db)

@router.post("/notifications/mark_read/", response_model=dict)
def mark_notifications_as_read_endpoint(
    log_ids_payload: schemas.ActivityLogMarkReadPayload, # Assuming you create this schema
    # log_ids: List[int] = Body(..., embed=True), # Previous way: Body(embed=True) expects {"log_ids": [1,2,3]}
    db: Session = Depends(get_db)
):
    
    class LogIDsPayload(schemas.BaseModel): # Define inline for simplicity, or move to schemas.py
        log_ids: List[int]

    class MarkReadPayload(schemas.BaseModel):
        log_ids: List[int]

    # Re-defining endpoint to use this payload model properly
    payload: MarkReadPayload = Body(...), # This expects the JSON body {"log_ids": [1,2,3]}
    # The Body(...) without embed=True when used with a Pydantic model means the whole body is that model.

    updated_count = crud.mark_activity_logs_as_read(db, log_ids=payload.log_ids)
    if updated_count > 0:
        return {"message": f"{updated_count} notifications marked as read."}
    return {"message": "No notifications were updated or found."}


@router.post("/notifications/mark_all_read/", response_model=dict)
def mark_all_user_notifications_as_read_endpoint(db: Session = Depends(get_db)):
    updated_count = crud.mark_all_activity_logs_as_read_for_user(db)
    return {"message": f"{updated_count} notifications marked as read."}

# --- Scan History (Admin can view all) ---
@router.get("/scan-history/", response_model=List[schemas.ScanHistory])
def read_all_scan_history_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    history = crud.get_all_scan_histories(db, skip=skip, limit=limit)
    return history

# Add a new endpoint for fetching a single scan history detail for admin
@router.get("/scan-history/{scan_id}", response_model=schemas.ScanHistory)
def read_scan_history_detail_endpoint(scan_id: int, db: Session = Depends(get_db)):
    scan_entry = crud.get_scan_history(db, scan_id=scan_id)
    if scan_entry is None:
        raise HTTPException(status_code=404, detail="Scan history entry not found")
    return scan_entry