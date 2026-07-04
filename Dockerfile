# Use the official Microsoft Playwright Python base image (includes Chromium and all OS dependencies)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set workspace directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create the screenshots directory
RUN mkdir -p static/screenshots

# Expose server port
EXPOSE 5000

# Set production environment variables
ENV PORT=5000
ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Start server using waitress
CMD ["python", "app.py"]
