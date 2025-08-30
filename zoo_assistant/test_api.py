#!/usr/bin/env python3
"""
Test script for API functionality
"""
import os
import sys
import argparse
import logging
import requests
import json
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default API URL
DEFAULT_API_URL = 'http://localhost:8000/api'

def test_root(api_url):
    """Test the root endpoint."""
    url = api_url.rstrip('/api')
    logger.info(f"Testing root endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        return response.json()
    
    except Exception as e:
        logger.error(f"Error testing root endpoint: {str(e)}")
        return None

def test_audio_process(api_url, audio_file):
    """Test the audio processing endpoint."""
    url = f"{api_url}/audio/process"
    logger.info(f"Testing audio processing endpoint: {url}")
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None
        
        # Upload file
        with open(audio_file, 'rb') as f:
            files = {'file': (os.path.basename(audio_file), f, 'audio/mpeg')}
            response = requests.post(url, files=files)
        
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Job ID: {result.get('id')}")
        logger.info(f"Status: {result.get('status')}")
        
        # Poll for status
        job_id = result.get('id')
        if job_id:
            poll_status(api_url, job_id)
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing audio processing endpoint: {str(e)}")
        return None

def poll_status(api_url, job_id, max_attempts=30, interval=2):
    """Poll for job status."""
    url = f"{api_url}/audio/status/{job_id}"
    logger.info(f"Polling job status: {url}")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status')
            
            logger.info(f"Attempt {attempt + 1}/{max_attempts}: Status = {status}")
            
            if status == 'completed':
                logger.info("Job completed successfully")
                logger.info(f"Transcription: {result.get('transcription')}")
                logger.info(f"Processing time: {result.get('processing_time')} seconds")
                logger.info(f"Found {len(result.get('entities', []))} entities")
                logger.info("Structured data:")
                pprint(result.get('structured_data'))
                return result
            
            elif status == 'failed':
                logger.error(f"Job failed: {result.get('error')}")
                return result
            
            # Wait before next attempt
            import time
            time.sleep(interval)
        
        except Exception as e:
            logger.error(f"Error polling job status: {str(e)}")
            import time
            time.sleep(interval)
    
    logger.error(f"Max polling attempts reached, job still processing")
    return None

def test_transcriptions(api_url):
    """Test the transcriptions endpoint."""
    url = f"{api_url}/transcriptions"
    logger.info(f"Testing transcriptions endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Found {len(result)} transcriptions")
        
        if result:
            logger.info("First transcription:")
            pprint(result[0])
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing transcriptions endpoint: {str(e)}")
        return None

def test_animals(api_url):
    """Test the animals endpoint."""
    url = f"{api_url}/animals"
    logger.info(f"Testing animals endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Found {len(result)} animals")
        
        if result:
            logger.info("First animal:")
            pprint(result[0])
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing animals endpoint: {str(e)}")
        return None

def test_animal_details(api_url, animal_id):
    """Test the animal details endpoint."""
    url = f"{api_url}/animals/{animal_id}"
    logger.info(f"Testing animal details endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Animal details:")
        pprint(result)
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing animal details endpoint: {str(e)}")
        return None

def test_animal_log(api_url, animal_id):
    """Test the animal log endpoint."""
    url = f"{api_url}/animals/{animal_id}/log"
    logger.info(f"Testing animal log endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Found {len(result)} log entries")
        
        if result:
            logger.info("First log entry:")
            pprint(result[0])
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing animal log endpoint: {str(e)}")
        return None

def test_daily_report(api_url, date=None):
    """Test the daily report endpoint."""
    url = f"{api_url}/reports/daily"
    if date:
        url += f"?date={date}"
    
    logger.info(f"Testing daily report endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Report date: {result.get('date')}")
        logger.info(f"Observations: {result.get('observations_count')}")
        logger.info(f"Measurements: {result.get('measurements_count')}")
        logger.info(f"Feedings: {result.get('feedings_count')}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing daily report endpoint: {str(e)}")
        return None

def test_entity_configs(api_url):
    """Test the entity configs endpoint."""
    url = f"{api_url}/entities/config"
    logger.info(f"Testing entity configs endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info(f"Status code: {response.status_code}")
        result = response.json()
        logger.info(f"Found {len(result)} entity configs")
        
        if result:
            logger.info("Entity configs:")
            pprint(result)
        
        return result
    
    except Exception as e:
        logger.error(f"Error testing entity configs endpoint: {str(e)}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Test Zoo Assistant API functionality')
    parser.add_argument('--api-url', default=DEFAULT_API_URL, help='API URL')
    parser.add_argument('--audio', help='Path to audio file for testing')
    parser.add_argument('--animal-id', type=int, help='Animal ID for testing')
    parser.add_argument('--date', help='Date for daily report (YYYY-MM-DD)')
    parser.add_argument('--endpoint', choices=['root', 'audio', 'transcriptions', 'animals', 
                                              'animal-details', 'animal-log', 'daily-report', 
                                              'entity-configs', 'all'], 
                        default='all', help='Endpoint to test (default: all)')
    
    args = parser.parse_args()
    
    # Normalize API URL
    api_url = args.api_url.rstrip('/')
    if not api_url.endswith('/api'):
        api_url += '/api'
    
    if args.endpoint == 'root' or args.endpoint == 'all':
        test_root(api_url)
    
    if args.endpoint == 'audio':
        if not args.audio:
            logger.error("Audio file is required for audio endpoint testing")
            sys.exit(1)
        test_audio_process(api_url, args.audio)
    
    if args.endpoint == 'transcriptions' or args.endpoint == 'all':
        test_transcriptions(api_url)
    
    if args.endpoint == 'animals' or args.endpoint == 'all':
        test_animals(api_url)
    
    if args.endpoint == 'animal-details':
        if not args.animal_id:
            logger.error("Animal ID is required for animal details endpoint testing")
            sys.exit(1)
        test_animal_details(api_url, args.animal_id)
    
    if args.endpoint == 'animal-log':
        if not args.animal_id:
            logger.error("Animal ID is required for animal log endpoint testing")
            sys.exit(1)
        test_animal_log(api_url, args.animal_id)
    
    if args.endpoint == 'daily-report' or args.endpoint == 'all':
        test_daily_report(api_url, args.date)
    
    if args.endpoint == 'entity-configs' or args.endpoint == 'all':
        test_entity_configs(api_url)

if __name__ == '__main__':
    main()