#IF RUNNING ON LINUX/MAC-BASED SYSTEMS, START HOSTING FROM THIS FILE! SIMPLY RUN THIS FILE FROM THE TERMINAL!
#THIS CAN BE RUN BY COPY AND PASTING THIS INTO THE TERMINAL: 
#chmod +x start.sh && ./start.sh
#!/usr/bin/env bash
set -euo pipefail
docker compose up -d --build
# Get the mapped host:port for container port 8000
ADDR=$(docker compose port app 8000)
# Normalize 0.0.0.0 -> 127.0.0.1 for clarity
URL="http://${ADDR/0.0.0.0/127.0.0.1}"
echo "App is starting… $URL"