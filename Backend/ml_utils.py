import pandas as pd
import numpy as np # Ensure numpy is imported
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
import joblib
import os
from typing import Dict, Any, Tuple, Union, Optional, List
import json # For testing serializability if needed, not directly used in the helper

MODELS_DIR = "backend_app/data/trained_models"
os.makedirs(MODELS_DIR, exist_ok=True)

# --- Serialization Helper ---
def _serialize_value(value):
    """Helper to convert individual values to be JSON serializable."""
    if isinstance(value, type): # Handles <class 'numpy.float64'>, <class 'int'> etc.
        return str(value)
    elif isinstance(value, (np.integer, np.floating)): # Handles numpy scalar numbers
        return value.item() # Converts to Python native int/float
    elif isinstance(value, np.bool_): # Handles numpy bool
        return bool(value.item()) # Converts to Python native bool
    elif isinstance(value, np.ndarray): # Handles numpy arrays
        return value.tolist()
    elif callable(value) and not isinstance(v, (str, int, float, bool, list, dict, tuple, type(None))):
        # For other callables that are not basic types and not already handled as 'type'
        return f"callable:{value.__name__}" if hasattr(value, '__name__') else str(value)
    # Add more specific type handling if needed (e.g., for specific scikit-learn internal objects)
    # Basic check for common non-serializable types already handled.
    # If it's not one of the above, and not a basic JSON type, fallback to string.
    if not isinstance(value, (str, int, float, bool, list, dict, tuple, type(None))):
        try:
            # A quick check if it can be dumped, to avoid overly aggressive string conversion
            # This is a safeguard but might be slow for very complex dicts.
            # For most sklearn params, direct str() is usually fine if not covered above.
            json.dumps(value) # Will raise TypeError if not serializable
            return value
        except TypeError:
            return str(value) # Fallback to string representation
    return value # Assume it's already serializable

def serialize_params_dict(params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively serializes a dictionary of parameters."""
    if not isinstance(params_dict, dict): # Should always be a dict from get_params()
        return str(params_dict)

    serializable = {}
    for key, value in params_dict.items():
        if isinstance(value, dict):
            serializable[key] = serialize_params_dict(value) # Recursively serialize nested dicts
        elif isinstance(value, list):
            serializable[key] = [_serialize_value(item) for item in value] # Serialize items in a list
        else:
            serializable[key] = _serialize_value(value)
    return serializable

# --- Data Loading and Preprocessing Utilities ---
def load_and_preprocess_data(file_path: str, target_column_name: Optional[str] = None):
    # ... (implementation as before)
    try:
        data = pd.read_csv(file_path)
        if target_column_name:
            if target_column_name not in data.columns:
                raise ValueError(f"Target column '{target_column_name}' not found in dataset.")
            y = data[target_column_name]
            X = data.drop(columns=[target_column_name])
        else:
            y = data.iloc[:, -1]
            X = data.iloc[:, :-1]
        numerical_features = X.select_dtypes(include=np.number).columns.tolist()
        categorical_features = X.select_dtypes(exclude=np.number).columns.tolist()
        return X, y, numerical_features, categorical_features
    except Exception as e:
        print(f"Error loading or initially processing dataset from {file_path}: {e}")
        raise

def create_preprocessor(numerical_features: List[str], categorical_features: List[str]):
    # ... (implementation as before)
    transformers = []
    if numerical_features:
        transformers.append(('num', StandardScaler(), numerical_features))
    if categorical_features:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features))
    if not transformers: return "passthrough"
    return ColumnTransformer(transformers=transformers, remainder='passthrough')

# --- Model Persistence Utilities ---
def save_hybrid_model_components(
    preprocessor: Union[ColumnTransformer, str], # Can be "passthrough"
    kmeans_model: KMeans,
    svm_model: SVC,
    model_name: str
) -> str:
    # ... (implementation as before)
    model_path = os.path.join(MODELS_DIR, model_name)
    pipeline_components = {
        'preprocessor': preprocessor, 'kmeans': kmeans_model, 'svm': svm_model,
        'model_base_name': model_name.replace(".joblib", "")
    }
    try:
        joblib.dump(pipeline_components, model_path)
        print(f"Hybrid model components saved to {model_path}")
        return model_path
    except Exception as e:
        print(f"Error saving hybrid model to {model_path}: {e}")
        raise

def load_hybrid_model_components(model_path: str) -> Dict[str, Any]:
    # ... (implementation as before)
    try:
        if not os.path.exists(model_path): raise FileNotFoundError(f"Model file not found at {model_path}")
        pipeline_components = joblib.load(model_path)
        print(f"Hybrid model components loaded from {model_path}")
        if not all(k in pipeline_components for k in ['preprocessor', 'kmeans', 'svm']):
            raise ValueError("Loaded model file is missing required components.")
        return pipeline_components
    except Exception as e:
        print(f"Error loading hybrid model from {model_path}: {e}")
        raise

# --- Prediction Utility ---
def make_hybrid_prediction(
    data_input: pd.DataFrame, 
    loaded_components: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray]:
    # ... (implementation as before, ensure data_processed is dense numpy array)
    preprocessor = loaded_components['preprocessor']
    kmeans_model = loaded_components['kmeans']
    svm_model = loaded_components['svm']
    try:
        if isinstance(preprocessor, ColumnTransformer):
            data_processed = preprocessor.transform(data_input)
        else: # Passthrough or other
            data_processed = data_input.to_numpy() if isinstance(data_input, pd.DataFrame) else data_input
        
        cluster_labels = kmeans_model.predict(data_processed)
        data_augmented = np.concatenate((data_processed, cluster_labels.reshape(-1, 1)), axis=1)
        
        predictions = svm_model.predict(data_augmented)
        probabilities = svm_model.predict_proba(data_augmented)
        return predictions, probabilities
    except Exception as e:
        print(f"Error during hybrid prediction: {e}")
        raise

# --- Main Training Orchestrator ---
def full_hybrid_model_training_pipeline(
    dataset_file_path: str, model_name_prefix: str, kmeans_hyperparams: Dict[str, Any],
    svm_hyperparams: Dict[str, Any], target_column: Optional[str] = None,
    test_size: float = 0.2, random_state: int = 42
) -> Tuple[str, float, Dict[str, Any]]:
    print(f"Starting hybrid model training pipeline for dataset: {dataset_file_path}")
    try:
        X, y, numerical_features, categorical_features = load_and_preprocess_data(
            dataset_file_path, target_column_name=target_column
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=y if y is not None and pd.Series(y).nunique() > 1 else None
        )
        feature_preprocessor = create_preprocessor(numerical_features, categorical_features)
        
        if isinstance(feature_preprocessor, ColumnTransformer):
            X_train_processed = feature_preprocessor.fit_transform(X_train)
            X_test_processed = feature_preprocessor.transform(X_test)
        else: 
            X_train_processed = X_train.to_numpy() if isinstance(X_train, pd.DataFrame) else X_train
            X_test_processed = X_test.to_numpy() if isinstance(X_test, pd.DataFrame) else X_test
            print("Warning: Preprocessor is passthrough or not a ColumnTransformer.")

        kmeans = KMeans(**kmeans_hyperparams)
        train_cluster_labels = kmeans.fit_predict(X_train_processed)
        X_train_augmented = np.concatenate((X_train_processed, train_cluster_labels.reshape(-1, 1)), axis=1)

        svm = SVC(**svm_hyperparams)
        svm.fit(X_train_augmented, y_train)
        
        test_cluster_labels = kmeans.predict(X_test_processed)
        X_test_augmented = np.concatenate((X_test_processed, test_cluster_labels.reshape(-1, 1)), axis=1)
        y_pred_test = svm.predict(X_test_augmented)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        print(f"Hybrid Model Test Accuracy: {test_accuracy:.4f}")

        model_filename = f"{model_name_prefix.replace(' ', '_')}_hybrid.joblib"
        saved_model_path = save_hybrid_model_components(
            preprocessor=feature_preprocessor, kmeans_model=kmeans, svm_model=svm, model_name=model_filename
        )
        
        serializable_transformers_config = "passthrough" # Default if not ColumnTransformer
        if isinstance(feature_preprocessor, ColumnTransformer):
            serializable_transformers_config = []
            for name, trans_obj, columns in feature_preprocessor.transformers_:
                if trans_obj == 'drop' or trans_obj == 'passthrough':
                    serializable_transformers_config.append({
                        "name": name, "transformer": trans_obj, "columns": columns
                    })
                elif hasattr(trans_obj, 'get_params'):
                    serializable_transformers_config.append({
                        "name": name, "transformer_class": str(trans_obj.__class__.__name__),
                        "parameters": serialize_params_dict(trans_obj.get_params(deep=True)), # Use deep=True for full capture
                        "columns": columns
                    })
                else:
                    serializable_transformers_config.append({
                        "name": name, "transformer_obj_str": str(trans_obj), "columns": columns
                    })
            
        final_model_params = {
            "kmeans_params_used": serialize_params_dict(kmeans.get_params(deep=True)), # Use deep=True
            "svm_params_used": serialize_params_dict(svm.get_params(deep=True)),       # Use deep=True
            "preprocessing_details": {
                "numerical_features_identified": numerical_features,
                "categorical_features_identified": categorical_features,
                "transformers_applied_config": serializable_transformers_config
            },
            "target_column_used": target_column if target_column else "last_column_default",
            "dataset_source_file_path": dataset_file_path,
            "training_test_split_size": test_size,
            "training_random_state_for_split": random_state
        }
        return saved_model_path, test_accuracy, final_model_params
    except Exception as e:
        print(f"Error in full hybrid model training pipeline: {e}")
        import traceback
        traceback.print_exc()
        raise