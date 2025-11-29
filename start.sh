#!/bin/bash
# Start script for Federated NL2SQL
# This script starts both backend and frontend concurrently

echo "🚀 Starting Federated NL2SQL..."
echo ""

# Check if in correct directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting Flask backend on port 5000..."
cd "$(dirname "$0")"
if [ -d "shrm" ]; then
    source shrm/Scripts/activate 2>/dev/null || source shrm/bin/activate
fi
python backend/app.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting React frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "✨ Federated NL2SQL is running!"
echo "=========================================="
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=========================================="
echo ""

# Wait for processes
wait
