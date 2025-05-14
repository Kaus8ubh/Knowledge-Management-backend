# Use lightweight Python image
FROM python:3.11-slim

# Install wkhtmltopdf, system libraries, and necessary dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libjpeg62-turbo \
    libfreetype6 \
    build-essential \
    libssl-dev \
    libmagic1 \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose port for Uvicorn
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
