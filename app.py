from fastapi import FastAPI, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from pathlib import Path
from ultralytics import YOLO
import joblib
import numpy as np
import pandas as pd 
from pydantic import BaseModel 
from pymongo import MongoClient

# Initialize FastAPI
app = FastAPI()

# Serve Static Files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure templates directory exists
TEMPLATES_DIR = "templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Initialize Jinja2 template engine
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Load YOLO Model
model = YOLO(r"C:\Users\hp\OneDrive\Desktop\Project\Yolo_model\best.pt")

# Route to Serve Landing Page
@app.get("/", response_class=HTMLResponse)
async def serve_landing_page(request: Request):
    return templates.TemplateResponse("Landing_page.html", {"request": request})

# Route for the login page
@app.get("/login", response_class=HTMLResponse)
async def serve_login_page(request: Request):
    return templates.TemplateResponse("Login_form.html", {"request": request})

# For the inputs
@app.post("/login", response_class=HTMLResponse)
async def handle_login(username: str = Form(...), email: str = Form(...), user_id: str = Form(...), password: str = Form(...)):
    if username and email and user_id and password:
        return RedirectResponse(url="/risk", status_code=302)
    raise HTTPException(status_code=400, detail="Invalid input, please try again.")

# Route for the Risk page
@app.get("/risk", response_class=HTMLResponse)
async def serve_risk_page(request: Request):
    return templates.TemplateResponse("Risk.html", {"request": request})

#Route for the authorization form
@app.get("/autho_", response_class=HTMLResponse)
async def serve_autho_page(request: Request):
    return templates.TemplateResponse("autho_.html", {"request": request})

# Route For the crack detection using yolo
@app.get("/crack", response_class=HTMLResponse)
async def serve_crack_page(request: Request):
    return templates.TemplateResponse("crack.html", {"request": request})

# Route for the Analysis
@app.get("/trial", response_class=HTMLResponse)
async def serve_trial_page(request: Request):
    trial_page_path = os.path.join(TEMPLATES_DIR, "trial.html")
    if os.path.exists(trial_page_path):
        return FileResponse(trial_page_path)
    else:
        raise HTTPException(status_code=404, detail="Trial page not found")

# Risk Analyzer
# Load the trained models
XG_model = joblib.load("xgboost_model.joblib")
ct = joblib.load("column_transformer.joblib")
le = joblib.load("label_encoder.joblib")

# Define input schema
class PredictionInput(BaseModel):
    age: float
    traffic: float
    weather: str
    waterflow: float
    stress: float
    rainfall: float
    design: str
    humidity: float

XG_model = joblib.load("xgboost_model.joblib")
ct = joblib.load("column_transformer.joblib")
le = joblib.load("label_encoder.joblib")

# Define a Pydantic model for input validation
class PredictionInput(BaseModel):
    age: float
    traffic: float
    weather: str
    waterflow: float
    stress: float
    rainfall: float
    design: str
    humidity: float

@app.post("/predict")
async def predict_risk(data: PredictionInput):
    try:
        # Convert input data into DataFrame
        input_df = pd.DataFrame([data.dict()])

        # Apply transformations (ColumnTransformer)
        transformed_input = ct.transform(input_df)

        # Make a prediction
        prediction = XG_model.predict(transformed_input)

        # Decode the prediction
        status = le.inverse_transform(prediction)[0]

        return {"status": status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route for processing uploaded video
@app.post("/process_video")
async def process_video(video: UploadFile = File(...)):
    try:
        video_dir = Path("temp_video")
        video_dir.mkdir(parents=True, exist_ok=True)

        video_path = video_dir / video.filename
        
        # Save uploaded video
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Run YOLO inference
        results = model(str(video_path), save=True)

        # 🔹 Get YOLO save directory
        processed_video_folder = Path(results[0].save_dir)  # YOLO saves results here

        # 🔹 Check for any AVI file in the directory
        processed_videos = list(processed_video_folder.glob("*.avi"))

        if processed_videos:
            processed_video_path = processed_videos[0]  # Take the first processed AVI file
            return FileResponse(str(processed_video_path), media_type="video/x-msvideo",
                                headers={"Content-Disposition": f"attachment; filename={processed_video_path.name}"})
        
        # 🔹 If no AVI file found, check for YOLO output images
        processed_images = list(processed_video_folder.glob("*.jpg"))  # Change to PNG if needed
        if processed_images:
            processed_image_path = processed_images[0]  # Return the first processed image
            return FileResponse(str(processed_image_path), media_type="image/jpeg",
                                headers={"Content-Disposition": f"attachment; filename={processed_image_path.name}"})

        raise HTTPException(status_code=500, detail="Processed files not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# MongoDB Connection
client = MongoClient("mongodb+srv://manavpatil47:l8lzyL2tImYkSeUl@cluster0.wu94h.mongodb.net/")
db = client["bridge_sense"]  # Database name
collection = db["projects"]  # Collection name

# Serving the HTML form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("autho_.html", {"request": request})

# Handling form submission and storing data in MongoDB
@app.post("/submit-form")
async def submit_form(
    authorized_username: str = Form(...),
    email: str = Form(...),
    contractor_email: str = Form(...),
    bridge_name: str = Form(...),
    bridge_location: str = Form(...),
    year_of_construction: int = Form(...),
    steel_percentage: int = Form(...),
    concrete_percentage: int = Form(...),
    wood_percentage: int = Form(...),
    year_of_maintenance: int = Form(...),
):
    # MongoDB data insertion
    project_data = {
        "authorized_username": authorized_username,
        "email": email,
        "contractor_email": contractor_email,
        "bridge_name": bridge_name,
        "bridge_location": bridge_location,
        "year_of_construction": year_of_construction,
        "steel_percentage": steel_percentage,
        "concrete_percentage": concrete_percentage,
        "wood_percentage": wood_percentage,
        "year_of_maintenance": year_of_maintenance,
    }

    # Insert the project data into MongoDB
    collection.insert_one(project_data)

    # Return a success message or redirect as needed
    return {"message": "Form data submitted successfully"}