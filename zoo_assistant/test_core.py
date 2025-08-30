#!/usr/bin/env python3
"""
Test script for core functionality
"""
import os
import sys
import argparse
import logging
import time
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_asr(audio_file):
    """Test the ASR (Automatic Speech Recognition) component."""
    logger.info(f"Testing ASR with audio file: {audio_file}")
    
    try:
        from core_engine.asr.speech_recognition import get_recognizer
        
        # Get the recognizer
        recognizer = get_recognizer()
        
        # Process the audio file
        start_time = time.time()
        result = recognizer.process_audio(audio_file)
        end_time = time.time()
        
        # Print results
        logger.info(f"ASR completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Audio duration: {result.audio_duration:.2f} seconds")
        logger.info(f"Processing time: {result.processing_time:.2f} seconds")
        logger.info(f"Real-time factor: {result.processing_time / result.audio_duration:.2f}x")
        logger.info(f"Transcription: {result.text}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing ASR: {str(e)}")
        return None

def test_ner(text):
    """Test the NER (Named Entity Recognition) component."""
    logger.info(f"Testing NER with text: {text[:100]}...")
    
    try:
        from core_engine.ner.entity_extraction import get_extractor
        
        # Get the extractor
        extractor = get_extractor()
        
        # Extract entities
        start_time = time.time()
        entities = extractor.extract_entities(text)
        end_time = time.time()
        
        # Print results
        logger.info(f"NER completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Found {len(entities)} entities")
        
        for entity in entities:
            logger.info(f"Entity: {entity.text} ({entity.type})")
        
        # Extract structured data
        start_time = time.time()
        structured_data = extractor.extract_animal_info(text)
        end_time = time.time()
        
        logger.info(f"Structured data extraction completed in {end_time - start_time:.2f} seconds")
        logger.info("Structured data:")
        pprint(structured_data)
        
        return structured_data
    
    except Exception as e:
        logger.error(f"Error testing NER: {str(e)}")
        return None

def test_pipeline(audio_file):
    """Test the complete processing pipeline."""
    logger.info(f"Testing complete pipeline with audio file: {audio_file}")
    
    try:
        from core_engine.processing_pipeline import get_pipeline
        
        # Get the pipeline
        pipeline = get_pipeline()
        
        # Process the audio file
        start_time = time.time()
        result = pipeline.process_audio(audio_file)
        end_time = time.time()
        
        # Print results
        logger.info(f"Pipeline completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Audio duration: {result.audio_duration:.2f} seconds")
        logger.info(f"Processing time: {result.processing_time:.2f} seconds")
        logger.info(f"Real-time factor: {result.processing_time / result.audio_duration:.2f}x")
        logger.info(f"Transcription: {result.transcription}")
        logger.info(f"Found {len(result.entities)} entities")
        logger.info("Structured data:")
        pprint(result.structured_data)
        logger.info("Database records:")
        pprint(result.db_records)
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing pipeline: {str(e)}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Test Zoo Assistant core functionality')
    parser.add_argument('--audio', help='Path to audio file for testing')
    parser.add_argument('--text', help='Text for NER testing')
    parser.add_argument('--component', choices=['asr', 'ner', 'pipeline'], default='pipeline',
                        help='Component to test (default: pipeline)')
    
    args = parser.parse_args()
    
    if args.component == 'asr':
        if not args.audio:
            logger.error("Audio file is required for ASR testing")
            sys.exit(1)
        test_asr(args.audio)
    
    elif args.component == 'ner':
        if not args.text:
            logger.error("Text is required for NER testing")
            sys.exit(1)
        test_ner(args.text)
    
    elif args.component == 'pipeline':
        if not args.audio:
            logger.error("Audio file is required for pipeline testing")
            sys.exit(1)
        test_pipeline(args.audio)

if __name__ == '__main__':
    main()