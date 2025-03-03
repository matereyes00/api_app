# Use an official Python runtime as a base image
FROM python:3.11


# Set the working directory in the container
WORKDIR /app

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd

RUN apt-get update && apt-get install -y postgresql-client

# Copy only the required files first (to leverage Docker cache)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install -r requirements.txt


# Copy the rest of the project
COPY . .

# Ensure scripts are executable
RUN chmod +x ./entrypoint.sh

# Expose the port Django runs on
EXPOSE 8000

# Default command
ENTRYPOINT ["./entrypoint.sh"]
