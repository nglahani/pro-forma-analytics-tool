#!/bin/bash
# Unix shell script for Linux compatibility validation  
# Usage: ./scripts/validate-linux.sh

echo "🐧 Starting Linux compatibility validation..."
echo

# Build the test container
echo "📦 Building Linux test container..."
docker build -f Dockerfile.test -t proforma-linux-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo
echo "✅ Linux test container built successfully!"
echo
echo "🎯 All validation steps completed during build process."
echo "   Your code is ready for Linux deployment!"
echo