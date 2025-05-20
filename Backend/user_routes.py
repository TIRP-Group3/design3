from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated, Dict, Any # Ensure List, Optional, Dict, Any are imported
import pandas as pd
import numpy as np # Make sure numpy is imported
import os
import shutil
import datetime # Required for ScanHistory and ActivityLog timestamps

from . import crud, models, schemas, ml_utils # Relative imports for other backend modules
from .database import SessionLocal # For DB session

# Define a default test user ID for now, assuming admin is 1.
# In a real app with auth, this would come from the authenticated user.
# DEFAULT_TEST_USER_ID = 2 # Not strictly needed if user_id is passed to endpoints
# DEFAULT_TEST_USER_EMAIL = "testuser@example.com"

# The router instance for user-specific routes, named 'router'
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

# Directory for temporarily storing files uploaded for scanning
SCAN_UPLOADS_DIR = "backend_app/data/scan_uploads"
os.makedirs(SCAN_UPLOADS_DIR, exist_ok=True)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to get or create a test user (simplistic for demonstration)
# In a real system, user management would be more robust.
def get_or_create_test_user(db: Session, user_id: int, email: Optional[str] = None) -> models.User:
    user = crud.get_user(db, user_id=user_id)
    if not user:
        print(f"Test user (ID: {user_id}) not found. Creating...")
        user_email = email or f"user{user_id}@example.local"
        # Ensure the UserCreate schema matches its definition
        user = crud.create_user(db, schemas.UserCreate(email=user_email, password="testpassword", role="user"))
        # Check if the created user ID matches the requested one, especially if DB auto-increments
        if user.id != user_id:
             print(f"Warning: Created test user with ID {user.id} instead of intended {user_id}. This might happen with auto-incrementing IDs.")
             # If IDs must match, this logic would need to be rethought or DB managed differently for test users.
    elif email and user.email != email : # If ID exists but email is different, update for consistency
        user = crud.update_user(db, user_id, schemas.UserUpdate(email=email))
    return user

# --- User Scan Endpoint ---
@router.post("/scan/", response_model=schemas.ScanHistory)
async def scan_file_endpoint(
    model_id: Annotated[int, Form()],
    user_id: Annotated[int, Form()], # Frontend will send this user_id for now
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate User (or create a test user for demo purposes)
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        print(f"User ID {user_id} not found for scan. Attempting to use/create a test user.")
        db_user = get_or_create_test_user(db, user_id, f"user{user_id}_scan@example.com")
        if not db_user: # If still no user after trying to create
             raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found and could not be created.")

    # 2. Validate Model
    db_trained_model = crud.get_trained_model(db, model_id=model_id)
    if not db_trained_model or not db_trained_model.model_path:
        raise HTTPException(status_code=404, detail=f"Trained model with ID {model_id} not found or not ready for use.")

    # 3. File Type Check (Only CSVs for current ML pipeline)
    allowed_content_types = ["text/csv", "application/vnd.ms-excel", "application/csv"]
    file_content_type = file.content_type
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = [".csv"]

    if not (file_content_type in allowed_content_types or file_extension in allowed_extensions):
        error_message = f"File type '{file_content_type or file_extension}' is not supported by model ID {model_id}. Please upload a CSV file."
        print(f"Scan rejected for user {db_user.id}, file {file.filename}: {error_message}")
        # Log this rejection to ScanHistory
        scan_results_payload_error = {"summary": "File type not supported for this model.", "error": error_message}
        crud.create_scan_history(
            db=db,
            scan=schemas.ScanHistoryCreate(
                file_name=file.filename, model_id=model_id, results=scan_results_payload_error, is_threat_detected=False
            ), user_id=db_user.id
        )
        raise HTTPException(status_code=400, detail=error_message)
    
    # 4. Save uploaded file temporarily
    temp_file_path = os.path.join(SCAN_UPLOADS_DIR, f"user_{db_user.id}_model_{model_id}_scan_{datetime.datetime.utcnow().timestamp()}_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        if os.path.exists(temp_file_path): os.remove(temp_file_path) # Clean up if partial write
        raise HTTPException(status_code=500, detail=f"Could not save uploaded file for scanning: {e}")
    finally:
        file.file.close()

    scan_results_payload = {"summary": "Scan processing initiated.", "error": None}
    is_threat = False # Default

    try:
        # 5. Load ML Model Components
        loaded_components = ml_utils.load_hybrid_model_components(db_trained_model.model_path)
        
        # 6. Prepare Input Data for Prediction (Read CSV)
        try:
            input_df = pd.read_csv(temp_file_path)
        except Exception as e:
            raise ValueError(f"Failed to read or parse the uploaded CSV file: {e}. Ensure it's a valid CSV.")

        # 7. Make Prediction using the hybrid model utility
        predictions, probabilities = ml_utils.make_hybrid_prediction(input_df, loaded_components)
        
        # 8. Interpret Results and Format for ScanHistory
        num_threats = int(np.sum(predictions)) # Ensure it's a Python int
        is_threat = num_threats > 0
        
        positive_class_label = 1 # Assuming 1 is the threat class
        try:
            # Find the column index corresponding to the positive class probability
            positive_class_idx_in_proba = np.where(loaded_components['svm'].classes_ == positive_class_label)[0][0]
        except IndexError:
            print(f"Warning: Positive class label '{positive_class_label}' not found in SVM model classes: {loaded_components['svm'].classes_}. Probabilities for threats might be incorrect.")
            # Fallback: if positive class not found, cannot reliably get its probability.
            # This might indicate a model training issue or misconfiguration.
            positive_class_idx_in_proba = None # Or choose a default like 0 or 1 if only two classes.

        detailed_threat_info_list = []
        if is_threat:
            threat_indices = np.where(predictions == positive_class_label)[0]
            for i, item_idx in enumerate(threat_indices):
                if i < 5: # Limit details for brevity in results
                    prob_threat = 0.0
                    if positive_class_idx_in_proba is not None and probabilities.shape[1] > positive_class_idx_in_proba:
                        prob_threat = float(probabilities[item_idx][positive_class_idx_in_proba])
                    
                    detailed_threat_info_list.append({
                        "item_index_in_file": int(item_idx),
                        "probability_of_threat": round(prob_threat, 4)
                    })
                else:
                    break
        
        scan_results_payload = {
            "summary": f"Scan completed. {num_threats} potential threat(s) detected out of {len(predictions)} items processed.",
            "total_items_scanned": len(predictions),
            "threats_detected_count": num_threats,
            "is_overall_threat_detected": is_threat, # Redundant with num_threats > 0 but explicit
            # "raw_predictions": predictions.tolist(), # Optional: if frontend needs all predictions
            # "raw_probabilities": probabilities.tolist(), # Optional: if frontend needs all probabilities
            "detailed_threat_info_sample": detailed_threat_info_list 
        }
        print(f"Scan for user {db_user.id}, file {file.filename}, model {model_id}: {scan_results_payload['summary']}")

    except FileNotFoundError as e: 
        scan_results_payload = {"summary": "Scan failed: A required model file was not found.", "error": str(e)}
    except ValueError as e: 
        scan_results_payload = {"summary": "Scan failed: Data processing or input error.", "error": str(e)}
    except Exception as e:
        scan_results_payload = {"summary": "Scan failed due to an unexpected internal error.", "error": str(e)}
        print(f"Unexpected error during scan for user {db_user.id}, file {file.filename}:")
        import traceback
        traceback.print_exc() # Log full traceback for unexpected errors
    finally:
        # Clean up the temporarily saved uploaded file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # 9. Log to ScanHistory
    scan_history_entry = crud.create_scan_history(
        db=db,
        scan=schemas.ScanHistoryCreate(
            file_name=file.filename,
            model_id=model_id,
            results=scan_results_payload, # Store the detailed payload
            is_threat_detected=is_threat # Overall threat status
        ),
        user_id=db_user.id
    )

    # 10. Log to ActivityLog
    activity_message = f"User '{db_user.email}' scanned file '{file.filename}'. Result: {scan_results_payload['summary']}"
    crud.create_activity_log(db, schemas.ActivityLogCreate(
        user_id=db_user.id,
        username=db_user.email, 
        action_type="file_scanned",
        message=activity_message,
        details={
            "scan_history_id": scan_history_entry.id, "model_id": model_id, 
            "is_threat_overall": is_threat, "items_scanned": scan_results_payload.get("total_items_scanned")
        }
    ))

    return scan_history_entry


# --- User Notification Endpoints ---
@router.get("/notifications/", response_model=List[schemas.ActivityLog])
def get_user_notifications_endpoint(
    # In a real app, user_id would come from an auth token, not a query param for security.
    # For now, we require it as a query parameter for explicit testing.
    user_id: int, 
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        # To prevent users from just guessing IDs, in a real system this would be tied to auth.
        # For now, if the user ID doesn't exist, return empty or error.
        raise HTTPException(status_code=404, detail="User not found for notifications.")
    logs = crud.get_activity_logs(db, skip=skip, limit=limit, user_id=user_id)
    return logs

@router.get("/notifications/unread_count/", response_model=int)
def get_user_unread_notifications_count_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found for unread count.")
    return crud.get_unread_activity_logs_count(db, user_id=user_id)

@router.post("/notifications/mark_read/", response_model=dict)
def mark_user_notifications_as_read_endpoint(
    payload: schemas.ActivityLogMarkReadPayload, # Expects {"log_ids": [1,2,3]}
    user_id: int, # User ID to ensure they only mark their own (or admin overrides)
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Modify crud.mark_activity_logs_as_read to ensure it only marks logs belonging to user_id
    # if the caller is not an admin, or add specific logic here.
    # For now, crud.mark_activity_logs_as_read takes an optional user_id to filter which logs can be marked.
    updated_count = crud.mark_activity_logs_as_read(db, log_ids=payload.log_ids, user_id=user_id)
    if updated_count > 0:
        return {"message": f"{updated_count} notifications marked as read."}
    return {"message": "No notifications were updated (they might not belong to you or were already read)."}
            
@router.post("/notifications/mark_all_read/", response_model=dict)
def mark_all_my_notifications_as_read_endpoint(
    user_id: int, 
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    updated_count = crud.mark_all_activity_logs_as_read_for_user(db, user_id=user_id)
    return {"message": f"{updated_count} of your notifications marked as read."}