import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel

# Import our modules
from ...core_engine.processing_pipeline import get_pipeline
from ...core_engine.db.database import get_db
from ...core_engine.db.models import Animal, Observation, Measurement, Feeding, EntityConfig, Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Zoo Assistant API",
    description="API for processing and managing zoo animal observations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models for API
class EntityConfigModel(BaseModel):
    entity_type: str
    is_active: bool
    priority: int = 1

class AudioProcessRequest(BaseModel):
    file_path: str

class AudioProcessResponse(BaseModel):
    id: str
    status: str
    file_name: str
    transcription: Optional[str] = None
    processing_time: Optional[float] = None
    entities: Optional[List[Dict[str, Any]]] = None
    structured_data: Optional[Dict[str, Any]] = None

class ObservationResponse(BaseModel):
    id: int
    animal_id: int
    animal_name: str
    animal_species: str
    behavior: Optional[str] = None
    health_status: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime
    audio_file: Optional[str] = None
    transcription: Optional[str] = None

# Create upload directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for processing jobs
processing_jobs = {}

@app.get("/")
async def root():
    """Root endpoint to check if API is running."""
    return {"message": "Zoo Assistant API is running"}

@app.post("/api/audio/process", response_model=AudioProcessResponse)
async def process_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Process an audio file containing zoo observations."""
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create a job entry
    processing_jobs[job_id] = {
        "id": job_id,
        "status": "processing",
        "file_name": file.filename,
        "file_path": file_path,
        "start_time": datetime.utcnow()
    }
    
    # Process the audio in the background
    background_tasks.add_task(process_audio_task, job_id, file_path, db)
    
    return AudioProcessResponse(
        id=job_id,
        status="processing",
        file_name=file.filename
    )

async def process_audio_task(job_id: str, file_path: str, db: Session):
    """Background task to process audio."""
    try:
        # Get the processing pipeline
        pipeline = get_pipeline()
        
        # Process the audio
        result = pipeline.process_audio(file_path)
        
        # Save to database
        db_result = pipeline.save_to_database(result)
        
        # Update job status
        processing_jobs[job_id].update({
            "status": "completed",
            "transcription": result.transcription,
            "processing_time": result.processing_time,
            "entities": result.entities,
            "structured_data": result.structured_data,
            "db_records": db_result
        })
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        processing_jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/api/audio/status/{job_id}", response_model=AudioProcessResponse)
async def get_audio_status(job_id: str):
    """Get the status of an audio processing job."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    return AudioProcessResponse(
        id=job["id"],
        status=job["status"],
        file_name=job["file_name"],
        transcription=job.get("transcription"),
        processing_time=job.get("processing_time"),
        entities=job.get("entities"),
        structured_data=job.get("structured_data")
    )

@app.get("/api/transcriptions", response_model=List[ObservationResponse])
async def get_transcriptions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get a list of transcriptions."""
    observations = db.query(
        Observation, Animal.name, Animal.species
    ).join(
        Animal, Observation.animal_id == Animal.id
    ).order_by(
        Observation.timestamp.desc()
    ).offset(offset).limit(limit).all()
    
    return [
        ObservationResponse(
            id=obs.Observation.id,
            animal_id=obs.Observation.animal_id,
            animal_name=obs.name,
            animal_species=obs.species,
            behavior=obs.Observation.behavior,
            health_status=obs.Observation.health_status,
            notes=obs.Observation.notes,
            timestamp=obs.Observation.timestamp,
            audio_file=obs.Observation.audio_file,
            transcription=obs.Observation.transcription
        )
        for obs in observations
    ]

@app.get("/api/animals", response_model=List[Dict[str, Any]])
async def get_animals(db: Session = Depends(get_db)):
    """Get a list of all animals."""
    animals = db.query(Animal).all()
    return [
        {
            "id": animal.id,
            "name": animal.name,
            "species": animal.species,
            "age": animal.age,
            "enclosure": animal.enclosure
        }
        for animal in animals
    ]

@app.get("/api/animals/{animal_id}", response_model=Dict[str, Any])
async def get_animal(animal_id: int, db: Session = Depends(get_db)):
    """Get details for a specific animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Get the latest observation
    latest_observation = db.query(Observation).filter(
        Observation.animal_id == animal_id
    ).order_by(Observation.timestamp.desc()).first()
    
    # Get the latest measurement
    latest_measurement = db.query(Measurement).filter(
        Measurement.animal_id == animal_id
    ).order_by(Measurement.timestamp.desc()).first()
    
    # Get the latest feeding
    latest_feeding = db.query(Feeding).filter(
        Feeding.animal_id == animal_id
    ).order_by(Feeding.timestamp.desc()).first()
    
    return {
        "id": animal.id,
        "name": animal.name,
        "species": animal.species,
        "age": animal.age,
        "enclosure": animal.enclosure,
        "latest_observation": {
            "behavior": latest_observation.behavior if latest_observation else None,
            "health_status": latest_observation.health_status if latest_observation else None,
            "notes": latest_observation.notes if latest_observation else None,
            "timestamp": latest_observation.timestamp if latest_observation else None
        },
        "latest_measurement": {
            "weight": latest_measurement.weight if latest_measurement else None,
            "length": latest_measurement.length if latest_measurement else None,
            "height": latest_measurement.height if latest_measurement else None,
            "temperature": latest_measurement.temperature if latest_measurement else None,
            "timestamp": latest_measurement.timestamp if latest_measurement else None
        },
        "latest_feeding": {
            "food_type": latest_feeding.food_type if latest_feeding else None,
            "quantity": latest_feeding.quantity if latest_feeding else None,
            "timestamp": latest_feeding.timestamp if latest_feeding else None
        }
    }

@app.get("/api/animals/{animal_id}/log", response_model=List[Dict[str, Any]])
async def get_animal_log(
    animal_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get observation log for a specific animal."""
    # Check if animal exists
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Get observations
    observations = db.query(Observation).filter(
        Observation.animal_id == animal_id
    ).order_by(Observation.timestamp.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": obs.id,
            "behavior": obs.behavior,
            "health_status": obs.health_status,
            "notes": obs.notes,
            "timestamp": obs.timestamp,
            "audio_file": obs.audio_file,
            "transcription": obs.transcription
        }
        for obs in observations
    ]

@app.get("/api/reports/daily", response_model=Dict[str, Any])
async def get_daily_report(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get a daily report of observations."""
    # Parse date or use today
    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        report_date = datetime.utcnow().date()
    
    # Get start and end of the day
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = datetime.combine(report_date, datetime.max.time())
    
    # Get observations for the day
    observations = db.query(
        Observation, Animal.name, Animal.species
    ).join(
        Animal, Observation.animal_id == Animal.id
    ).filter(
        Observation.timestamp >= start_date,
        Observation.timestamp <= end_date
    ).order_by(Observation.timestamp).all()
    
    # Get measurements for the day
    measurements = db.query(
        Measurement, Animal.name, Animal.species
    ).join(
        Animal, Measurement.animal_id == Animal.id
    ).filter(
        Measurement.timestamp >= start_date,
        Measurement.timestamp <= end_date
    ).order_by(Measurement.timestamp).all()
    
    # Get feedings for the day
    feedings = db.query(
        Feeding, Animal.name, Animal.species
    ).join(
        Animal, Feeding.animal_id == Animal.id
    ).filter(
        Feeding.timestamp >= start_date,
        Feeding.timestamp <= end_date
    ).order_by(Feeding.timestamp).all()
    
    return {
        "date": report_date.isoformat(),
        "observations_count": len(observations),
        "observations": [
            {
                "id": obs.Observation.id,
                "animal_name": obs.name,
                "animal_species": obs.species,
                "behavior": obs.Observation.behavior,
                "health_status": obs.Observation.health_status,
                "timestamp": obs.Observation.timestamp
            }
            for obs in observations
        ],
        "measurements_count": len(measurements),
        "measurements": [
            {
                "id": m.Measurement.id,
                "animal_name": m.name,
                "animal_species": m.species,
                "weight": m.Measurement.weight,
                "length": m.Measurement.length,
                "temperature": m.Measurement.temperature,
                "timestamp": m.Measurement.timestamp
            }
            for m in measurements
        ],
        "feedings_count": len(feedings),
        "feedings": [
            {
                "id": f.Feeding.id,
                "animal_name": f.name,
                "animal_species": f.species,
                "food_type": f.Feeding.food_type,
                "quantity": f.Feeding.quantity,
                "timestamp": f.Feeding.timestamp
            }
            for f in feedings
        ]
    }

@app.get("/api/entities/config", response_model=List[EntityConfigModel])
async def get_entity_configs(db: Session = Depends(get_db)):
    """Get entity extraction configurations."""
    configs = db.query(EntityConfig).all()
    return [
        EntityConfigModel(
            entity_type=config.entity_type,
            is_active=config.is_active,
            priority=config.priority
        )
        for config in configs
    ]

@app.post("/api/entities/config", response_model=EntityConfigModel)
async def update_entity_config(
    config: EntityConfigModel,
    db: Session = Depends(get_db)
):
    """Update entity extraction configuration."""
    # Check if config exists
    db_config = db.query(EntityConfig).filter(
        EntityConfig.entity_type == config.entity_type
    ).first()
    
    if db_config:
        # Update existing config
        db_config.is_active = config.is_active
        db_config.priority = config.priority
    else:
        # Create new config
        db_config = EntityConfig(
            entity_type=config.entity_type,
            is_active=config.is_active,
            priority=config.priority
        )
        db.add(db_config)
    
    db.commit()
    db.refresh(db_config)
    
    return EntityConfigModel(
        entity_type=db_config.entity_type,
        is_active=db_config.is_active,
        priority=db_config.priority
    )