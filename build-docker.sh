#!/bin/bash
# Build ZAHEL APK with Docker

echo "🚀 Building ZAHEL APK with Docker..."

# Build Docker image
docker build -t zahel-builder .

# Run build
docker run --rm -v $(pwd)/bin:/app/bin zahel-builder

echo "✅ Build complete! Check bin/ directory for APK"