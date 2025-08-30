# Zoo Assistant - Comprehensive Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Frontend Interface](#frontend-interface)
8. [Core Engine](#core-engine)
9. [Database Schema](#database-schema)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Usage](#advanced-usage)

## Introduction

Zoo Assistant is an AI-powered system designed to help zookeepers convert voice observations into structured data. The system uses speech recognition and natural language processing to extract relevant information about animals, their behavior, health status, measurements, and feeding details.

### Key Features

- **Speech-to-Text**: Convert audio recordings of zookeeper observations into text
- **Entity Extraction**: Automatically extract structured data from transcriptions
- **Data Management**: Store and organize animal observations, measurements, and feeding records
- **Web Interface**: User-friendly interface for uploading audio, viewing results, and generating reports
- **API**: RESTful API for integration with other systems

### Use Cases

- **Field Observations**: Zookeepers can record observations while working with animals
- **Health Monitoring**: Track animal health status and behavior over time
- **Feeding Management**: Record and analyze animal feeding patterns
- **Measurement Tracking**: Monitor animal growth and physical parameters
- **Reporting**: Generate daily and periodic reports for management

## System Architecture

Zoo Assistant follows a modular architecture with the following components:

### Backend

- **API Layer**: FastAPI-based REST API for handling requests
- **Core Engine**: Processing pipeline for audio transcription and entity extraction
- **Database Layer**: SQLAlchemy ORM for data persistence

### Frontend

- **Web Interface**: HTML, CSS, and JavaScript interface
- **Components**: Upload form, observation list, animal cards, and reports

### Data Flow

1. User uploads audio recording through the web interface
2. Backend processes the audio using the core engine
3. Speech is transcribed to text
4. Entities are extracted from the text
5. Structured data is stored in the database
6. Results are returned to the user

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Git (for cloning the repository)

### Method 1: Using the Installation Script

1. Clone the repository:
   ```
   git clone https://github.com/your-username/zoo-assistant.git
   cd zoo-assistant/zoo_assistant
   ```

2. Run the installation script:
   ```
   chmod +x install.sh
   ./install.sh
   ```

3. Start the server:
   ```
   source venv/bin/activate
   python server.py
   ```

### Method 2: Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/zoo-assistant.git
   cd zoo-assistant/zoo_assistant
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements_minimal.txt
   ```

4. Download the Vosk model:
   ```
   mkdir -p core_engine/asr/models
   cd core_engine/asr/models
   wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
   unzip vosk-model-small-ru-0.22.zip
   mv vosk-model-small-ru-0.22 vosk-model-ru
   cd ../../..
   ```

5. Create data directories:
   ```
   mkdir -p data/uploads
   ```

6. Initialize the database:
   ```
   python init_db.py
   ```

7. Start the server:
   ```
   python server.py
   ```

### Method 3: Using Docker

1. Clone the repository:
   ```
   git clone https://github.com/your-username/zoo-assistant.git
   cd zoo-assistant/zoo_assistant
   ```

2. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

## Configuration

### Environment Variables

Zoo Assistant can be configured using environment variables or a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./zoo_assistant.db` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `False` |
| `UPLOAD_DIR` | Directory for uploaded files | `data/uploads` |
| `MODEL_DIR` | Directory for ASR model | `core_engine/asr/models/vosk-model-ru` |
| `MAX_AUDIO_SIZE` | Maximum audio file size in bytes | `50000000` (50MB) |
| `ALLOWED_AUDIO_TYPES` | Comma-separated list of allowed audio MIME types | `audio/mpeg,audio/mp3,audio/wav,audio/ogg` |

### Database Configuration

By default, Zoo Assistant uses SQLite for simplicity. For production use, you can configure PostgreSQL:

1. Uncomment the PostgreSQL section in `docker-compose.yml`
2. Set `DATABASE_URL` to `postgresql://postgres:postgres@db:5379/zoo_assistant`

### Asynchronous Processing

For better performance with many users, you can enable asynchronous processing:

1. Uncomment the Redis and Celery sections in `docker-compose.yml`
2. Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` environment variables

## Usage

### Starting the Server

Run the following command to start the server:

```
python server.py
```

The server will start at http://localhost:8000

### Using the Web Interface

1. Open your browser and navigate to http://localhost:8000
2. Use the "Upload Audio" tab to upload and process audio recordings
3. View processed observations in the "Observations" tab
4. Browse animals in the "Animals" tab
5. Generate reports in the "Reports" tab

### Upload Audio

1. Click on "Upload Audio" in the navigation menu
2. Drag and drop an audio file or click "Select File"
3. Click "Process Recording" to start processing
4. Wait for the processing to complete
5. View the transcription and extracted data

### View Observations

1. Click on "Observations" in the navigation menu
2. Browse the list of observations
3. Use the search box to filter observations
4. Click "View" to see details of a specific observation
5. Click "Play" to listen to the original audio recording

### View Animals

1. Click on "Animals" in the navigation menu
2. Browse the grid of animal cards
3. Use the search box to filter animals
4. Click on an animal card to view details

### Generate Reports

1. Click on "Reports" in the navigation menu
2. Select a date using the date picker
3. View the daily report with observations, measurements, and feedings
4. Click "Export" to download the report

## API Reference

### Authentication

*Note: Authentication is not implemented in the current version.*

### Endpoints

#### Audio Processing

- `POST /api/audio/process`: Upload and process an audio file
  - Request: `multipart/form-data` with `file` field
  - Response: `{ "id": "job_id", "status": "processing", "file_name": "filename.mp3" }`

- `GET /api/audio/status/{job_id}`: Check the status of an audio processing job
  - Response: `{ "id": "job_id", "status": "completed|processing|failed", "transcription": "...", "processing_time": 1.23, "entities": [...], "structured_data": {...} }`

#### Data Retrieval

- `GET /api/transcriptions`: Get a list of transcriptions
  - Query Parameters:
    - `limit`: Maximum number of results (default: 10)
    - `offset`: Offset for pagination (default: 0)
  - Response: Array of transcription objects

- `GET /api/animals`: Get a list of all animals
  - Response: Array of animal objects

- `GET /api/animals/{animal_id}`: Get details for a specific animal
  - Response: Animal object with latest observation, measurement, and feeding

- `GET /api/animals/{animal_id}/log`: Get observation log for a specific animal
  - Query Parameters:
    - `limit`: Maximum number of results (default: 10)
    - `offset`: Offset for pagination (default: 0)
  - Response: Array of observation objects

- `GET /api/reports/daily`: Get a daily report of observations
  - Query Parameters:
    - `date`: Report date in YYYY-MM-DD format (default: today)
  - Response: Report object with observations, measurements, and feedings

#### Configuration

- `GET /api/entities/config`: Get entity extraction configurations
  - Response: Array of entity config objects

- `POST /api/entities/config`: Update entity extraction configuration
  - Request: `{ "entity_type": "animal_species", "is_active": true, "priority": 1 }`
  - Response: Updated entity config object

### Response Objects

#### Observation

```json
{
  "id": 1,
  "animal_id": 1,
  "animal_name": "Багира",
  "animal_species": "Тигрица",
  "behavior": "спокойное",
  "health_status": "нормальное",
  "notes": "Наблюдение за тигрицей-багирой...",
  "timestamp": "2023-09-01T12:34:56",
  "audio_file": "observation_1.mp3",
  "transcription": "Наблюдение за тигрицей-багирой..."
}
```

#### Animal

```json
{
  "id": 1,
  "name": "Багира",
  "species": "Тигрица",
  "age": 5,
  "enclosure": "Вольер хищников №1",
  "latest_observation": {
    "behavior": "спокойное",
    "health_status": "нормальное",
    "notes": "Наблюдение за тигрицей-багирой...",
    "timestamp": "2023-09-01T12:34:56"
  },
  "latest_measurement": {
    "weight": 150.0,
    "length": 2.5,
    "height": 0.9,
    "temperature": 37.5,
    "timestamp": "2023-09-01T12:34:56"
  },
  "latest_feeding": {
    "food_type": "мясо",
    "quantity": 4.0,
    "timestamp": "2023-09-01T10:34:56"
  }
}
```

#### Entity Config

```json
{
  "entity_type": "animal_species",
  "is_active": true,
  "priority": 1
}
```

#### Daily Report

```json
{
  "date": "2023-09-01",
  "observations_count": 5,
  "observations": [...],
  "measurements_count": 3,
  "measurements": [...],
  "feedings_count": 4,
  "feedings": [...]
}
```

## Frontend Interface

### Pages

#### Upload Audio

- Audio file upload form
- Audio preview player
- Processing status indicator
- Transcription display
- Extracted data display

#### Observations

- List of observations with filters
- Search functionality
- Pagination
- Observation details view
- Audio playback

#### Animals

- Grid of animal cards
- Search functionality
- Animal details view
- Observation history

#### Reports

- Date selection
- Summary statistics
- Detailed tables for observations, measurements, and feedings
- Export functionality

### Components

- Navigation menu
- Search box
- Pagination controls
- Audio player
- Status indicators
- Data tables
- Animal cards

## Core Engine

### Speech Recognition

Zoo Assistant uses Vosk for speech recognition, which is optimized for CPU usage:

- **Model**: Small Russian model (vosk-model-small-ru-0.22)
- **Features**:
  - Offline processing (no internet required)
  - Fast transcription on CPU
  - Support for Russian language
  - Word timestamps and confidence scores

### Entity Extraction

Entity extraction is performed using Natasha, a Russian NLP library:

- **Components**:
  - Segmenter: Splits text into sentences and tokens
  - Morph Tagger: Performs morphological analysis
  - NER Tagger: Extracts named entities
  - Syntax Parser: Analyzes syntactic structure

- **Custom Rules**: Additional rules for zoo-specific entities:
  - Animal species
  - Behavior patterns
  - Health statuses
  - Measurements (weight, length, temperature)
  - Food types and quantities

### Processing Pipeline

1. **Audio Processing**:
   - Convert audio to WAV format if needed
   - Transcribe speech to text
   - Calculate processing metrics

2. **Entity Extraction**:
   - Extract named entities using Natasha
   - Extract custom entities using rules
   - Extract numeric values and units

3. **Structured Data Creation**:
   - Organize entities into structured format
   - Resolve references and relationships
   - Normalize values and units

4. **Database Storage**:
   - Create or update animal records
   - Store observations with metadata
   - Store measurements and feeding records

## Database Schema

### Tables

#### animals

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Animal name |
| species | String | Animal species |
| age | Float | Animal age in years |
| enclosure | String | Enclosure location |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record update timestamp |

#### observations

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| animal_id | Integer | Foreign key to animals |
| observer | String | Observer name |
| behavior | String | Observed behavior |
| health_status | String | Health status |
| notes | Text | Observation notes |
| temperature | Float | Environmental temperature |
| humidity | Float | Environmental humidity |
| timestamp | DateTime | Observation timestamp |
| audio_file | String | Audio file path |
| transcription | Text | Transcription text |

#### measurements

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| animal_id | Integer | Foreign key to animals |
| weight | Float | Weight in kg |
| length | Float | Length in m |
| height | Float | Height in m |
| temperature | Float | Body temperature |
| timestamp | DateTime | Measurement timestamp |

#### feedings

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| animal_id | Integer | Foreign key to animals |
| food_type | String | Type of food |
| quantity | Float | Quantity in kg |
| timestamp | DateTime | Feeding timestamp |
| notes | Text | Feeding notes |

#### entity_configs

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| entity_type | String | Entity type name |
| is_active | Boolean | Whether extraction is active |
| priority | Integer | Extraction priority |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record update timestamp |

### Relationships

- One animal has many observations (one-to-many)
- One animal has many measurements (one-to-many)
- One animal has many feedings (one-to-many)
- Animals can have relationships with other animals (many-to-many)

## Performance Optimization

Zoo Assistant is optimized for CPU-only environments:

### Speech Recognition Optimization

- **Model Selection**: Using the small Vosk model instead of larger models
- **Audio Preprocessing**: Converting to optimal format before processing
- **Chunked Processing**: Processing audio in chunks to reduce memory usage
- **Caching**: Caching model in memory for faster subsequent processing

### Entity Extraction Optimization

- **Rule-Based Extraction**: Using efficient rule-based extraction where possible
- **Selective Processing**: Only running necessary NLP components
- **Batched Processing**: Processing multiple entities in batches
- **Preloaded Models**: Keeping models in memory for faster processing

### API Optimization

- **Asynchronous Processing**: Using background tasks for long-running operations
- **Connection Pooling**: Reusing database connections
- **Response Caching**: Caching frequent API responses
- **Pagination**: Limiting result sets for better performance

### Database Optimization

- **Indexing**: Creating indexes on frequently queried columns
- **Query Optimization**: Writing efficient queries
- **Connection Pooling**: Reusing database connections
- **Lazy Loading**: Loading related objects only when needed

## Troubleshooting

### Common Issues

#### Audio Processing Fails

- **Check FFmpeg**: Ensure FFmpeg is installed and in the PATH
- **Check Audio Format**: Ensure the audio file is in a supported format
- **Check File Size**: Ensure the audio file is not too large
- **Check Logs**: Check the server logs for specific errors

#### Entity Extraction Issues

- **Check Language**: Ensure the audio is in Russian
- **Check Transcription**: Verify the transcription is correct
- **Check Entity Config**: Ensure the entity type is active
- **Adjust Rules**: Modify extraction rules if needed

#### Database Issues

- **Check Connection**: Ensure the database connection is correct
- **Check Permissions**: Ensure the database user has proper permissions
- **Check Disk Space**: Ensure there is enough disk space
- **Check Logs**: Check the database logs for specific errors

#### Server Issues

- **Check Port**: Ensure the port is not in use
- **Check Permissions**: Ensure the user has proper permissions
- **Check Disk Space**: Ensure there is enough disk space
- **Check Logs**: Check the server logs for specific errors

### Logging

Logs are written to the console by default. To save logs to a file, redirect the output:

```
python server.py > zoo_assistant.log 2>&1
```

### Debugging

To enable debug mode, set the `DEBUG` environment variable to `True`:

```
DEBUG=True python server.py
```

## Advanced Usage

### Custom Entity Extraction

You can customize entity extraction by modifying the entity configuration:

1. Use the API to get current configurations:
   ```
   GET /api/entities/config
   ```

2. Update a configuration:
   ```
   POST /api/entities/config
   {
     "entity_type": "animal_species",
     "is_active": true,
     "priority": 1
   }
   ```

### Adding Custom Rules

To add custom extraction rules, modify the `entity_extraction.py` file:

1. Add new dictionaries for your entities:
   ```python
   self.custom_entities = [
       'entity1', 'entity2', 'entity3'
   ]
   ```

2. Create Yargy rules for your entities:
   ```python
   CUSTOM_WORDS = morph_pipeline(self.custom_entities)
   self.custom_parser = Parser(CUSTOM_WORDS)
   ```

3. Add extraction logic in the `_extract_custom_entities` method:
   ```python
   custom_entities = self._extract_with_parser(text, self.custom_parser, 'custom')
   entities.extend(custom_entities)
   ```

### Using Different ASR Models

To use a different Vosk model:

1. Download the model from [Vosk Models](https://alphacephei.com/vosk/models)
2. Extract it to the `core_engine/asr/models` directory
3. Update the `MODEL_DIR` environment variable or modify the `speech_recognition.py` file

### Database Migration

To migrate from SQLite to PostgreSQL:

1. Export data from SQLite:
   ```
   sqlite3 zoo_assistant.db .dump > dump.sql
   ```

2. Modify the dump file to be compatible with PostgreSQL

3. Import data to PostgreSQL:
   ```
   psql -U postgres -d zoo_assistant -f dump.sql
   ```

4. Update the `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/zoo_assistant
   ```

### API Integration

To integrate Zoo Assistant with other systems:

1. Use the API endpoints to send and receive data
2. Implement authentication if needed
3. Use webhooks for event-driven integration
4. Consider using message queues for asynchronous processing