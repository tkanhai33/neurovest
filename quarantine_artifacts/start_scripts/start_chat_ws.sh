#!/bin/bash

echo "======================================"
echo "🧠 NEURO WEBSOCKET CHAT"
echo "Type Ctrl+C to exit"
echo "======================================"

while true; do
    read -p "Neuro > " input
    python3 backend/app/llm_bridge/ws/client.py "$input"
done
