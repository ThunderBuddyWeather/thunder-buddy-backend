# Use the official Python 3.12 slim image as the base.
# The slim version reduces the overall image size.
FROM python:3.12-slim

# Install curl, wget, and PostgreSQL client tools for database initialization
# Also install net-tools for network debugging (netstat) and procps for process inspection (ps)
RUN apt-get update && apt-get install -y \
  curl \
  wget \
  postgresql-client \
  net-tools \
  procps \
  iproute2 \
  jq \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
# All subsequent commands run within this directory.
WORKDIR /app

# Copy the requirements file into the container.
# This file lists all the Python dependencies your app requires.
COPY requirements.txt .

# Copy the .env.ci file as .env
COPY .env.ci .env.ci

# Install Python dependencies specified in requirements.txt.
# The --no-cache-dir flag prevents pip from caching package downloads,
# which helps reduce the final image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY scripts/ scripts/

# Copy the static directory
COPY static/ static/

# Copy the startup script into the container
COPY scripts/startup.sh .

# Copy the init_db_user script into the container
COPY scripts/init_db_user.py .

# Make the startup script executable
RUN chmod +x scripts/startup.sh

# Expose port 5000 so that the container listens on this port at runtime.
EXPOSE 5000

# Environment variables
ENV DB_HOST=db \
  DB_PORT=5432 \
  DB_NAME=thunderbuddy \
  DB_USER=thunderbuddy \
  DB_PASSWORD=localdev \
  DB_ADMIN_USER=postgres \
  DB_ADMIN_PASSWORD=postgres \
  DATABASE_URL=postgresql://thunderbuddy:localdev@db:5432/thunderbuddy

# Set the container's entrypoint to run our startup script.
ENTRYPOINT ["scripts/startup.sh"]

# Define default arguments to the ENTRYPOINT via CMD.
# Using an empty array (CMD []) here is a best practice, as it allows you
# to override or add additional arguments at runtime without changing the ENTRYPOINT.
CMD []
