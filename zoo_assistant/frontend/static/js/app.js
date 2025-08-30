// API URL - change this to match your backend URL
const API_URL = 'http://localhost:8000';

// DOM Elements
const navLinks = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page');
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('audio-file');
const selectFileBtn = document.getElementById('select-file-btn');
const uploadPreview = document.getElementById('upload-preview');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const audioPreview = document.getElementById('audio-preview');
const removeFileBtn = document.getElementById('remove-file-btn');
const uploadBtn = document.getElementById('upload-btn');
const processingResult = document.getElementById('processing-result');
const statusText = document.getElementById('status-text');
const processingSpinner = document.getElementById('processing-spinner');
const transcriptionText = document.getElementById('transcription-text');
const extractedData = document.getElementById('extracted-data');
const observationsList = document.getElementById('observations-list');
const animalsGrid = document.getElementById('animals-grid');
const reportDate = document.getElementById('report-date');
const reportDetails = document.getElementById('report-details');
const observationsCount = document.getElementById('observations-count');
const measurementsCount = document.getElementById('measurements-count');
const feedingsCount = document.getElementById('feedings-count');
const alertsCount = document.getElementById('alerts-count');

// Set default date to today
if (reportDate) {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    reportDate.value = `${year}-${month}-${day}`;
}

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links and pages
        navLinks.forEach(l => l.classList.remove('active'));
        pages.forEach(p => p.classList.remove('active'));
        
        // Add active class to clicked link and corresponding page
        link.classList.add('active');
        const pageId = link.getAttribute('data-page') + '-page';
        document.getElementById(pageId).classList.add('active');
        
        // Load page data
        if (pageId === 'observations-page') {
            loadObservations();
        } else if (pageId === 'animals-page') {
            loadAnimals();
        } else if (pageId === 'reports-page') {
            loadReport();
        }
    });
});

// File Upload Handling
if (selectFileBtn) {
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
}

if (fileInput) {
    fileInput.addEventListener('change', handleFileSelect);
}

if (dropArea) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
}

if (removeFileBtn) {
    removeFileBtn.addEventListener('click', removeFile);
}

if (uploadBtn) {
    uploadBtn.addEventListener('click', uploadFile);
}

if (reportDate) {
    reportDate.addEventListener('change', loadReport);
}

// Functions
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropArea.classList.add('dragover');
}

function unhighlight() {
    dropArea.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    const file = files[0];
    
    // Check if file is audio
    if (!file.type.startsWith('audio/')) {
        alert('Пожалуйста, выберите аудиофайл');
        return;
    }
    
    // Display file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    // Create audio preview
    const url = URL.createObjectURL(file);
    audioPreview.src = url;
    
    // Show upload preview
    uploadPreview.style.display = 'block';
    
    // Hide drop area
    dropArea.style.display = 'none';
    
    // Hide processing result
    processingResult.style.display = 'none';
}

function removeFile() {
    // Clear file input
    fileInput.value = '';
    
    // Hide upload preview
    uploadPreview.style.display = 'none';
    
    // Show drop area
    dropArea.style.display = 'block';
    
    // Hide processing result
    processingResult.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function uploadFile() {
    if (!fileInput.files[0]) {
        alert('Пожалуйста, выберите файл');
        return;
    }
    
    // Show processing result
    processingResult.style.display = 'block';
    statusText.textContent = 'Обработка...';
    processingSpinner.style.display = 'block';
    transcriptionText.textContent = 'Загрузка транскрипции...';
    extractedData.innerHTML = '<div class="data-loading">Извлечение данных...</div>';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        // Upload file
        const response = await fetch(`${API_URL}/api/audio/process`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки файла');
        }
        
        const data = await response.json();
        
        // Poll for processing status
        pollProcessingStatus(data.id);
        
    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = 'Ошибка обработки';
        processingSpinner.style.display = 'none';
        transcriptionText.textContent = 'Произошла ошибка при обработке файла. Пожалуйста, попробуйте снова.';
    }
}

async function pollProcessingStatus(jobId) {
    try {
        const response = await fetch(`${API_URL}/api/audio/status/${jobId}`);
        
        if (!response.ok) {
            throw new Error('Ошибка получения статуса обработки');
        }
        
        const data = await response.json();
        
        if (data.status === 'processing') {
            // Continue polling
            setTimeout(() => pollProcessingStatus(jobId), 2000);
        } else if (data.status === 'completed') {
            // Update UI with results
            statusText.textContent = 'Обработка завершена';
            processingSpinner.style.display = 'none';
            
            // Display transcription
            transcriptionText.textContent = data.transcription || 'Транскрипция не найдена';
            
            // Display extracted data
            displayExtractedData(data.structured_data);
            
            // Refresh observations list if on that page
            if (document.getElementById('observations-page').classList.contains('active')) {
                loadObservations();
            }
        } else {
            // Error
            statusText.textContent = 'Ошибка обработки';
            processingSpinner.style.display = 'none';
            transcriptionText.textContent = 'Произошла ошибка при обработке файла. Пожалуйста, попробуйте снова.';
        }
    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = 'Ошибка обработки';
        processingSpinner.style.display = 'none';
    }
}

function displayExtractedData(data) {
    if (!data) {
        extractedData.innerHTML = '<div class="data-loading">Данные не найдены</div>';
        return;
    }
    
    let html = '';
    
    // Animal info
    if (data.name || data.species) {
        html += `<div class="entity-item">
            <div class="entity-type">Животное</div>
            <div class="entity-value">
                <span>${data.name || 'Неизвестно'}</span>
                <span>${data.species || 'Неизвестно'}</span>
            </div>
        </div>`;
    }
    
    // Measurements
    const measurements = data.measurements || {};
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
    if (data.behavior || data.health_status) {
        html += `<div class="entity-item">
            <div class="entity-type">Состояние</div>`;
        
        if (data.behavior) {
            html += `<div class="entity-value">
                <span>Поведение</span>
                <span>${data.behavior}</span>
            </div>`;
        }
        
        if (data.health_status) {
            html += `<div class="entity-value">
                <span>Здоровье</span>
                <span>${data.health_status}</span>
            </div>`;
        }
        
        html += `</div>`;
    }
    
    // Feeding
    const feeding = data.feeding || {};
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
    const environment = data.environment || {};
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
        html = '<div class="data-loading">Структурированные данные не найдены</div>';
    }
    
    extractedData.innerHTML = html;
}

async function loadObservations() {
    if (!observationsList) return;
    
    observationsList.innerHTML = '<div class="loading">Загрузка наблюдений...</div>';
    
    try {
        const response = await fetch(`${API_URL}/api/transcriptions`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки наблюдений');
        }
        
        const data = await response.json();
        
        if (data.length === 0) {
            observationsList.innerHTML = '<div class="loading">Наблюдения не найдены</div>';
            return;
        }
        
        let html = '';
        
        data.forEach(obs => {
            const date = new Date(obs.timestamp);
            const formattedDate = date.toLocaleDateString('ru-RU');
            const formattedTime = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
            
            html += `
            <div class="observation-item">
                <div class="observation-icon">
                    <i class="fas fa-clipboard-list"></i>
                </div>
                <div class="observation-content">
                    <h3>${obs.animal_name} (${obs.animal_species})</h3>
                    <p>${obs.transcription || 'Нет транскрипции'}</p>
                    <div class="observation-actions">
                        <button onclick="viewObservation(${obs.id})"><i class="fas fa-eye"></i> Просмотр</button>
                        <button onclick="playAudio('${obs.audio_file}')"><i class="fas fa-play"></i> Воспроизвести</button>
                    </div>
                </div>
                <div class="observation-meta">
                    <div class="date">${formattedDate}</div>
                    <div class="time">${formattedTime}</div>
                </div>
            </div>
            `;
        });
        
        observationsList.innerHTML = html;
        
    } catch (error) {
        console.error('Error:', error);
        observationsList.innerHTML = '<div class="loading">Ошибка загрузки наблюдений</div>';
    }
}

async function loadAnimals() {
    if (!animalsGrid) return;
    
    animalsGrid.innerHTML = '<div class="loading">Загрузка данных о животных...</div>';
    
    try {
        const response = await fetch(`${API_URL}/api/animals`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки данных о животных');
        }
        
        const data = await response.json();
        
        if (data.length === 0) {
            animalsGrid.innerHTML = '<div class="loading">Животные не найдены</div>';
            return;
        }
        
        let html = '';
        
        data.forEach(animal => {
            // Generate a placeholder image based on species
            const imageSrc = getAnimalImage(animal.species);
            
            html += `
            <div class="animal-card" onclick="viewAnimal(${animal.id})">
                <div class="animal-image" style="background-image: url('${imageSrc}')"></div>
                <div class="animal-info">
                    <h3>${animal.name}</h3>
                    <div class="species">${animal.species}</div>
                    
                    <div class="animal-stats">
                        <div class="stat-item">
                            <span class="stat-label">Возраст</span>
                            <span class="stat-value">${animal.age || 'Н/Д'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Вольер</span>
                            <span class="stat-value">${animal.enclosure || 'Н/Д'}</span>
                        </div>
                    </div>
                    
                    <div class="animal-status">
                        <div class="status-indicator">
                            <div class="dot healthy"></div>
                            <span>Здоров</span>
                        </div>
                        <button class="btn icon-btn"><i class="fas fa-chevron-right"></i></button>
                    </div>
                </div>
            </div>
            `;
        });
        
        animalsGrid.innerHTML = html;
        
    } catch (error) {
        console.error('Error:', error);
        animalsGrid.innerHTML = '<div class="loading">Ошибка загрузки данных о животных</div>';
    }
}

async function loadReport() {
    if (!reportDetails || !reportDate) return;
    
    const date = reportDate.value;
    
    reportDetails.innerHTML = '<div class="loading">Загрузка отчета...</div>';
    
    try {
        const response = await fetch(`${API_URL}/api/reports/daily?date=${date}`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки отчета');
        }
        
        const data = await response.json();
        
        // Update summary counts
        observationsCount.textContent = data.observations_count;
        measurementsCount.textContent = data.measurements_count;
        feedingsCount.textContent = data.feedings_count;
        alertsCount.textContent = '0'; // No alerts in this version
        
        let html = '';
        
        // Observations section
        html += `
        <div class="report-section">
            <h3>Наблюдения (${data.observations_count})</h3>
            ${data.observations_count > 0 ? `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>Животное</th>
                        <th>Вид</th>
                        <th>Поведение</th>
                        <th>Состояние здоровья</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.observations.map(obs => {
                        const date = new Date(obs.timestamp);
                        const formattedTime = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                        
                        return `
                        <tr>
                            <td>${formattedTime}</td>
                            <td>${obs.animal_name}</td>
                            <td>${obs.animal_species}</td>
                            <td>${obs.behavior || 'Н/Д'}</td>
                            <td>${obs.health_status || 'Н/Д'}</td>
                        </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
            ` : '<p>Нет наблюдений за выбранную дату</p>'}
        </div>
        `;
        
        // Measurements section
        html += `
        <div class="report-section">
            <h3>Измерения (${data.measurements_count})</h3>
            ${data.measurements_count > 0 ? `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>Животное</th>
                        <th>Вид</th>
                        <th>Вес (кг)</th>
                        <th>Длина (м)</th>
                        <th>Температура (°C)</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.measurements.map(m => {
                        const date = new Date(m.timestamp);
                        const formattedTime = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                        
                        return `
                        <tr>
                            <td>${formattedTime}</td>
                            <td>${m.animal_name}</td>
                            <td>${m.animal_species}</td>
                            <td>${m.weight || 'Н/Д'}</td>
                            <td>${m.length || 'Н/Д'}</td>
                            <td>${m.temperature || 'Н/Д'}</td>
                        </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
            ` : '<p>Нет измерений за выбранную дату</p>'}
        </div>
        `;
        
        // Feedings section
        html += `
        <div class="report-section">
            <h3>Кормления (${data.feedings_count})</h3>
            ${data.feedings_count > 0 ? `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>Животное</th>
                        <th>Вид</th>
                        <th>Тип пищи</th>
                        <th>Количество (кг)</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.feedings.map(f => {
                        const date = new Date(f.timestamp);
                        const formattedTime = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                        
                        return `
                        <tr>
                            <td>${formattedTime}</td>
                            <td>${f.animal_name}</td>
                            <td>${f.animal_species}</td>
                            <td>${f.food_type || 'Н/Д'}</td>
                            <td>${f.quantity || 'Н/Д'}</td>
                        </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
            ` : '<p>Нет кормлений за выбранную дату</p>'}
        </div>
        `;
        
        reportDetails.innerHTML = html;
        
    } catch (error) {
        console.error('Error:', error);
        reportDetails.innerHTML = '<div class="loading">Ошибка загрузки отчета</div>';
    }
}

function getAnimalImage(species) {
    // Map species to image URLs
    const speciesImages = {
        'тигр': 'https://images.unsplash.com/photo-1615963244664-5b845b2025ee',
        'тигрица': 'https://images.unsplash.com/photo-1615963244664-5b845b2025ee',
        'лев': 'https://images.unsplash.com/photo-1546182990-dffeafbe841d',
        'львица': 'https://images.unsplash.com/photo-1546182990-dffeafbe841d',
        'слон': 'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46',
        'жираф': 'https://images.unsplash.com/photo-1547721064-da6cfb341d50',
        'зебра': 'https://images.unsplash.com/photo-1526095179574-86e545346ae6',
        'обезьяна': 'https://images.unsplash.com/photo-1540573133985-87b6da6d54a9',
        'медведь': 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d',
        'волк': 'https://images.unsplash.com/photo-1564466809058-bf4114d55352',
        'питон': 'https://images.unsplash.com/photo-1531386151447-fd76ad50012f',
        'игуана': 'https://images.unsplash.com/photo-1580859297753-039d0341fa51',
        'черепаха': 'https://images.unsplash.com/photo-1558652249-3f7e0c1a3411'
    };
    
    // Convert species to lowercase for case-insensitive matching
    const lowerSpecies = species.toLowerCase();
    
    // Return matching image or default
    for (const [key, url] of Object.entries(speciesImages)) {
        if (lowerSpecies.includes(key)) {
            return url;
        }
    }
    
    // Default image if no match
    return 'https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a';
}

function viewAnimal(id) {
    // Redirect to animal details page (to be implemented)
    alert(`Просмотр животного с ID: ${id}`);
}

function viewObservation(id) {
    // Redirect to observation details page (to be implemented)
    alert(`Просмотр наблюдения с ID: ${id}`);
}

function playAudio(filename) {
    // Play audio file (to be implemented)
    alert(`Воспроизведение аудио: ${filename}`);
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data for active page
    const activePage = document.querySelector('.page.active');
    if (activePage) {
        if (activePage.id === 'observations-page') {
            loadObservations();
        } else if (activePage.id === 'animals-page') {
            loadAnimals();
        } else if (activePage.id === 'reports-page') {
            loadReport();
        }
    }
});