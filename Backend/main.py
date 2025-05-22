from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database components
from database import engine, Base # SQLALCHEMY_DATABASE_URL, SessionLocal were also in database.py
import models # This ensures models are registered with Base

# Import routers
from admin_routes import router as admin_router
from user_routes import router as user_router 


# Create all database tables
# This will create tables defined in models.py if they don't already exist
# It's okay to call this at module level for simple apps; for complex apps, you might use Alembic migrations.
try:
    models.Base.metadata.create_all(bind=engine)
    print("Database tables checked/created successfully.")
except Exception as e:
    print(f"Error creating database tables: {e}")


app = FastAPI(
    title="Simple Web App API",
    description="API for managing datasets, training models, and scanning files.",
    version="0.1.0"
)

# CORS (Cross-Origin Resource Sharing) Middleware
# This is important to allow your React frontend (running on a different port)
# to communicate with the FastAPI backend.
origins = [
    "http://localhost:5175",  # Vite or React dev server
    "http://127.0.0.1:5175",  # Add this too if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True, # Allows cookies to be included in cross-origin requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)

# Include API routers
app.include_router(admin_router, prefix="/api/v1") # Prefixing all admin routes with /api/v1
app.include_router(user_router, prefix="/api/v1") # For when user routes are added

@app.get("/api/v1", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Simple Web App API"}

# To run this application, you would typically use Uvicorn:
# uvicorn backend_app.main:app --reload
# Ensure your terminal is in the 'webapp' directory (the parent of 'backend_app')