import os
import json
import wave
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Vosk log level to warnings only
SetLogLevel(-1)

class TranscriptionResult(BaseModel):
    text: str
    segments: List[Dict[str, Any]] = []
    processing_time: float
    audio_duration: float
    wer: Optional[float] = None

class SpeechRecognizer:
    def __init__(self, model_path: str = None):
        """Initialize the speech recognizer with the specified model."""
        if model_path is None:
            # Default to the Russian model we downloaded
            model_path = os.path.join(os.path.dirname(__file__), "models/vosk-model-ru")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")
        
        logger.info(f"Loading ASR model from {model_path}")
        self.model = Model(model_path)
        logger.info("ASR model loaded successfully")
        
        # Create a thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())
    
    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """Transcribe an audio file and return the text."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        start_time = time.time()
        
        # Open the audio file
        wf = wave.open(audio_path, "rb")
        
        # Get audio duration
        audio_duration = wf.getnframes() / wf.getframerate()
        
        # Check if the audio format is compatible
        if wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio file must be WAV format PCM")
        
        # Create recognizer
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)
        rec.SetPartialWords(True)
        
        # Process audio in chunks
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                results.append(part_result)
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        results.append(final_result)
        
        # Combine all results
        all_text = " ".join([r.get("text", "") for r in results if "text" in r and r["text"]])
        
        # Extract all segments
        all_segments = []
        for r in results:
            if "result" in r:
                all_segments.extend(r["result"])
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            text=all_text,
            segments=all_segments,
            processing_time=processing_time,
            audio_duration=audio_duration
        )
    
    def convert_to_wav(self, input_file: str, output_file: str = None) -> str:
        """Convert audio file to WAV format for processing."""
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + ".wav"
        
        # Use ffmpeg to convert the file
        import subprocess
        cmd = [
            "ffmpeg", "-y", "-i", input_file,
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            output_file
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_file
    
    def process_audio(self, audio_path: str) -> TranscriptionResult:
        """Process audio file, converting if necessary."""
        # Check if the file is already in WAV format
        if not audio_path.lower().endswith('.wav'):
            logger.info(f"Converting {audio_path} to WAV format")
            wav_path = self.convert_to_wav(audio_path)
            result = self.transcribe_file(wav_path)
            # Clean up temporary WAV file if it's different from the original
            if wav_path != audio_path:
                os.remove(wav_path)
            return result
        else:
            return self.transcribe_file(audio_path)

# Singleton instance
_recognizer = None

def get_recognizer():
    """Get or create a singleton instance of the speech recognizer."""
    global _recognizer
    if _recognizer is None:
        _recognizer = SpeechRecognizer()
    return _recognizer