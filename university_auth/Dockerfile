FROM python:3.12.6-bookworm


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory inside container
WORKDIR /app

# Copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your service code
COPY auth ./auth

# Set working directory to your app folder
WORKDIR /app/auth

# Run your FastStream service
CMD ["python", "app.py"]
