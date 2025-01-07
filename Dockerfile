# Start with a Python image
FROM python:3.8-slim

# Install dependencies needed for Firefox and Geckodriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    unzip \
    libx11-dev \
    libx11-6 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libdbus-1-3 \
    libxt6 \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox
RUN wget https://github.com/mozilla/firefox/releases/download/112.0/firefox-112.0.tar.bz2 -O firefox.tar.bz2 && \
    tar xjf firefox.tar.bz2 && \
    mv firefox /opt/firefox

# Install Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz -O geckodriver.tar.gz && \
    tar -xvzf geckodriver.tar.gz && \
    mv geckodriver /usr/local/bin/

# Set environment variables to help find Firefox and Geckodriver
ENV PATH=/opt/firefox:$PATH
ENV GECKODRIVER_PATH=/usr/local/bin/geckodriver
ENV MOZ_HEADLESS=1

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application files into the container
COPY . .

# Command to run your Python script
CMD ["python", "app.py"]
