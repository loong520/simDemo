#!/bin/bash

# Batch Simulation Runner Script
# Project: {{ project_name }}
# Runs ocean simulation
# Generated automatically by simDemo

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_info "Starting batch simulation for project: {{ project_name }}"

# Run Ocean simulation
OCEAN_RUNNER="run_{{ project_name }}_ocean.sh"

if [ -f "$OCEAN_RUNNER" ]; then
    print_info "Running Ocean simulation..."
    if bash "$OCEAN_RUNNER"; then
        print_info "Ocean simulation completed successfully"
    else
        print_error "Ocean simulation failed"
        exit 1
    fi
else
    print_error "Ocean runner script not found: $OCEAN_RUNNER"
    exit 1
fi

print_info "Batch simulation completed successfully!"