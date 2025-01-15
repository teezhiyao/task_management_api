# Use the official Python image
FROM python:3.12-slim

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Copy the wait-for-db.sh script
COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# Start the FastAPI application
CMD ["/app/wait-for-db.sh", "db", "3306", "uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
