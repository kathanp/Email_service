#!/bin/bash

# Kill Ports Script for Email Bot Development
# Usage: ./kill-ports.sh [port_number] or ./kill-ports.sh all

echo "🔧 Email Bot Port Management"
echo "================================"

kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🔴 Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null
        echo "✅ Port $port is now free"
    else
        echo "✅ Port $port is already free"
    fi
}

case "$1" in
    "3000")
        kill_port 3000
        ;;
    "8000")
        kill_port 8000
        ;;
    "all"|"")
        echo "🧹 Cleaning all development ports..."
        kill_port 3000
        kill_port 8000
        echo "🎉 All ports cleaned!"
        ;;
    *)
        if [[ "$1" =~ ^[0-9]+$ ]]; then
            kill_port $1
        else
            echo "❌ Invalid port number: $1"
            echo "Usage: $0 [3000|8000|all|port_number]"
            echo "Examples:"
            echo "  $0          # Kill ports 3000 and 8000"
            echo "  $0 all      # Kill ports 3000 and 8000"
            echo "  $0 3000     # Kill only port 3000"
            echo "  $0 8000     # Kill only port 8000"
            echo "  $0 9000     # Kill custom port 9000"
            exit 1
        fi
        ;;
esac

echo "================================"
echo "✨ Port cleanup complete!" 