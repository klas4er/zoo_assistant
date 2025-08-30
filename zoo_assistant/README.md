# Zoo Assistant - AI-powered Assistant for Zookeepers

Zoo Assistant is an intelligent system designed to help zookeepers convert voice observations into structured data. The system uses speech recognition and natural language processing to extract relevant information about animals, their behavior, health status, measurements, and feeding details.

## Features

- **Speech-to-Text**: Convert audio recordings of zookeeper observations into text
- **Entity Extraction**: Automatically extract structured data from transcriptions
- **Data Management**: Store and organize animal observations, measurements, and feeding records
- **Web Interface**: User-friendly interface for uploading audio, viewing results, and generating reports
- **API**: RESTful API for integration with other systems

## System Components

### Backend

- **API**: FastAPI-based REST API for data processing and retrieval
- **Core Engine**: Speech recognition and entity extraction components
- **Database**: SQLAlchemy ORM with SQLite database (can be configured for PostgreSQL)

### Frontend

- **Web Interface**: HTML, CSS, and JavaScript interface for zookeepers and management
- **Responsive Design**: Works on desktop and mobile devices

## Technical Details

### CPU Optimization

This system is optimized to run efficiently on CPU-only environments:

- **Vosk**: Lightweight speech recognition model for Russian language
- **Natasha**: CPU-optimized NER for Russian language
- **Multithreading**: Parallel processing for improved performance
- **Caching**: Preloaded models and cached results for faster processing

### Entity Extraction

The system can extract the following entities:

- Animal names and species
- Behavior and health status
- Physical measurements (weight, length, height)
- Body temperature
- Environmental conditions (temperature, humidity)
- Feeding details (food type, quantity)
- Dates and times

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/zoo-assistant.git
   cd zoo-assistant
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   cd zoo_assistant
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

5. Initialize the database:
   ```
   python init_db.py
   ```

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

### API Endpoints

#### Audio Processing

- `POST /api/audio/process`: Upload and process an audio file
- `GET /api/audio/status/{job_id}`: Check the status of an audio processing job

#### Data Retrieval

- `GET /api/transcriptions`: Get a list of transcriptions
- `GET /api/animals`: Get a list of all animals
- `GET /api/animals/{animal_id}`: Get details for a specific animal
- `GET /api/animals/{animal_id}/log`: Get observation log for a specific animal
- `GET /api/reports/daily`: Get a daily report of observations

#### Configuration

- `GET /api/entities/config`: Get entity extraction configurations
- `POST /api/entities/config`: Update entity extraction configuration

## Performance Metrics

- **Speech Recognition**: WER < 20% on Russian language
- **Entity Extraction**: Accuracy > 75%
- **Processing Speed**: 5-minute audio processed in < 90 seconds on CPU

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Vosk](https://alphacephei.com/vosk/) for the speech recognition model
- [Natasha](https://github.com/natasha/natasha) for the Russian NER
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework