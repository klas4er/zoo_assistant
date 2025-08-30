import os
import logging
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import json
from datetime import datetime

from .asr.speech_recognition import get_recognizer, TranscriptionResult
from .ner.entity_extraction import get_extractor
from .db.database import get_db
from .db.models import Animal, Observation, Measurement, Feeding

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioProcessingResult(BaseModel):
    audio_file: str
    transcription: str
    processing_time: float
    audio_duration: float
    entities: List[Dict[str, Any]]
    structured_data: Dict[str, Any]
    db_records: Dict[str, Any]

class ProcessingPipeline:
    def __init__(self):
        """Initialize the processing pipeline."""
        logger.info("Initializing processing pipeline")
        # These will be lazy-loaded when needed
        self._recognizer = None
        self._extractor = None
    
    @property
    def recognizer(self):
        """Lazy-load the speech recognizer."""
        if self._recognizer is None:
            self._recognizer = get_recognizer()
        return self._recognizer
    
    @property
    def extractor(self):
        """Lazy-load the entity extractor."""
        if self._extractor is None:
            self._extractor = get_extractor()
        return self._extractor
    
    def process_audio(self, audio_path: str) -> AudioProcessingResult:
        """Process an audio file through the entire pipeline."""
        start_time = time.time()
        
        # Step 1: Transcribe audio
        logger.info(f"Transcribing audio: {audio_path}")
        transcription_result = self.recognizer.process_audio(audio_path)
        transcription = transcription_result.text
        logger.info(f"Transcription completed in {transcription_result.processing_time:.2f}s")
        
        # Step 2: Extract entities
        logger.info("Extracting entities from transcription")
        entity_start_time = time.time()
        structured_data = self.extractor.extract_animal_info(transcription)
        entity_time = time.time() - entity_start_time
        logger.info(f"Entity extraction completed in {entity_time:.2f}s")
        
        # Step 3: Prepare database records
        db_records = self._prepare_db_records(structured_data, audio_path, transcription)
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f}s")
        
        return AudioProcessingResult(
            audio_file=audio_path,
            transcription=transcription,
            processing_time=total_time,
            audio_duration=transcription_result.audio_duration,
            entities=structured_data['entities'],
            structured_data=structured_data,
            db_records=db_records
        )
    
    def _prepare_db_records(self, structured_data: Dict[str, Any], audio_path: str, transcription: str) -> Dict[str, Any]:
        """Prepare database records from structured data."""
        # Extract relevant information
        animal_name = structured_data.get('name')
        animal_species = structured_data.get('species')
        
        # If we don't have a name or species, try to extract from the transcription
        if not animal_name or not animal_species:
            # Simple heuristic: look for "наблюдение за" pattern
            observation_pattern = "наблюдение за"
            if observation_pattern in transcription.lower():
                # Extract the text after "наблюдение за"
                start_idx = transcription.lower().find(observation_pattern) + len(observation_pattern)
                end_idx = transcription.find(".", start_idx)
                if end_idx == -1:
                    end_idx = transcription.find(",", start_idx)
                if end_idx == -1:
                    end_idx = len(transcription)
                
                animal_text = transcription[start_idx:end_idx].strip()
                # If we found something and don't have a species yet
                if animal_text and not animal_species:
                    animal_species = animal_text
        
        # Prepare animal record
        animal_record = {
            "name": animal_name or "Unknown",
            "species": animal_species or "Unknown"
        }
        
        # Prepare observation record
        observation_record = {
            "behavior": structured_data.get('behavior'),
            "health_status": structured_data.get('health_status'),
            "notes": transcription,
            "audio_file": os.path.basename(audio_path),
            "transcription": transcription,
            "temperature": structured_data.get('environment', {}).get('temperature'),
            "humidity": structured_data.get('environment', {}).get('humidity')
        }
        
        # Prepare measurement record if we have any measurements
        measurements = structured_data.get('measurements', {})
        measurement_record = None
        if any(measurements.values()):
            measurement_record = {
                "weight": measurements.get('weight'),
                "length": measurements.get('length'),
                "height": None,  # Not extracted yet
                "temperature": measurements.get('temperature')
            }
        
        # Prepare feeding record if we have feeding info
        feeding = structured_data.get('feeding', {})
        feeding_record = None
        if feeding.get('food_type') or feeding.get('quantity'):
            feeding_record = {
                "food_type": feeding.get('food_type', "Unknown"),
                "quantity": feeding.get('quantity'),
                "notes": None
            }
        
        return {
            "animal": animal_record,
            "observation": observation_record,
            "measurement": measurement_record,
            "feeding": feeding_record
        }
    
    def save_to_database(self, result: AudioProcessingResult):
        """Save processing results to the database."""
        db = next(get_db())
        try:
            # Check if animal exists
            animal_name = result.db_records['animal']['name']
            animal_species = result.db_records['animal']['species']
            
            animal = db.query(Animal).filter(
                Animal.name == animal_name,
                Animal.species == animal_species
            ).first()
            
            # Create animal if it doesn't exist
            if not animal:
                animal = Animal(
                    name=animal_name,
                    species=animal_species
                )
                db.add(animal)
                db.flush()  # To get the ID
            
            # Create observation
            observation_data = result.db_records['observation']
            observation = Observation(
                animal_id=animal.id,
                behavior=observation_data.get('behavior'),
                health_status=observation_data.get('health_status'),
                notes=observation_data.get('notes'),
                audio_file=observation_data.get('audio_file'),
                transcription=observation_data.get('transcription'),
                temperature=observation_data.get('temperature'),
                humidity=observation_data.get('humidity'),
                timestamp=datetime.utcnow()
            )
            db.add(observation)
            
            # Create measurement if available
            if result.db_records.get('measurement'):
                measurement_data = result.db_records['measurement']
                measurement = Measurement(
                    animal_id=animal.id,
                    weight=measurement_data.get('weight'),
                    length=measurement_data.get('length'),
                    height=measurement_data.get('height'),
                    temperature=measurement_data.get('temperature'),
                    timestamp=datetime.utcnow()
                )
                db.add(measurement)
            
            # Create feeding record if available
            if result.db_records.get('feeding'):
                feeding_data = result.db_records['feeding']
                feeding = Feeding(
                    animal_id=animal.id,
                    food_type=feeding_data.get('food_type'),
                    quantity=feeding_data.get('quantity'),
                    notes=feeding_data.get('notes'),
                    timestamp=datetime.utcnow()
                )
                db.add(feeding)
            
            # Commit all changes
            db.commit()
            logger.info(f"Successfully saved data for animal: {animal_name}")
            
            return {
                "animal_id": animal.id,
                "observation_id": observation.id
            }
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            raise
        finally:
            db.close()

# Singleton instance
_pipeline = None

def get_pipeline():
    """Get or create a singleton instance of the processing pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = ProcessingPipeline()
    return _pipeline