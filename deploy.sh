#!/bin/bash

# NewEdu API Deployment Script
# =========================
# This script automates the deployment of the NewEdu API to a production server.
# Usage: ./deploy.sh [target_server] [target_directory]

set -e  # Exit on any error

# Default values
TARGET_SERVER=${1:-"api.newedu.uz"}
TARGET_DIR=${2:-"/var/www/api.newedu.uz"}
APP_NAME="api_newedu"

# Colors for better readability
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Helper function for printing information
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if dependencies are installed
command -v rsync >/dev/null 2>&1 || error "rsync is required but not installed."
ssh -V >/dev/null 2>&1 || error "ssh is required but not installed."

info "Starting deployment to $TARGET_SERVER..."

# Check if we can connect to the server
info "Verifying SSH connection to $TARGET_SERVER..."
ssh -q -o BatchMode=yes -o ConnectTimeout=5 $TARGET_SERVER exit
if [ $? -ne 0 ]; then
    error "Cannot connect to $TARGET_SERVER. Check your SSH configuration."
fi

# Create a temporary directory for deployment files
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Create the deployment package
info "Creating deployment package..."

# Copy essential files to temporary directory
cp -r app/ main.py requirements.txt create_tables.py create_superuser.py $TMP_DIR/

# Copy .env.example, don't copy actual .env which may contain secrets
cp .env.example $TMP_DIR/

# Create version file
echo "Deployment: $(date)" > $TMP_DIR/version.txt
echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo 'No git repo')" >> $TMP_DIR/version.txt

# Sync files to server
info "Uploading files to $TARGET_SERVER:$TARGET_DIR..."
rsync -avz --exclude=".venv" --exclude=".git" --exclude="__pycache__" \
    --exclude="*.pyc" --exclude=".env" $TMP_DIR/ $TARGET_SERVER:$TARGET_DIR/

# Execute deployment commands on the server
info "Running deployment commands on server..."
ssh $TARGET_SERVER << EOF
    cd $TARGET_DIR
    
    # Ensure Python venv exists
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate venv and install dependencies
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Check if we need to restart the service
    if systemctl is-active --quiet $APP_NAME; then
        echo "Restarting $APP_NAME service..."
        sudo systemctl restart $APP_NAME
    else
        echo "$APP_NAME service is not running. Please start it manually."
    fi
    
    # Check service status
    echo "Service status:"
    sudo systemctl status $APP_NAME
EOF

info "Deployment completed successfully!"
info "Don't forget to check logs after deployment:"
info "  ssh $TARGET_SERVER 'tail -f /var/log/api_newedu.log'"

# Final instructions
echo ""
echo -e "${GREEN}=== Next Steps ===${NC}"
echo "1. If this is the first deployment, please run:"
echo "   ssh $TARGET_SERVER 'cd $TARGET_DIR && source .venv/bin/activate && python create_tables.py'"
echo "2. Create a superuser if needed:"
echo "   ssh $TARGET_SERVER 'cd $TARGET_DIR && source .venv/bin/activate && python create_superuser.py --phone="+998XXXXXXXXX" --name="Admin Name"'"
echo "3. Check the application logs:"
echo "   ssh $TARGET_SERVER 'tail -f /var/log/api_newedu.log'"
