#!/bin/bash

# Netlist Generation Script
# Project: {{ project_name }}
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
# EDA Tool Environment Setup
# ====================================================================

print_info "Setting up EDA tool environment..."

# Source environment setup scripts if provided
{% if source_commands %}
{% for source_cmd in source_commands %}
{{ source_cmd }}
{% endfor %}
{% endif %}

# Export EDA tool environment variables
{% if export_commands %}
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

# ====================================================================
# Netlist Generation Execution
# ====================================================================

print_info "Starting netlist generation..."
START_TIME=$(date +%s)

# Netlist script execution
NETLIST_SCRIPT="{{ netlist_script_path }}"

if [ ! -f "$NETLIST_SCRIPT" ]; then
    print_error "Netlist script not found: $NETLIST_SCRIPT"
    exit 1
fi

print_info "Netlist script: $NETLIST_SCRIPT"

# Execute netlist generation
print_info "Executing: {{ ocean_cmd }} {{ launch_args }} $NETLIST_SCRIPT"

# Redirect output to log file
LOG_FILE="logs/{{ project_name }}_netlist_$(date +%Y%m%d_%H%M%S).log"
print_info "Log file: $LOG_FILE"

# Run netlist generation
if {{ ocean_cmd }} {{ launch_args }} "$NETLIST_SCRIPT" 2>&1 | tee "$LOG_FILE"; then
    SIMULATION_EXIT_CODE=${PIPESTATUS[0]}
else
    SIMULATION_EXIT_CODE=$?
fi

# ====================================================================
# Results and Cleanup
# ====================================================================

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_info "Netlist generation completed in ${DURATION} seconds"

# Check netlist generation results
if [ $SIMULATION_EXIT_CODE -eq 0 ]; then
    print_info "Netlist generation completed successfully!"
    
    # List generated netlist files
    if [ -d "{{ design_path_dir }}" ]; then
        NETLIST_COUNT=$(find {{ design_path_dir }} -name "*.scs" -o -name "*.netlist" | wc -l)
        print_info "Found $NETLIST_COUNT netlist files in {{ design_path_dir }}"
    fi
    
    exit 0
else
    print_error "Netlist generation failed with exit code: $SIMULATION_EXIT_CODE"
    print_error "Check log file for details: $LOG_FILE"
    exit $SIMULATION_EXIT_CODE
fi