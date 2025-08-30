#!/bin/bash

# Zoo Assistant Installation Script

# Exit on error
set -e

# Print colored messages
print_info() {
    echo -e "\e[1;34m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[1;32m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[1;31m[ERROR]\e[0m $1"
}

print_warning() {
    echo -e "\e[1;33m[WARNING]\e[0m $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_info "Checking Python version..."
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 --version | awk '{print $2}')
        python_major=$(echo $python_version | cut -d. -f1)
        python_minor=$(echo $python_version | cut -d. -f2)
        
        if [ "$python_major" -ge 3 ] && [ "$python_minor" -ge 8 ]; then
            print_success "Python $python_version is installed"
            return 0
        else
            print_error "Python 3.8+ is required, found $python_version"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Check if FFmpeg is installed
check_ffmpeg() {
    print_info "Checking FFmpeg..."
    if command -v ffmpeg >/dev/null 2>&1; then
        ffmpeg_version=$(ffmpeg -version | head -n1)
        print_success "FFmpeg is installed: $ffmpeg_version"
        return 0
    else
        print_error "FFmpeg is not installed"
        return 1
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements_minimal.txt
    print_success "Dependencies installed"
}

# Download Vosk model
download_vosk_model() {
    print_info "Downloading Vosk model..."
    model_dir="core_engine/asr/models/vosk-model-ru"
    
    if [ -d "$model_dir" ]; then
        print_warning "Vosk model already exists"
        return 0
    fi
    
    mkdir -p core_engine/asr/models
    cd core_engine/asr/models
    
    if command -v wget >/dev/null 2>&1; then
        wget -q https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    elif command -v curl >/dev/null 2>&1; then
        curl -s -O https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
    else
        print_error "Neither wget nor curl is installed"
        cd ../../../
        return 1
    fi
    
    if command -v unzip >/dev/null 2>&1; then
        unzip -q vosk-model-small-ru-0.22.zip
        mv vosk-model-small-ru-0.22 vosk-model-ru
        rm vosk-model-small-ru-0.22.zip
        cd ../../../
        print_success "Vosk model downloaded and extracted"
        return 0
    else
        print_error "unzip is not installed"
        cd ../../../
        return 1
    fi
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    source venv/bin/activate
    python init_db.py
    print_success "Database initialized"
}

# Create data directories
create_data_dirs() {
    print_info "Creating data directories..."
    mkdir -p data/uploads
    print_success "Data directories created"
}

# Main installation function
main() {
    print_info "Starting Zoo Assistant installation..."
    
    # Check requirements
    check_python || { print_error "Python check failed"; exit 1; }
    check_ffmpeg || { print_warning "FFmpeg not found, audio processing may not work"; }
    
    # Setup environment
    create_venv
    install_dependencies
    download_vosk_model || { print_error "Failed to download Vosk model"; exit 1; }
    create_data_dirs
    init_database
    
    print_success "Installation completed successfully!"
    print_info "To start the application, run: source venv/bin/activate && python server.py"
    print_info "Then open http://localhost:8000 in your browser"
}

# Run the installation
main