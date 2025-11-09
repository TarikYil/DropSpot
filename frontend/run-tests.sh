#!/bin/bash
# Frontend test runner script

echo "Frontend Test Runner"
echo "===================="
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run tests
echo "Running tests..."
npm test -- --run

