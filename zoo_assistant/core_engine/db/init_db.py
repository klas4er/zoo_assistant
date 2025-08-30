"""
Database initialization script
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .models import Base, Animal, Observation, Measurement, Feeding, EntityConfig
from .database import engine, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def create_entity_configs():
    """Create default entity extraction configurations."""
    db = SessionLocal()
    try:
        # Check if we already have entity configs
        if db.query(EntityConfig).count() > 0:
            logger.info("Entity configs already exist, skipping creation")
            return
        
        logger.info("Creating default entity configs...")
        
        # Create entity configs
        entity_configs = [
            EntityConfig(entity_type="animal_species", is_active=True, priority=1),
            EntityConfig(entity_type="behavior", is_active=True, priority=2),
            EntityConfig(entity_type="health_status", is_active=True, priority=3),
            EntityConfig(entity_type="weight", is_active=True, priority=4),
            EntityConfig(entity_type="length", is_active=True, priority=5),
            EntityConfig(entity_type="temperature", is_active=True, priority=6),
            EntityConfig(entity_type="food", is_active=True, priority=7),
            EntityConfig(entity_type="person", is_active=True, priority=8),
            EntityConfig(entity_type="location", is_active=True, priority=9),
            EntityConfig(entity_type="date", is_active=True, priority=10),
            EntityConfig(entity_type="time", is_active=True, priority=11),
            EntityConfig(entity_type="percentage", is_active=True, priority=12),
            EntityConfig(entity_type="age", is_active=True, priority=13)
        ]
        
        db.add_all(entity_configs)
        db.commit()
        logger.info("Default entity configs created successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating entity configs: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    create_entity_configs()