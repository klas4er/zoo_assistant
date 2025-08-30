from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# Association table for many-to-many relationships between animals
animal_relationships = Table(
    'animal_relationships',
    Base.metadata,
    Column('animal_id', Integer, ForeignKey('animals.id'), primary_key=True),
    Column('related_animal_id', Integer, ForeignKey('animals.id'), primary_key=True),
    Column('relationship_type', String(50)),
    Column('created_at', DateTime, default=datetime.datetime.utcnow)
)

class Animal(Base):
    __tablename__ = 'animals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    species = Column(String(100), nullable=False)
    age = Column(Float, nullable=True)
    enclosure = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    observations = relationship("Observation", back_populates="animal")
    measurements = relationship("Measurement", back_populates="animal")
    feedings = relationship("Feeding", back_populates="animal")
    
    def __repr__(self):
        return f"<Animal(name='{self.name}', species='{self.species}')>"

class Observation(Base):
    __tablename__ = 'observations'
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey('animals.id'))
    observer = Column(String(100), nullable=True)
    behavior = Column(String(100), nullable=True)
    health_status = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    temperature = Column(Float, nullable=True)  # Environmental temperature
    humidity = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    audio_file = Column(String(255), nullable=True)
    transcription = Column(Text, nullable=True)
    
    # Relationships
    animal = relationship("Animal", back_populates="observations")
    
    def __repr__(self):
        return f"<Observation(animal='{self.animal.name if self.animal else None}', timestamp='{self.timestamp}')>"

class Measurement(Base):
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey('animals.id'))
    weight = Column(Float, nullable=True)  # in kg
    length = Column(Float, nullable=True)  # in cm
    height = Column(Float, nullable=True)  # in cm
    temperature = Column(Float, nullable=True)  # Body temperature
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    animal = relationship("Animal", back_populates="measurements")
    
    def __repr__(self):
        return f"<Measurement(animal='{self.animal.name if self.animal else None}', weight='{self.weight}', timestamp='{self.timestamp}')>"

class Feeding(Base):
    __tablename__ = 'feedings'
    
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey('animals.id'))
    food_type = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)  # in kg
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    animal = relationship("Animal", back_populates="feedings")
    
    def __repr__(self):
        return f"<Feeding(animal='{self.animal.name if self.animal else None}', food='{self.food_type}', quantity='{self.quantity}')>"

class EntityConfig(Base):
    __tablename__ = 'entity_configs'
    
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<EntityConfig(type='{self.entity_type}', active='{self.is_active}')>"