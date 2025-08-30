#!/usr/bin/env python3
"""
Demo script for Zoo Assistant
"""
import os
import sys
import argparse
import logging
import time
import json
from pprint import pprint
import subprocess
import webbrowser
import threading
import http.server
import socketserver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEMO_PORT = 8080
DEMO_HOST = "localhost"
API_PORT = 8000
API_HOST = "localhost"

def start_server():
    """Start the Zoo Assistant server."""
    logger.info("Starting Zoo Assistant server...")
    
    # Start the server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(3)
    
    # Check if the server is running
    try:
        import requests
        response = requests.get(f"http://{API_HOST}:{API_PORT}")
        if response.status_code == 200:
            logger.info("Server started successfully")
            return server_process
        else:
            logger.error(f"Server returned status code {response.status_code}")
            server_process.terminate()
            return None
    except Exception as e:
        logger.error(f"Error checking server status: {str(e)}")
        server_process.terminate()
        return None

def process_audio(audio_file):
    """Process an audio file and return the results."""
    logger.info(f"Processing audio file: {audio_file}")
    
    try:
        import requests
        
        # Check if file exists
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None
        
        # Upload file
        with open(audio_file, 'rb') as f:
            files = {'file': (os.path.basename(audio_file), f, 'audio/mpeg')}
            response = requests.post(f"http://{API_HOST}:{API_PORT}/api/audio/process", files=files)
        
        response.raise_for_status()
        
        result = response.json()
        job_id = result.get('id')
        
        if not job_id:
            logger.error("No job ID returned")
            return None
        
        # Poll for status
        max_attempts = 30
        interval = 2
        
        for attempt in range(max_attempts):
            logger.info(f"Checking job status (attempt {attempt + 1}/{max_attempts})...")
            
            response = requests.get(f"http://{API_HOST}:{API_PORT}/api/audio/status/{job_id}")
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status')
            
            if status == 'completed':
                logger.info("Processing completed successfully")
                return result
            elif status == 'failed':
                logger.error(f"Processing failed: {result.get('error')}")
                return None
            
            time.sleep(interval)
        
        logger.error("Processing timed out")
        return None
    
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return None

def create_demo_report(results, output_dir):
    """Create a demo report from processing results."""
    logger.info("Creating demo report...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create HTML report
    html_file = os.path.join(output_dir, "report.html")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zoo Assistant Demo Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #2e7d32;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-right: 20px;
            display: flex;
            align-items: center;
        }
        .logo i {
            margin-right: 10px;
            color: #2e7d32;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        .transcription {
            white-space: pre-wrap;
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #2e7d32;
        }
        .entity-item {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        .entity-item:last-child {
            border-bottom: none;
        }
        .entity-type {
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 5px;
        }
        .entity-value {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .entity-value span:first-child {
            font-weight: 500;
        }
        .audio-player {
            width: 100%;
            margin: 10px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #757575;
            font-size: 14px;
        }
        .metrics {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: white;
            padding: 15px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            flex: 1;
            min-width: 200px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #757575;
            font-size: 14px;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <i class="fas fa-paw"></i>
                Zoo Assistant
            </div>
            <h1>Демонстрационный отчет</h1>
        </div>
        
        <div class="section">
            <h2>Информация об обработке</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value" id="processing-time">0.00</div>
                    <div class="metric-label">Время обработки (сек)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="audio-duration">0.00</div>
                    <div class="metric-label">Длительность аудио (сек)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="rtf">0.00</div>
                    <div class="metric-label">Фактор реального времени (RTF)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="entity-count">0</div>
                    <div class="metric-label">Найдено сущностей</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Аудиозапись</h2>
            <audio controls class="audio-player" id="audio-player">
                <source src="" type="audio/mpeg">
                Ваш браузер не поддерживает аудио элемент.
            </audio>
        </div>
        
        <div class="section">
            <h2>Транскрипция</h2>
            <div class="transcription" id="transcription">
                Загрузка транскрипции...
            </div>
        </div>
        
        <div class="section">
            <h2>Извлеченные данные</h2>
            <div id="extracted-data">
                <div class="loading">Загрузка данных...</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Zoo Assistant Demo Report &copy; 2025</p>
        </div>
    </div>
    
    <script>
        // Load report data
        const reportData = REPORT_DATA_PLACEHOLDER;
        
        // Update metrics
        document.getElementById('processing-time').textContent = reportData.processing_time.toFixed(2);
        document.getElementById('audio-duration').textContent = reportData.audio_duration.toFixed(2);
        document.getElementById('rtf').textContent = (reportData.processing_time / reportData.audio_duration).toFixed(2);
        document.getElementById('entity-count').textContent = reportData.entities ? reportData.entities.length : 0;
        
        // Update transcription
        document.getElementById('transcription').textContent = reportData.transcription || 'Транскрипция не найдена';
        
        // Update audio player
        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = reportData.audio_file || '';
        
        // Update extracted data
        const extractedDataElement = document.getElementById('extracted-data');
        const structuredData = reportData.structured_data;
        
        if (structuredData) {
            let html = '';
            
            // Animal info
            if (structuredData.name || structuredData.species) {
                html += `<div class="entity-item">
                    <div class="entity-type">Животное</div>
                    <div class="entity-value">
                        <span>Имя</span>
                        <span>${structuredData.name || 'Неизвестно'}</span>
                    </div>
                    <div class="entity-value">
                        <span>Вид</span>
                        <span>${structuredData.species || 'Неизвестно'}</span>
                    </div>
                </div>`;
            }
            
            // Measurements
            const measurements = structuredData.measurements || {};
            if (measurements.weight || measurements.length || measurements.temperature) {
                html += `<div class="entity-item">
                    <div class="entity-type">Измерения</div>`;
                
                if (measurements.weight) {
                    html += `<div class="entity-value">
                        <span>Вес</span>
                        <span>${measurements.weight} кг</span>
                    </div>`;
                }
                
                if (measurements.length) {
                    html += `<div class="entity-value">
                        <span>Длина</span>
                        <span>${measurements.length} м</span>
                    </div>`;
                }
                
                if (measurements.temperature) {
                    html += `<div class="entity-value">
                        <span>Температура тела</span>
                        <span>${measurements.temperature} °C</span>
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            // Behavior and health
            if (structuredData.behavior || structuredData.health_status) {
                html += `<div class="entity-item">
                    <div class="entity-type">Состояние</div>`;
                
                if (structuredData.behavior) {
                    html += `<div class="entity-value">
                        <span>Поведение</span>
                        <span>${structuredData.behavior}</span>
                    </div>`;
                }
                
                if (structuredData.health_status) {
                    html += `<div class="entity-value">
                        <span>Здоровье</span>
                        <span>${structuredData.health_status}</span>
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            // Feeding
            const feeding = structuredData.feeding || {};
            if (feeding.food_type || feeding.quantity) {
                html += `<div class="entity-item">
                    <div class="entity-type">Кормление</div>`;
                
                if (feeding.food_type) {
                    html += `<div class="entity-value">
                        <span>Тип пищи</span>
                        <span>${feeding.food_type}</span>
                    </div>`;
                }
                
                if (feeding.quantity) {
                    html += `<div class="entity-value">
                        <span>Количество</span>
                        <span>${feeding.quantity} кг</span>
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            // Environment
            const environment = structuredData.environment || {};
            if (environment.temperature || environment.humidity) {
                html += `<div class="entity-item">
                    <div class="entity-type">Окружающая среда</div>`;
                
                if (environment.temperature) {
                    html += `<div class="entity-value">
                        <span>Температура</span>
                        <span>${environment.temperature} °C</span>
                    </div>`;
                }
                
                if (environment.humidity) {
                    html += `<div class="entity-value">
                        <span>Влажность</span>
                        <span>${environment.humidity}%</span>
                    </div>`;
                }
                
                html += `</div>`;
            }
            
            if (html === '') {
                html = '<div class="loading">Структурированные данные не найдены</div>';
            }
            
            extractedDataElement.innerHTML = html;
        } else {
            extractedDataElement.innerHTML = '<div class="loading">Структурированные данные не найдены</div>';
        }
    </script>
</body>
</html>
""".replace("REPORT_DATA_PLACEHOLDER", json.dumps(results)))
    
    # Create JSON report
    json_file = os.path.join(output_dir, "report.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Report created at {html_file}")
    return html_file

def start_demo_server(html_file):
    """Start a simple HTTP server to serve the demo report."""
    logger.info(f"Starting demo server on http://{DEMO_HOST}:{DEMO_PORT}")
    
    # Get the directory containing the HTML file
    directory = os.path.dirname(os.path.abspath(html_file))
    
    # Change to that directory
    os.chdir(directory)
    
    # Create a simple HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((DEMO_HOST, DEMO_PORT), handler)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Demo Zoo Assistant')
    parser.add_argument('--audio', required=True, help='Audio file to process')
    parser.add_argument('--output-dir', default='demo_output', help='Output directory for demo files')
    parser.add_argument('--no-server', action='store_true', help='Do not start the Zoo Assistant server')
    parser.add_argument('--no-browser', action='store_true', help='Do not open the browser')
    
    args = parser.parse_args()
    
    # Start the server if needed
    server_process = None
    if not args.no_server:
        server_process = start_server()
        if not server_process:
            logger.error("Failed to start server")
            sys.exit(1)
    
    try:
        # Process the audio file
        results = process_audio(args.audio)
        if not results:
            logger.error("Failed to process audio")
            sys.exit(1)
        
        # Add audio file path to results
        results['audio_file'] = os.path.basename(args.audio)
        
        # Create demo report
        html_file = create_demo_report(results, args.output_dir)
        
        # Start demo server
        demo_server = start_demo_server(html_file)
        
        # Open browser
        if not args.no_browser:
            url = f"http://{DEMO_HOST}:{DEMO_PORT}/{os.path.basename(html_file)}"
            logger.info(f"Opening browser at {url}")
            webbrowser.open(url)
        
        # Keep the script running
        logger.info("Press Ctrl+C to exit")
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Exiting...")
    
    finally:
        # Stop the server if we started it
        if server_process:
            logger.info("Stopping server...")
            server_process.terminate()

if __name__ == '__main__':
    main()