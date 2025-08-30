#!/usr/bin/env python3
"""
Zoo Assistant - Main entry point
"""
import os
import argparse
import logging
import sys
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        # Check if ffmpeg is installed
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("FFmpeg is installed")
    except FileNotFoundError:
        logger.error("FFmpeg is not installed. Please install it before running the application.")
        return False
    
    # Check if Vosk model exists
    model_path = os.path.join('core_engine', 'asr', 'models', 'vosk-model-ru')
    if not os.path.exists(model_path):
        logger.error(f"Vosk model not found at {model_path}. Please download it first.")
        return False
    
    return True

def init_database():
    """Initialize the database."""
    logger.info("Initializing database...")
    try:
        subprocess.run([sys.executable, 'init_db.py'], check=True)
        logger.info("Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def run_server(host='0.0.0.0', port=8000, debug=False):
    """Run the server."""
    logger.info(f"Starting server on {host}:{port}")
    
    # Create data directories if they don't exist
    os.makedirs(os.path.join('data', 'uploads'), exist_ok=True)
    
    # Run the server
    cmd = [sys.executable, 'server.py']
    if debug:
        cmd.append('--debug')
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Server stopped")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Zoo Assistant - AI-powered assistant for zookeepers')
    parser.add_argument('--init-db', action='store_true', help='Initialize the database')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database if requested
    if args.init_db:
        if not init_database():
            sys.exit(1)
    
    # Run the server
    run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()