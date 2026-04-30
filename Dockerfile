# ZAHEL - Build Android APK with Docker

FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-dev \
    openjdk-17-jdk \
    unzip \
    zlib1g-dev \
    libncurses5 \
    libstdc++6 \
    libffi-dev \
    libssl-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Buildozer
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install buildozer

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build APK
RUN buildozer android debug

# The APK will be in bin/ directory