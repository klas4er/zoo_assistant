import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models
from zoo_assistant.core_engine.db.models import Base, Animal, Observation, Measurement, Feeding, EntityConfig
from zoo_assistant.core_engine.db.database import engine, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with tables and sample data."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have data
        if db.query(Animal).count() > 0:
            logger.info("Database already contains data, skipping initialization")
            return
        
        logger.info("Adding sample data...")
        
        # Create sample animals
        animals = [
            Animal(name="Багира", species="Тигрица", age=5, enclosure="Вольер хищников №1"),
            Animal(name="Змей Горыныч", species="Питон", age=8, enclosure="Террариум №3"),
            Animal(name="Годзилла", species="Игуана", age=3, enclosure="Террариум №2"),
            Animal(name="Тортила", species="Черепаха", age=80, enclosure="Террариум №1")
        ]
        
        db.add_all(animals)
        db.flush()
        
        # Create sample observations
        observations = [
            Observation(
                animal_id=1,  # Багира
                observer="Иванов И.И.",
                behavior="спокойное",
                health_status="нормальное",
                notes="Наблюдение за тигрицей-багирой. Животное проявляет нормальную активность. Съело примерно 4 кг мяса из утренней порции. Температура воздуха 22 градуса. Поведение спокойное. После кормления легла отдыхать в тени. Состояние здоровья в норме.",
                temperature=22.0,
                humidity=60.0,
                timestamp=datetime.utcnow() - timedelta(days=1),
                audio_file="Наблюдение_1.mp3",
                transcription="Наблюдение за тигрицей-багирой. Животное проявляет нормальную активность. Съело примерно 4 кг мяса из утренней порции. Температура воздуха 22 градуса. Поведение спокойное. После кормления легла отдыхать в тени. Состояние здоровья в норме."
            ),
            Observation(
                animal_id=2,  # Змей Горыныч
                observer="Петров П.П.",
                behavior="переваривает",
                health_status="нормальное",
                notes="Питон Змей Горыныч. Длина 4 метра 30 сантиметров. Вес 42 килограмма. Температура 28 градусов. Вчера покормили, дали кролика весом 2,5 килограмма. Переваривает.",
                temperature=28.0,
                humidity=70.0,
                timestamp=datetime.utcnow() - timedelta(hours=5),
                audio_file="Наблюдение_10.mp3",
                transcription="Питон Змей Горыныч. Длина 4 метра 30 сантиметров. Вес 42 килограмма. Температура 28 градусов. Вчера покормили, дали кролика весом 2,5 килограмма. Переваривает."
            )
        ]
        
        db.add_all(observations)
        
        # Create sample measurements
        measurements = [
            Measurement(
                animal_id=1,  # Багира
                weight=150.0,
                length=2.5,
                height=0.9,
                temperature=37.5,
                timestamp=datetime.utcnow() - timedelta(days=1)
            ),
            Measurement(
                animal_id=2,  # Змей Горыныч
                weight=42.0,
                length=4.3,
                height=None,
                temperature=28.0,
                timestamp=datetime.utcnow() - timedelta(hours=5)
            ),
            Measurement(
                animal_id=3,  # Годзилла
                weight=6.3,
                length=1.65,
                height=0.3,
                temperature=35.0,
                timestamp=datetime.utcnow() - timedelta(hours=5)
            ),
            Measurement(
                animal_id=4,  # Тортила
                weight=95.0,
                length=0.78,
                height=0.3,
                temperature=26.0,
                timestamp=datetime.utcnow() - timedelta(hours=5)
            )
        ]
        
        db.add_all(measurements)
        
        # Create sample feedings
        feedings = [
            Feeding(
                animal_id=1,  # Багира
                food_type="мясо",
                quantity=4.0,
                timestamp=datetime.utcnow() - timedelta(days=1, hours=2),
                notes="Утреннее кормление"
            ),
            Feeding(
                animal_id=2,  # Змей Горыныч
                food_type="кролик",
                quantity=2.5,
                timestamp=datetime.utcnow() - timedelta(days=1),
                notes="Еженедельное кормление"
            ),
            Feeding(
                animal_id=3,  # Годзилла
                food_type="салат и фрукты",
                quantity=0.5,
                timestamp=datetime.utcnow() - timedelta(hours=6),
                notes="Утреннее кормление"
            ),
            Feeding(
                animal_id=4,  # Тортила
                food_type="трава и овощи",
                quantity=1.5,
                timestamp=datetime.utcnow() - timedelta(hours=6),
                notes="Утреннее кормление"
            )
        ]
        
        db.add_all(feedings)
        
        # Create entity configs
        entity_configs = [
            EntityConfig(entity_type="animal_species", is_active=True, priority=1),
            EntityConfig(entity_type="behavior", is_active=True, priority=2),
            EntityConfig(entity_type="health_status", is_active=True, priority=3),
            EntityConfig(entity_type="weight", is_active=True, priority=4),
            EntityConfig(entity_type="length", is_active=True, priority=5),
            EntityConfig(entity_type="temperature", is_active=True, priority=6),
            EntityConfig(entity_type="food", is_active=True, priority=7)
        ]
        
        db.add_all(entity_configs)
        
        # Commit all changes
        db.commit()
        logger.info("Sample data added successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()