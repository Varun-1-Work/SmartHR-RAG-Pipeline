# This is where you build the "Entry Point" for your application. FastAPI uses decorators (like @app.post) to define routes.

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware # 1. Import this
import shutil
import os
from processor import process_resume, screen_candidates, format_with_ai 
from typing import List

app = FastAPI()

# 2. Add this block to fix the "Failed to fetch" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

@app.get("/")
def home():
    return {"message": "Welcome to Smart HR Screener"}

@app.post("/upload-resumes/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        file_path = f"uploads/{file.filename}"
        
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Index in ChromaDB
        msg = process_resume(file_path, file.filename)
        results.append(msg)
        
    return {"status": "Success", "processed_files": results} 


@app.post("/search/")
def search_resumes(job_description: str):
    raw_match = screen_candidates(job_description)
    
    if raw_match is None:
        return {"best_matches": ["No suitable candidates found for this role."]}
    
    # If we found a good match, format it with AI
    formatted_resume = format_with_ai(raw_match)
    return {"best_matches": [formatted_resume]}

   