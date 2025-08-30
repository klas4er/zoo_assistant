#!/bin/bash

# Zoo Assistant Packaging Script

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

# Check if version is provided
if [ -z "$1" ]; then
    print_error "Version number is required. Usage: ./package.sh <version>"
    exit 1
fi

VERSION=$1
PACKAGE_NAME="zoo_assistant-${VERSION}"
DIST_DIR="dist"

# Create distribution directory
print_info "Creating distribution package for Zoo Assistant v${VERSION}..."
mkdir -p ${DIST_DIR}

# Create package directory
mkdir -p ${DIST_DIR}/${PACKAGE_NAME}

# Copy files
print_info "Copying files..."
cp -r backend core_engine frontend docs data ${DIST_DIR}/${PACKAGE_NAME}/
cp server.py init_db.py run.py test_core.py test_api.py README.md requirements_minimal.txt .env Dockerfile docker-compose.yml install.sh ${DIST_DIR}/${PACKAGE_NAME}/

# Create version file
echo "${VERSION}" > ${DIST_DIR}/${PACKAGE_NAME}/VERSION

# Remove any existing model files (they're large and can be downloaded during installation)
print_info "Removing model files to reduce package size..."
rm -rf ${DIST_DIR}/${PACKAGE_NAME}/core_engine/asr/models/*

# Remove any database files
print_info "Removing database files..."
rm -f ${DIST_DIR}/${PACKAGE_NAME}/*.db

# Remove any __pycache__ directories
print_info "Removing __pycache__ directories..."
find ${DIST_DIR}/${PACKAGE_NAME} -name "__pycache__" -type d -exec rm -rf {} +

# Create zip archive
print_info "Creating zip archive..."
cd ${DIST_DIR}
zip -r ${PACKAGE_NAME}.zip ${PACKAGE_NAME}
cd ..

# Create tar.gz archive
print_info "Creating tar.gz archive..."
cd ${DIST_DIR}
tar -czf ${PACKAGE_NAME}.tar.gz ${PACKAGE_NAME}
cd ..

# Calculate checksums
print_info "Calculating checksums..."
cd ${DIST_DIR}
sha256sum ${PACKAGE_NAME}.zip ${PACKAGE_NAME}.tar.gz > ${PACKAGE_NAME}.sha256
cd ..

print_success "Package created successfully!"
print_info "Package files:"
print_info "- ${DIST_DIR}/${PACKAGE_NAME}.zip"
print_info "- ${DIST_DIR}/${PACKAGE_NAME}.tar.gz"
print_info "- ${DIST_DIR}/${PACKAGE_NAME}.sha256"