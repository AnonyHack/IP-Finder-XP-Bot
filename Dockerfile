# Use Python 3.10 (can change to 3.11 if you prefer)
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to ensure output is not buffered
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
