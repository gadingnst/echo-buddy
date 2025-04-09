#!/bin/bash

SERVICE_NAME=echo-buddy
PROJECT_DIR=$(pwd)
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
EXEC_SCRIPT="$PROJECT_DIR/run.sh"

echo "📦 Setting up autorun service for $SERVICE_NAME..."

# 1. Make run.sh executable
chmod +x "$EXEC_SCRIPT"
echo "✅ run.sh made executable"

# 2. Create systemd service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Echo Buddy Voice Assistant
After=network.target

[Service]
ExecStart=$EXEC_SCRIPT
WorkingDirectory=$PROJECT_DIR
Restart=always
User=$USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created systemd service file at $SERVICE_FILE"

# 3. Reload systemd daemon and enable service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "🚀 Service $SERVICE_NAME is now running and will start on boot!"
