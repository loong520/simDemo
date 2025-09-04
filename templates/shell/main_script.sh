#!/bin/bash

# EDA Simulation Runner Script
# Project: {{ project_name }}
# Simulator: {{ simulator }}
# Generated automatically by simDemo

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ====================================================================
# EDA Tool Environment Setup for {{ simulator|upper }}
# ====================================================================

print_info "Setting up EDA tool environment..."

{% if source_commands %}
# Source environment setup scripts
{% for source_cmd in source_commands %}
{{ source_cmd }}
{% endfor %}

{% endif %}
{% if export_commands %}
# Export EDA tool environment variables
{% for export_cmd in export_commands %}
{{ export_cmd }}
{% endfor %}

{% endif %}
# ====================================================================
# Working Directory Setup
# ====================================================================

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_info "Script directory: $SCRIPT_DIR"

# Set working directory
cd "$SCRIPT_DIR"
print_info "Working directory: $(pwd)"

# Create necessary directories
mkdir -p {{ results_dir }}
mkdir -p logs
mkdir -p temp

# ====================================================================
# {{ script_type|upper }} Simulation Execution
# ====================================================================

print_info "Starting {{ script_type }} simulation..."
START_TIME=$(date +%s)

{% if script_type == "ocean" %}
# Ocean script execution
OCEAN_SCRIPT="{{ target_script_path }}"

if [ ! -f "$OCEAN_SCRIPT" ]; then
    print_error "Ocean script not found: $OCEAN_SCRIPT"
    exit 1
fi

print_info "Ocean script: $OCEAN_SCRIPT"

# Execute ocean simulation
print_info "Executing: {{ ocean_cmd }} {{ launch_args }} $OCEAN_SCRIPT"

# Redirect output to log file
LOG_FILE="logs/{{ project_name }}_ocean_$(date +%Y%m%d_%H%M%S).log"
print_info "Log file: $LOG_FILE"

# Run simulation
if {{ ocean_cmd }} {{ launch_args }} "$OCEAN_SCRIPT" 2>&1 | tee "$LOG_FILE"; then
    SIMULATION_EXIT_CODE=${PIPESTATUS[0]}
else
    SIMULATION_EXIT_CODE=$?
fi
{% endif %}

# ====================================================================
# Results and Cleanup
# ====================================================================

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_info "Simulation completed in ${DURATION} seconds"

# Check simulation results
if [ $SIMULATION_EXIT_CODE -eq 0 ]; then
    print_info "Simulation completed successfully!"
    print_info "Results directory: {{ results_dir }}"
    
    # List result files
    if [ -d "{{ results_dir }}" ]; then
        RESULT_COUNT=$(find {{ results_dir }} -type f | wc -l)
        print_info "Found $RESULT_COUNT result files"
    fi
    
    exit 0
else
    print_error "Simulation failed with exit code: $SIMULATION_EXIT_CODE"
    print_error "Check log file for details: $LOG_FILE"
    exit $SIMULATION_EXIT_CODE
fi